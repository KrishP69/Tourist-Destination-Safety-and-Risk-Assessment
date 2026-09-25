/**
 * Tourist-first UX shell: explore drawer, map float tools, SOS FAB,
 * bottom nav, and safety/nearby/alerts snapshots from real APIs.
 */
const TouristShell = {
  _nearbyCache: [],
  _alertsCache: [],
  _refreshTimer: null,

  init() {
    this.bindExplore();
    this.bindMapTools();
    this.bindBottomNav();
    this.bindDesktopNav();
    this.bindSnapshotActions();
    this.refreshSnapshots();
    this._refreshTimer = setInterval(() => this.refreshSnapshots(), 30000);
    window.addEventListener("locationUpdated", () => this.refreshSnapshots());
    window.addEventListener("touristDataReady", () => this.refreshSnapshots());
  },

  bindExplore() {
    const open = () => this.openExplore();
    const close = () => this.closeExplore();
    document.getElementById("btnOpenExplore")?.addEventListener("click", open);
    document.getElementById("navTabExplore")?.addEventListener("click", open);
    document.getElementById("btnCloseExplore")?.addEventListener("click", close);
    document.getElementById("exploreDrawerBackdrop")?.addEventListener("click", (e) => {
      if (e.target.id === "exploreDrawerBackdrop") close();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
  },

  openExplore() {
    const bd = document.getElementById("exploreDrawerBackdrop");
    bd?.classList.add("open");
    bd?.setAttribute("aria-hidden", "false");
    this.setNavActive("explore");
  },

  closeExplore() {
    const bd = document.getElementById("exploreDrawerBackdrop");
    bd?.classList.remove("open");
    bd?.setAttribute("aria-hidden", "true");
  },

  bindMapTools() {
    document.getElementById("btnMapZoomIn")?.addEventListener("click", () => {
      const map = window.getSafetyMap?.();
      if (map) map.zoomIn();
    });
    document.getElementById("btnMapZoomOut")?.addEventListener("click", () => {
      const map = window.getSafetyMap?.();
      if (map) map.zoomOut();
    });
    document.getElementById("btnMapRecenter")?.addEventListener("click", () => {
      const map = window.getSafetyMap?.();
      const pos = window.GeolocationEngine?.currentPosition;
      if (map && pos?.lat != null && pos?.lng != null) {
        map.flyTo([pos.lat, pos.lng], Math.max(map.getZoom(), 13), { animate: true, duration: 0.9 });
      } else {
        document.getElementById("btnAcquireCurrentGPS")?.click();
      }
    });

    const layersBtn = document.getElementById("btnMapLayers");
    const pop = document.getElementById("layersPopover");
    layersBtn?.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = pop?.classList.toggle("open");
      layersBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", (e) => {
      if (!pop || !layersBtn) return;
      if (pop.contains(e.target) || layersBtn.contains(e.target)) return;
      pop.classList.remove("open");
      layersBtn.setAttribute("aria-expanded", "false");
    });
  },

  bindBottomNav() {
    document.getElementById("navTabMap")?.addEventListener("click", () => {
      this.closeExplore();
      this.setNavActive("map");
      document.querySelector(".map-wrapper-card")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    document.getElementById("navTabAlerts")?.addEventListener("click", () => {
      this.closeExplore();
      this.setNavActive("alerts");
      document.querySelector(".incident-ticker-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    document.getElementById("navTabAccount")?.addEventListener("click", () => {
      this.setNavActive("account");
      if (window.UxShell) UxShell.openMobile();
      else document.getElementById("btnMobileMenu")?.click();
    });
  },

  bindDesktopNav() {
    document.getElementById("navLinkHome")?.addEventListener("click", () => {
      this.closeExplore();
      window.scrollTo({ top: 0, behavior: "smooth" });
      this.markDesktopNav("navLinkHome");
    });
    document.getElementById("navLinkSafety")?.addEventListener("click", () => {
      document.getElementById("touristSnapshotRow")?.scrollIntoView({ behavior: "smooth", block: "start" });
      this.markDesktopNav("navLinkSafety");
    });
    document.getElementById("navLinkAlerts")?.addEventListener("click", () => {
      document.querySelector(".incident-ticker-section")?.scrollIntoView({ behavior: "smooth" });
      this.markDesktopNav("navLinkAlerts");
    });
    document.getElementById("navLinkTickets")?.addEventListener("click", () => {
      document.getElementById("btnMyTickets")?.click();
      this.markDesktopNav("navLinkTickets");
    });
    document.getElementById("btnOpenExplore")?.addEventListener("click", () => {
      this.markDesktopNav("btnOpenExplore");
    });
  },

  markDesktopNav(id) {
    document.querySelectorAll(".tourist-nav-links .nav-text-link").forEach((btn) => {
      btn.classList.toggle("active", btn.id === id);
    });
  },

  setNavActive(key) {
    document.querySelectorAll(".tourist-bottom-nav button").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.nav === key);
    });
  },

  bindSnapshotActions() {
    document.getElementById("btnJumpToAlerts")?.addEventListener("click", () => {
      document.querySelector(".incident-ticker-section")?.scrollIntoView({ behavior: "smooth" });
      this.setNavActive("alerts");
    });
  },

  haversineKm(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const toRad = (d) => (d * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  },

  formatDistance(km) {
    if (km == null || Number.isNaN(km)) return "";
    if (km < 1) return `${Math.round(km * 1000)} m`;
    return `${km.toFixed(1)} km`;
  },

  async refreshSnapshots() {
    await Promise.all([this.updateSafetySnapshot(), this.updateNearbySnapshot(), this.updateAlertsSnapshot()]);
  },

  async updateSafetySnapshot() {
    const scoreEl = document.getElementById("touristSafetyScore");
    const blurbEl = document.getElementById("touristSafetyBlurb");
    const avgEl = document.getElementById("touristNetworkAvg");
    const alertEl = document.getElementById("touristAlertCount");
    if (!scoreEl) return;

    try {
      const res = await fetch("/api/destinations/stats/overview");
      const stats = await res.json();
      const avg = stats.average_safety_score;
      const alerts = stats.active_incidents || 0;
      if (avgEl) avgEl.textContent = avg != null ? `${avg} / 100` : "—";
      if (alertEl) alertEl.textContent = String(alerts);

      // Prefer nearest destination safety if user location + destinations exist
      const pos = window.GeolocationEngine?.currentPosition;
      const dests = typeof allDestinationsData !== "undefined" ? allDestinationsData : [];
      let localScore = null;
      let localName = null;
      if (pos?.lat != null && dests.length) {
        let best = null;
        let bestKm = Infinity;
        dests.forEach((d) => {
          if (d.lat == null || d.lng == null) return;
          const km =
            d.distance_km != null
              ? Number(d.distance_km)
              : this.haversineKm(pos.lat, pos.lng, d.lat, d.lng);
          if (km < bestKm) {
            bestKm = km;
            best = d;
          }
        });
        if (best && bestKm < 80) {
          localScore = best.overall_safety_score ?? best.safety_score ?? null;
          localName = best.name;
        }
      }

      const displayScore = localScore != null ? localScore : avg;
      if (displayScore == null) {
        scoreEl.textContent = "—";
        scoreEl.className = "snapshot-metric";
        if (blurbEl) blurbEl.textContent = "Safety data is loading…";
        return;
      }

      scoreEl.textContent = `${displayScore} / 100`;
      scoreEl.className = "snapshot-metric";
      if (displayScore >= 70) scoreEl.classList.add("safe");
      else if (displayScore >= 45) scoreEl.classList.add("warn");
      else scoreEl.classList.add("danger");

      if (blurbEl) {
        if (localName) {
          blurbEl.textContent = `Near ${localName}. Based on destination safety assessment — not a guarantee.`;
        } else {
          blurbEl.textContent =
            "Network average across monitored destinations. Enable location for a nearby reading.";
        }
      }
    } catch (_) {
      scoreEl.textContent = "—";
      if (blurbEl) blurbEl.textContent = "Unable to load safety information.";
    }
  },

  async updateNearbySnapshot() {
    const list = document.getElementById("touristNearbyList");
    if (!list) return;

    const pos = window.GeolocationEngine?.currentPosition;
    try {
      if (!this._nearbyCache.length) {
        const res = await fetch("/api/emergency/facilities");
        if (!res.ok) throw new Error("facilities");
        this._nearbyCache = await res.json();
      }
      const facilities = this._nearbyCache || [];
      if (!facilities.length) {
        list.innerHTML = `<li class="snapshot-empty">No emergency facilities in the directory yet.</li>`;
        return;
      }

      let ranked = facilities.filter((f) => f.lat != null && f.lng != null);
      if (pos?.lat != null && pos?.lng != null) {
        ranked = ranked
          .map((f) => ({
            ...f,
            _km: this.haversineKm(pos.lat, pos.lng, Number(f.lat), Number(f.lng)),
          }))
          .sort((a, b) => a._km - b._km)
          .slice(0, 4);
      } else {
        ranked = ranked.slice(0, 4).map((f) => ({ ...f, _km: null }));
      }

      if (!ranked.length) {
        list.innerHTML = `<li class="snapshot-empty">Enable location to rank nearby help.</li>`;
        return;
      }

      list.innerHTML = ranked
        .map((f) => {
          const type = (f.facility_type || "Facility").replace(/_/g, " ");
          const dist =
            f._km != null
              ? `<span>${this.formatDistance(f._km)}</span>`
              : `<span></span>`;
          return `<li><strong>${this.escapeHtml(f.facility_name || type)}</strong>${dist}</li>`;
        })
        .join("");
    } catch (_) {
      list.innerHTML = `<li class="snapshot-empty">Unable to load nearby help. <button type="button" class="btn-crowd-ghost" id="btnRetryNearby" style="margin-left:6px;">Retry</button></li>`;
      document.getElementById("btnRetryNearby")?.addEventListener("click", () => {
        this._nearbyCache = [];
        this.updateNearbySnapshot();
      });
    }
  },

  async updateAlertsSnapshot() {
    const list = document.getElementById("touristAlertsList");
    if (!list) return;
    try {
      const res = await fetch("/api/incidents?status=Active");
      const incidents = await res.json();
      this._alertsCache = incidents || [];
      if (!this._alertsCache.length) {
        list.innerHTML = `<li class="snapshot-empty">No nearby alerts.</li>`;
        return;
      }
      list.innerHTML = this._alertsCache
        .slice(0, 3)
        .map((inc) => {
          const title = this.escapeHtml(inc.title || inc.category || "Alert");
          const where = this.escapeHtml(inc.location_name || inc.destination_name || "");
          return `<li><strong>${title}</strong><span>${where}</span></li>`;
        })
        .join("");
    } catch (_) {
      list.innerHTML = `<li class="snapshot-empty">Unable to load alerts.</li>`;
    }
  },

  escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },
};

window.TouristShell = TouristShell;

document.addEventListener("DOMContentLoaded", () => {
  TouristShell.init();
});
