/**
 * Best Time to Visit — signature recommendation UI wired to prediction engine.
 */
const BestTime = {
  destId: null,
  lastPayload: null,
  ranks: ["🥇", "🥈", "🥉"],

  levelEmoji(level) {
    return (window.CrowdDashboard && CrowdDashboard.levelEmoji(level)) || "⚪";
  },

  formatTime(t) {
    if (!t) return "—";
    const [h, m] = t.split(":").map(Number);
    const ampm = h >= 12 ? "PM" : "AM";
    const hr = ((h + 11) % 12) + 1;
    return `${hr}:${String(m || 0).padStart(2, "0")} ${ampm}`;
  },

  async load(destId) {
    this.destId = destId || this.destId || window.currentSelectedDestination?.id;
    if (!this.destId) return;
    const date = document.getElementById("bookingSlotDate")?.value || new Date().toISOString().slice(0, 10);
    const box = document.getElementById("bestTimeOptions");
    const conf = document.getElementById("bestTimeConfidence");
    if (box) box.innerHTML = `<div style="font-size:0.78rem;color:#94a3b8;">Analyzing lower-crowd slots…</div>`;
    try {
      const res = await fetch(`/api/crowd/${this.destId}/best-time?date=${date}&limit=3`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Best time unavailable");
      this.lastPayload = data;
      this.render(data);
      await this.loadForecast(this.destId);
    } catch (e) {
      if (box) box.innerHTML = `<div style="color:#f87171;font-size:0.78rem;">${e.message}</div>`;
      if (conf) conf.textContent = "";
    }
  },

  render(data) {
    const box = document.getElementById("bestTimeOptions");
    const conf = document.getElementById("bestTimeConfidence");
    if (!box) return;
    const opts = data.top_options || [];
    if (!opts.length) {
      box.innerHTML = `<div style="font-size:0.78rem;color:#94a3b8;">${data.unavailable_message || "No lower-crowd slots available."}</div>`;
      return;
    }
    box.innerHTML = opts
      .map((o, i) => {
        const top = i === 0 ? "top" : "";
        return `
        <div class="best-option ${top}">
          <div class="best-rank" aria-hidden="true">${this.ranks[i] || "•"}</div>
          <div class="best-option-meta">
            <strong>${this.formatTime(o.start_time)} – ${this.formatTime(o.end_time)}</strong>
            Predicted crowd: ~${o.predicted_crowd} · Occupancy: ${o.predicted_occupancy}% ·
            Tickets available: ${o.available}<br>
            <span class="crowd-level-pill ${o.crowd_level || "UNKNOWN"}">${this.levelEmoji(o.crowd_level)} ${o.crowd_level || "UNKNOWN"}</span>
            <span style="margin-left:6px;color:#64748b;">Lower predicted crowd</span>
          </div>
          <button type="button" class="btn-book-best" onclick="BestTime.bookSlot(${o.slot_id})">Book this slot</button>
        </div>`;
      })
      .join("");

    if (conf) {
      const c = data.confidence;
      const limited = data.limited_data;
      conf.innerHTML = c != null
        ? `Prediction confidence: <strong>${c}%</strong>${limited ? " — Limited data available" : ""}`
        : "Prediction confidence unavailable";
    }

    // Hero tickets available from top options sum remaining
    const heroTickets = document.getElementById("heroTicketsAvail");
    if (heroTickets) {
      const sum = opts.reduce((a, o) => a + (o.available || 0), 0);
      heroTickets.textContent = String(sum);
    }
  },

  async loadForecast(destId) {
    try {
      const res = await fetch(`/api/crowd/${destId}/forecast`);
      const data = await res.json();
      if (!res.ok) return;
      this.renderForecast(data);
      this.renderInsight(data.insight || {});
    } catch (_) {}
  },

  renderForecast(data) {
    const chart = document.getElementById("forecastChart");
    if (!chart) return;
    const points = data.points || [];
    const vals = points.map((p) => p.value).filter((v) => v != null);
    const max = Math.max(...vals, 1);
    chart.innerHTML = points
      .map((p) => {
        const h = p.value != null ? Math.max(8, Math.round((p.value / max) * 100)) : 8;
        const cls = p.kind === "estimated" ? "estimated" : "predicted";
        return `
        <div class="forecast-bar-wrap">
          <div class="forecast-value">${p.value != null ? `~${p.value}` : "—"}</div>
          <div class="forecast-bar ${cls}" style="height:${h}px" title="${p.kind}"></div>
          <div class="forecast-label">${p.label}<br><span style="font-size:0.58rem;">${p.kind === "estimated" ? "estimate" : "predicted"}</span></div>
        </div>`;
      })
      .join("");
    const peak = document.getElementById("forecastPeak");
    const trend = document.getElementById("forecastTrend");
    if (peak) peak.textContent = data.peak_expected_around || "—";
    if (trend) {
      const t = data.trend || "stable";
      trend.textContent = t.startsWith("increasing") ? `↑ ${t}` : t.startsWith("decreasing") ? `↓ ${t}` : t;
    }
  },

  renderInsight(insight) {
    const q = document.getElementById("insightQuestion");
    const list = document.getElementById("insightReasons");
    const peak = document.getElementById("insightPeak");
    const conf = document.getElementById("insightConfidence");
    if (q) q.textContent = insight.question || "What is shaping today’s crowd?";
    if (list) {
      const reasons = insight.reasons || [];
      list.innerHTML = reasons.length
        ? reasons
            .map((r) => {
              const arrow = r.direction === "up" ? "↑" : r.direction === "down" ? "↓" : "•";
              const cls = r.direction === "up" ? "dir-up" : r.direction === "down" ? "dir-down" : "";
              return `<li><span class="${cls}">${arrow}</span> ${r.text}</li>`;
            })
            .join("")
        : `<li style="color:#64748b;">Insufficient signals for an explanation right now.</li>`;
    }
    if (peak) {
      peak.textContent =
        insight.expected_peak != null
          ? `${insight.expected_peak}${insight.expected_peak_crowd != null ? ` (~${insight.expected_peak_crowd})` : ""}`
          : "—";
    }
    if (conf) {
      const c = insight.confidence;
      conf.textContent =
        c != null
          ? `${c}%${insight.limited_data ? " (limited data)" : ""}`
          : "—";
    }
  },

  openModal() {
    const modal = document.getElementById("bestTimeModal");
    const body = document.getElementById("bestTimeModalBody");
    if (!modal || !body) return;
    const data = this.lastPayload;
    if (!data || !(data.top_options || []).length) {
      this.load().then(() => this.openModal());
      return;
    }
    const top = data.recommended || data.top_options[0];
    const others = (data.top_options || []).slice(1);
    body.innerHTML = `
      <div class="confirm-card" style="margin-top:10px;">
        <div style="font-size:0.72rem;color:#94a3b8;margin-bottom:6px;">RECOMMENDED — lower predicted crowd</div>
        <strong style="font-size:1.1rem;color:#f8fafc;">${this.formatTime(top.start_time)} – ${this.formatTime(top.end_time)}</strong>
        <div class="row"><span>Predicted crowd</span><b>~${top.predicted_crowd}</b></div>
        <div class="row"><span>Occupancy</span><b>${top.predicted_occupancy}%</b></div>
        <div class="row"><span>Tickets available</span><b>${top.available}</b></div>
        <div class="row"><span>Confidence</span><b>${top.confidence}%${data.limited_data ? " · Limited data" : ""}</b></div>
        <button type="button" class="btn-book-best" style="margin-top:10px;width:100%;" onclick="BestTime.bookSlot(${top.slot_id}); BestTime.closeModal();">Book this slot</button>
      </div>
      ${
        others.length
          ? `<p class="muted" style="margin-top:12px;">Other lower-crowd options</p>
             ${others
               .map(
                 (o) =>
                   `<div class="ticket-item"><strong>${this.formatTime(o.start_time)} – ${this.formatTime(o.end_time)}</strong>~${o.predicted_crowd} visitors · ${o.available} available
                    <button type="button" class="btn-crowd-ghost" style="margin-top:6px;" onclick="BestTime.bookSlot(${o.slot_id}); BestTime.closeModal();">Book</button></div>`
               )
               .join("")}`
          : ""
      }`;
    modal.classList.add("open");
  },

  closeModal() {
    document.getElementById("bestTimeModal")?.classList.remove("open");
  },

  bookSlot(slotId) {
    if (window.SmartBooking) SmartBooking.bookSlot(slotId);
  },
};

window.BestTime = BestTime;
