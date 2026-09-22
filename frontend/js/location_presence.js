/**
 * Opt-in location presence for crowd estimation.
 * Does not store precise trails — only posts membership pings after consent.
 */
const LocationPresence = {
  watchId: null,
  consentGranted: false,
  status: "idle", // idle | prompting | granted | denied | unavailable | active
  updateIntervalMs: 30000,
  lastSentAt: 0,

  getAnonymousId() {
    let id = localStorage.getItem("safetour_anon_id");
    if (!id) {
      if (window.crypto && crypto.randomUUID) {
        id = "anon_" + crypto.randomUUID().replace(/-/g, "");
      } else {
        id = "anon_" + String(Date.now()) + Math.random().toString(16).slice(2);
      }
      localStorage.setItem("safetour_anon_id", id);
    }
    return id;
  },

  updateStatusChip() {
    const chip = document.getElementById("locationPresenceStatus");
    if (!chip) return;
    chip.classList.remove("active", "denied");
    const labels = {
      idle: "Location off",
      prompting: "Awaiting permission…",
      granted: "Permission granted",
      denied: "Permission denied",
      unavailable: "Location unavailable",
      active: "Sharing for crowd estimate",
    };
    chip.textContent = labels[this.status] || this.status;
    if (this.status === "active" || this.status === "granted") chip.classList.add("active");
    if (this.status === "denied") chip.classList.add("denied");
  },

  showConsentBanner(show = true) {
    const banner = document.getElementById("locationConsentBanner");
    if (!banner) return;
    banner.classList.toggle("visible", show);
  },

  async loadConfig() {
    try {
      const res = await fetch("/api/location/config");
      const cfg = await res.json();
      if (cfg.update_interval_sec) this.updateIntervalMs = cfg.update_interval_sec * 1000;
      const purpose = document.getElementById("locationConsentPurpose");
      if (purpose && cfg.purpose) purpose.textContent = cfg.purpose;
    } catch (_) {}
  },

  async enable() {
    this.status = "prompting";
    this.updateStatusChip();
    if (!("geolocation" in navigator)) {
      this.status = "unavailable";
      this.updateStatusChip();
      this.showConsentBanner(false);
      if (typeof window.showLiveToast === "function") {
        window.showLiveToast("Geolocation not supported on this device");
      }
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        this.consentGranted = true;
        this.status = "granted";
        this.updateStatusChip();
        this.showConsentBanner(false);
        localStorage.setItem("safetour_location_consent", "1");
        await this.sendUpdate(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy);
        this.startWatch();
      },
      (err) => {
        if (err.code === 1) this.status = "denied";
        else if (err.code === 2) this.status = "unavailable";
        else this.status = "unavailable";
        this.updateStatusChip();
        if (typeof window.showLiveToast === "function") {
          window.showLiveToast("Location permission not granted — crowd will use bookings/history");
        }
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  },

  decline() {
    this.consentGranted = false;
    this.status = "denied";
    localStorage.setItem("safetour_location_consent", "0");
    this.showConsentBanner(false);
    this.updateStatusChip();
    this.stop();
  },

  startWatch() {
    if (this.watchId != null) return;
    this.watchId = navigator.geolocation.watchPosition(
      (pos) => {
        this.status = "active";
        this.updateStatusChip();
        const now = Date.now();
        if (now - this.lastSentAt < this.updateIntervalMs) return;
        this.sendUpdate(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy);
      },
      () => {
        this.status = "unavailable";
        this.updateStatusChip();
      },
      { enableHighAccuracy: true, maximumAge: 15000, timeout: 15000 }
    );
  },

  async sendUpdate(lat, lng, accuracy) {
    this.lastSentAt = Date.now();
    const body = {
      anonymous_user_id: this.getAnonymousId(),
      latitude: lat,
      longitude: lng,
      accuracy_m: accuracy,
    };
    if (window.currentSelectedDestination?.id) {
      body.destination_id = currentSelectedDestination.id;
    }
    try {
      await fetch("/api/location/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch (_) {}
  },

  async stop() {
    if (this.watchId != null) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
    try {
      await fetch("/api/location/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ anonymous_user_id: this.getAnonymousId() }),
      });
    } catch (_) {}
  },

  init() {
    this.loadConfig();
    this.getAnonymousId();
    const consent = localStorage.getItem("safetour_location_consent");
    if (consent === "1") {
      this.enable();
    } else if (consent !== "0") {
      this.showConsentBanner(true);
      this.status = "idle";
    }
    this.updateStatusChip();

    document.getElementById("btnEnableLocationCrowd")?.addEventListener("click", () => this.enable());
    document.getElementById("btnDeclineLocationCrowd")?.addEventListener("click", () => this.decline());
  },
};

window.LocationPresence = LocationPresence;
