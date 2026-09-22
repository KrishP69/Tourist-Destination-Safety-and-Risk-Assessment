/**
 * Crowd Intelligence Dashboard + presence reporting helpers.
 * Terminology: Observed / Estimated / Predicted — never "exact live headcount".
 */
const CrowdDashboard = {
  pollTimer: null,
  ws: null,
  currentDestId: null,
  lastPayload: null,

  levelEmoji(level) {
    const map = {
      LOW: "🟢",
      MODERATE: "🟡",
      HIGH: "🟠",
      VERY_HIGH: "🔴",
      CRITICAL: "⚫",
      UNKNOWN: "⚪",
    };
    return map[level] || "⚪";
  },

  async fetchCrowd(destId) {
    const res = await fetch(`/api/crowd/${destId}`);
    if (!res.ok) throw new Error("Crowd data unavailable");
    return res.json();
  },

  render(destId, data) {
    this.currentDestId = destId;
    this.lastPayload = data;
    const root = document.getElementById("crowdIntelCard");
    if (!root) return;

    const demo = document.getElementById("crowdDemoBanner");
    if (demo) {
      demo.classList.toggle("visible", !!(data.is_demo_data || data.demo_mode));
    }

    const unavailable = !data.data_available || data.estimated_crowd == null;
    const setText = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    if (unavailable) {
      setText("crowdObserved", "—");
      setText("crowdBooked", "—");
      setText("crowdEstimated", "Unavailable");
      setText("crowdOccupancy", "—");
      setText("crowdCapacity", data.capacity != null ? String(data.capacity) : "—");
      setText("crowdDensity", "—");
      setText("crowdTrend", "—");
      setText("crowdConfidence", "—");
      setText("crowdPredicted", "—");
      setText("crowdUpdated", "—");
      const levelEl = document.getElementById("crowdLevelPill");
      if (levelEl) {
        levelEl.className = "crowd-level-pill UNKNOWN";
        levelEl.textContent = "Live crowd information currently unavailable.";
      }
      return;
    }

    setText("crowdObserved", String(data.observed_users ?? 0));
    setText("crowdBooked", String(data.booked_visitors ?? 0));
    setText("crowdEstimated", `~${data.estimated_crowd}`);
    setText("crowdOccupancy", `${data.occupancy_percentage}%`);
    setText("crowdCapacity", String(data.capacity));
    setText(
      "crowdDensity",
      data.density != null ? `${Number(data.density).toFixed(4)} /m²` : "n/a"
    );
    setText("crowdTrend", `${data.trend || "stable"} (${data.trend_delta_30m >= 0 ? "+" : ""}${data.trend_delta_30m ?? 0})`);
    setText(
      "crowdConfidence",
      `${data.confidence}% (${data.confidence_label || "Low"})${(data.confidence || 0) < 50 ? " · Limited data" : ""}`
    );

    const pred = data.next_hour_prediction || {};
    setText(
      "crowdPredicted",
      pred.predicted_crowd != null ? `~${pred.predicted_crowd}` : "—"
    );
    setText("crowdUpdated", "just now");

    // Hero metrics
    setText("heroEstimatedCrowd", `~${data.estimated_crowd}`);
    setText("heroOccupancy", `${data.occupancy_percentage}%`);
    setText("heroNextHour", pred.predicted_crowd != null ? `~${pred.predicted_crowd}` : "—");

    const crowdChip = document.getElementById("detailCrowdChip");
    if (crowdChip) {
      const lvl = data.crowd_level || "UNKNOWN";
      const rising = String(data.trend || "").startsWith("increasing");
      crowdChip.textContent = rising ? `CROWD RISING · ${lvl}` : `CROWD ${lvl}`;
    }
    const safetyChip = document.getElementById("detailSafetyChip");
    const riskBadge = document.getElementById("detailRiskBadge");
    if (safetyChip && riskBadge) {
      const t = riskBadge.innerText || "";
      safetyChip.className = "status-chip";
      if (t.includes("Low Risk") || t.includes("Safe")) {
        safetyChip.classList.add("safe");
        safetyChip.textContent = "SAFE";
      } else if (t.includes("Moderate")) {
        safetyChip.classList.add("moderate");
        safetyChip.textContent = "MODERATE RISK";
      } else if (t.includes("High Caution")) {
        safetyChip.classList.add("caution");
        safetyChip.textContent = "HIGH CAUTION";
      } else {
        safetyChip.classList.add("severe");
        safetyChip.textContent = "SEVERE RISK";
      }
    }

    if (window.LiveStatus) LiveStatus.markFresh();

    const levelEl = document.getElementById("crowdLevelPill");
    if (levelEl) {
      const lvl = data.crowd_level || "UNKNOWN";
      levelEl.className = `crowd-level-pill ${lvl}`;
      levelEl.textContent = `${this.levelEmoji(lvl)} ${lvl.replace("_", " ")}`;
    }
  },

  async loadForDestination(destId) {
    const loading = document.getElementById("crowdLoadingState");
    if (loading) loading.style.display = "block";
    try {
      const data = await this.fetchCrowd(destId);
      this.render(destId, data);
      if (typeof MapEngineCrowd !== "undefined") {
        MapEngineCrowd.updateDestinationCrowd(destId, data);
      }
    } catch (err) {
      console.warn("Crowd load failed", err);
      this.render(destId, { data_available: false, capacity: null });
    } finally {
      if (loading) loading.style.display = "none";
    }
  },

  startPolling(destId, intervalMs = 20000) {
    this.stopPolling();
    this.loadForDestination(destId);
    this.pollTimer = setInterval(() => this.loadForDestination(destId), intervalMs);
    this.connectWebSocket(destId);
  },

  stopPolling() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  },

  connectWebSocket(destId) {
    if (this.ws) {
      try { this.ws.close(); } catch (_) {}
      this.ws = null;
    }
    try {
      const proto = location.protocol === "https:" ? "wss" : "ws";
      this.ws = new WebSocket(`${proto}://${location.host}/api/crowd/ws`);
      this.ws.onopen = () => {
        this.ws.send(JSON.stringify({ type: "subscribe", destination_id: destId }));
      };
      this.ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          if (msg.type === "crowd_detail" && msg.payload) {
            this.render(destId, msg.payload);
          }
        } catch (_) {}
      };
      this.ws.onerror = () => {
        /* Polling remains the fallback */
      };
    } catch (_) {
      /* Browser / proxy may block WS — polling still works */
    }
  },
};

window.CrowdDashboard = CrowdDashboard;
