/**
 * Live Disaster / Risk Intelligence — Leaflet layer + dashboard card.
 * Additive: does not replace existing map layers or SOS/alerts.
 */
const LiveRiskIntel = {
  events: [],
  summary: null,
  layer: null,
  pollTimer: null,
  filters: { event_type: "all", risk_level: "all", source: "all" },
  available: true,
  lastError: null,

  COLORS: {
    LOW: "#10b981",
    MODERATE: "#f59e0b",
    HIGH: "#f97316",
    CRITICAL: "#ef4444",
  },

  init() {
    this.bindFilters();
    this.ensureLayerToggle();
    document.getElementById("btnRiskRefresh")?.addEventListener("click", () => this.refresh(true));
    document.getElementById("btnRiskViewMap")?.addEventListener("click", () => {
      document.querySelector(".map-wrapper-card")?.scrollIntoView({ behavior: "smooth" });
    });
    this.load();
    this.pollTimer = setInterval(() => this.load(), 5 * 60 * 1000);
    window.addEventListener("locationUpdated", () => this.updateNearbyBanner());
  },

  ensureLayerToggle() {
    const host = document.querySelector("#layersPopover .map-layer-toggles");
    if (!host || document.getElementById("toggleLiveRisk")) return;
    const label = document.createElement("label");
    label.className = "layer-switch";
    label.innerHTML = `
      <input type="checkbox" id="toggleLiveRisk" checked>
      <span class="slider round"></span>
      <span class="switch-label">Live Risk</span>
    `;
    host.appendChild(label);
    document.getElementById("toggleLiveRisk")?.addEventListener("change", (e) => {
      const map = window.getSafetyMap?.();
      if (!map || !this.layer) return;
      if (e.target.checked) map.addLayer(this.layer);
      else map.removeLayer(this.layer);
    });
  },

  bindFilters() {
    document.querySelectorAll("[data-risk-filter]").forEach((el) => {
      el.addEventListener("click", () => {
        const group = el.dataset.riskFilter;
        const value = el.dataset.value;
        this.filters[group] = value;
        document.querySelectorAll(`[data-risk-filter="${group}"]`).forEach((b) => {
          b.classList.toggle("active", b.dataset.value === value);
        });
        this.renderMap();
        this.renderList();
      });
    });
  },

  async load() {
    this.setStatus("Updating live risk…");
    try {
      const params = new URLSearchParams();
      if (this.filters.event_type !== "all") params.set("event_type", this.filters.event_type);
      if (this.filters.risk_level !== "all") params.set("risk_level", this.filters.risk_level);
      if (this.filters.source !== "all") params.set("source", this.filters.source);
      const res = await fetch(`/api/risk-events?${params.toString()}`);
      if (!res.ok) throw new Error("Risk API unavailable");
      const data = await res.json();
      this.events = data.events || [];
      this.summary = data.summary || null;
      this.available = true;
      this.lastError = null;
      this.renderSummary();
      this.renderMap();
      this.renderList();
      this.updateNearbyBanner();
      this.setStatus(this.summary?.last_updated ? `Updated ${this.relTime(this.summary.last_updated)}` : "Live risk ready");
    } catch (e) {
      this.available = false;
      this.lastError = e.message || "unavailable";
      this.setStatus("Live risk data temporarily unavailable");
      const card = document.getElementById("liveRiskSummaryBody");
      if (card) {
        card.innerHTML = `<p class="live-risk-empty">Live risk data temporarily unavailable.</p>`;
      }
    }
  },

  async refresh(forcePipeline) {
    if (forcePipeline) {
      this.setStatus("Refreshing sources…");
      try {
        await fetch("/api/risk-events/refresh", { method: "POST" });
      } catch (_) {}
    }
    await this.load();
  },

  setStatus(text) {
    const el = document.getElementById("liveRiskUpdated");
    if (el) el.textContent = text;
  },

  relTime(ts) {
    if (!ts) return "just now";
    const t = Date.parse(String(ts).replace(" ", "T"));
    if (!t) return "recently";
    const sec = Math.max(0, Math.round((Date.now() - t) / 1000));
    if (sec < 60) return `${sec}s ago`;
    if (sec < 3600) return `${Math.round(sec / 60)} min ago`;
    return `${Math.round(sec / 3600)} h ago`;
  },

  filteredEvents() {
    return (this.events || []).filter((e) => {
      if (this.filters.event_type !== "all" && e.event_type !== this.filters.event_type) return false;
      if (this.filters.risk_level !== "all" && e.risk_level !== this.filters.risk_level) return false;
      if (this.filters.source === "official" && !e.official_alert) return false;
      if (this.filters.source === "news" && e.official_alert) return false;
      return true;
    });
  },

  renderSummary() {
    const body = document.getElementById("liveRiskSummaryBody");
    const c = this.summary?.counts || {};
    if (!body) return;
    body.innerHTML = `
      <div class="live-risk-counts">
        <span class="lr-pill critical"><strong>${c.CRITICAL || 0}</strong> Critical</span>
        <span class="lr-pill high"><strong>${c.HIGH || 0}</strong> High</span>
        <span class="lr-pill moderate"><strong>${c.MODERATE || 0}</strong> Moderate</span>
        <span class="lr-pill low"><strong>${c.LOW || 0}</strong> Low</span>
      </div>
      <p class="live-risk-note">News-detected intelligence with location extraction. Official alerts are labelled separately when available.</p>
    `;
  },

  renderList() {
    const list = document.getElementById("liveRiskEventList");
    if (!list) return;
    const rows = this.filteredEvents().slice(0, 6);
    if (!rows.length) {
      list.innerHTML = `<li class="live-risk-empty">No active mapped risk events for these filters.</li>`;
      return;
    }
    list.innerHTML = rows
      .map((e) => {
        const color = this.COLORS[e.risk_level] || this.COLORS.MODERATE;
        return `<li class="live-risk-item" data-id="${e.id}">
          <span class="lr-dot" style="background:${color}"></span>
          <div>
            <strong>${this.esc(e.location_label)}</strong>
            <span>${this.esc((e.event_type || "").replace(/_/g, " "))} · ${e.risk_level} · conf ${e.confidence_score}%</span>
          </div>
        </li>`;
      })
      .join("");
    list.querySelectorAll(".live-risk-item").forEach((li) => {
      li.addEventListener("click", () => {
        const ev = this.events.find((x) => String(x.id) === li.dataset.id);
        if (ev) this.focusEvent(ev);
      });
    });
  },

  ensureMapLayer() {
    const map = window.getSafetyMap?.();
    if (!map || typeof L === "undefined") return null;
    if (!this.layer) {
      this.layer = L.layerGroup();
      const toggle = document.getElementById("toggleLiveRisk");
      if (!toggle || toggle.checked) map.addLayer(this.layer);
    }
    return this.layer;
  },

  renderMap() {
    const layer = this.ensureMapLayer();
    if (!layer) return;
    layer.clearLayers();
    this.filteredEvents().forEach((e) => {
      const color = this.COLORS[e.risk_level] || "#f59e0b";
      const radius = Math.max(8000, Number(e.radius_m) || 25000);
      const circle = L.circle([e.lat, e.lng], {
        radius,
        color,
        weight: 2,
        fillColor: color,
        fillOpacity: e.risk_level === "CRITICAL" || e.risk_level === "HIGH" ? 0.22 : 0.14,
        className: "live-risk-circle",
      });
      const marker = L.circleMarker([e.lat, e.lng], {
        radius: 9,
        color: "#fff",
        weight: 2,
        fillColor: color,
        fillOpacity: 0.95,
      });
      const html = this.popupHtml(e);
      circle.bindPopup(html, { maxWidth: 320 });
      marker.bindPopup(html, { maxWidth: 320 });
      circle.addTo(layer);
      marker.addTo(layer);
    });
  },

  popupHtml(e) {
    const official = e.official_alert
      ? `<div class="lr-badge official">Official alert signal</div>`
      : `<div class="lr-badge news">News reports (system detection)</div>`;
    const sources = (e.sources || [])
      .slice(0, 4)
      .map((s) => {
        const url = s.url ? `<a href="${this.esc(s.url)}" target="_blank" rel="noopener noreferrer">${this.esc(s.source || "Source")}</a>` : this.esc(s.source || "Source");
        return `<li>${url}</li>`;
      })
      .join("");
    return `
      <div class="popup-dest-card live-risk-popup">
        <strong style="color:${this.COLORS[e.risk_level] || "#f59e0b"};">${e.risk_level} RISK</strong>
        <div style="margin-top:4px;font-weight:700;color:#fff;">${this.esc(e.location_label)}</div>
        <p style="margin:6px 0 0;font-size:12px;color:#cbd5e1;">
          Event: ${this.esc((e.event_type || "").replace(/_/g, " "))}<br>
          Risk: ${e.risk_score} / 100<br>
          Confidence: ${e.confidence_score}%<br>
          Sources: ${e.independent_sources || 1} independent<br>
          Updated: ${this.esc(this.relTime(e.last_seen_at))}
        </p>
        ${official}
        <p style="margin:8px 0 0;font-size:11px;color:#94a3b8;">${this.esc(e.summary || "")}</p>
        ${sources ? `<ul style="margin:8px 0 0;padding-left:16px;font-size:11px;">${sources}</ul>` : ""}
      </div>
    `;
  },

  focusEvent(e) {
    const map = window.getSafetyMap?.();
    if (!map || e.lat == null) return;
    map.flyTo([e.lat, e.lng], 8, { animate: true, duration: 0.9 });
  },

  async updateNearbyBanner() {
    const el = document.getElementById("liveRiskNearbyBanner");
    if (!el) return;
    const pos = window.GeolocationEngine?.currentPosition;
    if (!pos?.lat || !pos?.lng) {
      el.hidden = true;
      return;
    }
    try {
      const res = await fetch(`/api/risk-events/nearby?lat=${pos.lat}&lng=${pos.lng}&radius_km=80`);
      const data = await res.json();
      const top = (data.events || [])[0];
      if (!top) {
        el.hidden = true;
        return;
      }
      el.hidden = false;
      el.innerHTML = `
        <strong>Nearby risk signal</strong>
        ${this.esc((top.event_type || "").replace(/_/g, " "))} near ${this.esc(top.location_label)}
        (~${top.distance_km} km) · ${top.risk_level}
        <span class="muted">News/official detection — verify before travel decisions.</span>
      `;
    } catch (_) {
      el.hidden = true;
    }
  },

  esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },
};

window.LiveRiskIntel = LiveRiskIntel;
document.addEventListener("DOMContentLoaded", () => LiveRiskIntel.init());
