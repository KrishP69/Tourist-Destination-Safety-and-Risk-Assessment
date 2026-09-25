/**
 * Destinations panel — Near Me sorting, clean cards, List/Map toggle.
 * Preserves selectDestinationById, filters, search, and existing APIs.
 */
const DestinationsPanel = {
  NEARBY_RADIUS_KM: 80,
  NEARBY_EXPANDED_RADIUS_KM: 150,
  NEARBY_PREVIEW: 7,

  mode: "near", // near | all
  view: "list", // list | map
  showAllNearby: false,
  nearbyRadiusKm: 80,
  _sideMap: null,
  _sideMarkers: null,
  _userMarker: null,
  _lastDests: [],
  _bound: false,

  init() {
    if (this._bound) return;
    this._bound = true;
    this.nearbyRadiusKm = this.NEARBY_RADIUS_KM;

    // Event delegation — survives re-renders and is reliable on mobile
    document.getElementById("destinationsListView")?.addEventListener("click", (e) => {
      const modeBtn = e.target.closest("[data-mode]");
      if (modeBtn && modeBtn.id?.startsWith("destMode")) {
        e.preventDefault();
        this.setMode(modeBtn.dataset.mode === "all" ? "all" : "near");
        return;
      }
      const viewBtn = e.target.closest("[data-view]");
      if (viewBtn && viewBtn.id?.startsWith("destView")) {
        e.preventDefault();
        this.setView(viewBtn.dataset.view === "map" ? "map" : "list");
        return;
      }
      if (e.target.closest("#btnViewAllNearby")) {
        e.preventDefault();
        this.expandNearby();
        return;
      }
      if (e.target.closest("#btnDestEnableLocation")) {
        e.preventDefault();
        document.getElementById("btnAcquireCurrentGPS")?.click();
        if (window.LocationPresence) LocationPresence.enable();
        this.updateLocationBanner("loading");
      }
    });

    window.addEventListener("locationUpdated", () => {
      this.updateLocationBanner("ready");
      const source =
        typeof allDestinationsData !== "undefined" && allDestinationsData.length
          ? allDestinationsData
          : this._lastDests;
      if (source?.length) this.render(source);
    });

    this.updateLocationBanner();
  },

  expandNearby() {
    const source =
      typeof allDestinationsData !== "undefined" && allDestinationsData.length
        ? allDestinationsData
        : this._lastDests;

    const enriched = this.attachDistances(source || []);
    const radiusKm = this.nearbyRadiusKm || this.NEARBY_RADIUS_KM;
    const nearbyCount = this.hasUserLocation()
      ? enriched.filter(
          (d) =>
            d.lat != null &&
            d.lng != null &&
            d._distanceKm != null &&
            d._distanceKm <= radiusKm
        ).length
      : 0;
    const previewTruncated = nearbyCount > this.NEARBY_PREVIEW && !this.showAllNearby;

    // Reveal truncated preview within current radius
    if (previewTruncated) {
      this.showAllNearby = true;
      this.render(source);
      document.getElementById("destNearbySection")?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    // Widen radius so more places count as nearby
    if (this.nearbyRadiusKm < this.NEARBY_EXPANDED_RADIUS_KM) {
      this.nearbyRadiusKm = this.NEARBY_EXPANDED_RADIUS_KM;
      this.showAllNearby = true;
      this.mode = "near";
      document.getElementById("destModeNearMe")?.classList.add("active");
      document.getElementById("destModeAll")?.classList.remove("active");
      this.render(source);
      document.getElementById("destNearbySection")?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    // Nothing more nearby → full list sorted by distance
    this.setMode("all");
  },

  setMode(mode) {
    this.mode = mode === "all" ? "all" : "near";
    this.showAllNearby = false;
    if (this.mode === "near") this.nearbyRadiusKm = this.NEARBY_RADIUS_KM;

    document.getElementById("destModeNearMe")?.classList.toggle("active", this.mode === "near");
    document.getElementById("destModeAll")?.classList.toggle("active", this.mode === "all");
    document.getElementById("destModeNearMe")?.setAttribute("aria-pressed", this.mode === "near" ? "true" : "false");
    document.getElementById("destModeAll")?.setAttribute("aria-pressed", this.mode === "all" ? "true" : "false");

    const source =
      typeof allDestinationsData !== "undefined" && allDestinationsData.length
        ? allDestinationsData
        : this._lastDests;
    this.render(source);
    if (this.view === "map") this.refreshSideMap(source);
  },

  setView(view) {
    this.view = view === "map" ? "map" : "list";
    document.getElementById("destViewList")?.classList.toggle("active", this.view === "list");
    document.getElementById("destViewMap")?.classList.toggle("active", this.view === "map");
    document.getElementById("destViewList")?.setAttribute("aria-pressed", this.view === "list" ? "true" : "false");
    document.getElementById("destViewMap")?.setAttribute("aria-pressed", this.view === "map" ? "true" : "false");

    const list = document.getElementById("destListPanel");
    const map = document.getElementById("destMapPanel");
    if (list) {
      list.hidden = this.view !== "list";
      list.classList.toggle("dest-panel-hidden", this.view !== "list");
    }
    if (map) {
      map.hidden = this.view !== "map";
      map.classList.toggle("dest-panel-hidden", this.view !== "map");
    }

    if (this.view === "map") {
      const source =
        typeof allDestinationsData !== "undefined" && allDestinationsData.length
          ? allDestinationsData
          : this._lastDests;
      this.ensureSideMap();
      this.refreshSideMap(source);
      setTimeout(() => {
        try {
          this._sideMap?.invalidateSize();
        } catch (_) {}
      }, 120);
    }
  },

  hasUserLocation() {
    const pos = window.GeolocationEngine?.currentPosition;
    return !!(pos && pos.lat != null && pos.lng != null && Number.isFinite(Number(pos.lat)));
  },

  getUserPos() {
    return window.GeolocationEngine?.currentPosition || null;
  },

  haversineKm(lat1, lon1, lat2, lon2) {
    if (window.GeolocationEngine?._haversineKm) {
      return GeolocationEngine._haversineKm(lat1, lon1, lat2, lon2);
    }
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
    if (km == null || Number.isNaN(Number(km))) return null;
    const n = Number(km);
    if (n < 1) return `${Math.round(n * 1000)} m away`;
    return `${n.toFixed(1)} km away`;
  },

  attachDistances(destinations) {
    const pos = this.getUserPos();
    return (destinations || []).map((d) => {
      const copy = { ...d };
      if (d.lat == null || d.lng == null) {
        copy._distanceKm = null;
        return copy;
      }
      if (pos?.lat != null && pos?.lng != null) {
        if (d.distance_km != null && Number.isFinite(Number(d.distance_km))) {
          copy._distanceKm = Number(d.distance_km);
        } else {
          copy._distanceKm = this.haversineKm(Number(pos.lat), Number(pos.lng), Number(d.lat), Number(d.lng));
        }
      } else {
        copy._distanceKm = d.distance_km != null ? Number(d.distance_km) : null;
      }
      return copy;
    });
  },

  updateLocationBanner(state) {
    const banner = document.getElementById("destLocationBanner");
    const text = document.getElementById("destLocationBannerText");
    const btn = document.getElementById("btnDestEnableLocation");
    if (!banner || !text) return;

    if (state === "loading") {
      banner.hidden = false;
      banner.classList.remove("ready", "denied");
      banner.classList.add("loading");
      text.textContent = "Finding destinations near you…";
      if (btn) btn.hidden = true;
      return;
    }

    if (this.hasUserLocation()) {
      const place =
        this.getUserPos()?.shortName ||
        this.getUserPos()?.locationName ||
        "your location";
      banner.hidden = false;
      banner.classList.add("ready");
      banner.classList.remove("loading", "denied");
      text.textContent = `Showing distances from ${place}`;
      if (btn) btn.hidden = true;
    } else {
      banner.hidden = false;
      banner.classList.remove("ready", "loading");
      banner.classList.add("denied");
      text.textContent = "Enable location to see destinations near you";
      if (btn) btn.hidden = false;
    }
  },

  escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },

  buildCard(dest) {
    const tierInfo =
      typeof getTierDetails === "function"
        ? getTierDetails(dest.risk_tier)
        : { cssClass: "safe" };
    const distLabel = this.formatDistance(dest._distanceKm);
    const openLabel = dest.is_currently_open ? "Open now" : "Closed";
    const openClass = dest.is_currently_open ? "open" : "closed";
    const hours =
      typeof formatTime12h === "function"
        ? `${formatTime12h(dest.opening_time)} – ${formatTime12h(dest.closing_time)}`
        : `${dest.opening_time || "—"} – ${dest.closing_time || "—"}`;
    const category = dest.category || "";
    const placeHint = dest.state || dest.city || "";
    const img =
      dest.image_url ||
      "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=600";
    const alert =
      dest.nearby_incidents && dest.nearby_incidents.length > 0
        ? `<span class="dest-chip alert"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i> Alert</span>`
        : "";

    return `
      <article class="dest-modern-card" data-dest-id="${dest.id}" role="button" tabindex="0"
        aria-label="${this.escapeHtml(dest.name)}, safety ${dest.overall_safety_score}">
        <div class="dest-modern-media">
          <img src="${this.escapeHtml(img)}" alt="${this.escapeHtml(dest.name)}"
            loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1564507592333-c60657eea523?w=600'">
          <div class="dest-score-pill ${tierInfo.cssClass}" title="Safety score">
            <span class="dest-score-label">Safety</span>
            <span class="dest-score-value">${dest.overall_safety_score}</span>
          </div>
        </div>
        <div class="dest-modern-body">
          <h4 class="dest-modern-name">${this.escapeHtml(dest.name)}</h4>
          ${
            distLabel
              ? `<p class="dest-modern-dist"><i class="fa-solid fa-location-dot" aria-hidden="true"></i> ${distLabel}</p>`
              : `<p class="dest-modern-dist muted">Distance unavailable</p>`
          }
          <p class="dest-modern-meta">
            <span>${this.escapeHtml(category)}${placeHint ? ` · ${this.escapeHtml(placeHint)}` : ""}</span>
          </p>
          <p class="dest-modern-hours">
            <i class="fa-regular fa-clock" aria-hidden="true"></i>
            <span class="dest-open-chip ${openClass}">${openLabel}</span>
            <span>${hours}</span>
          </p>
          <div class="dest-modern-footer">
            ${alert}
            <span class="dest-view-link">View details <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
          </div>
        </div>
      </article>
    `;
  },

  bindCardClicks(root) {
    root?.querySelectorAll(".dest-modern-card").forEach((card) => {
      const go = () => {
        const id = Number(card.dataset.destId);
        if (id && typeof window.selectDestinationById === "function") {
          window.selectDestinationById(id);
        }
      };
      card.addEventListener("click", go);
      card.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          go();
        }
      });
    });
  },

  render(destinations) {
    this.init();
    this._lastDests = destinations || [];
    this.updateLocationBanner();

    const enriched = this.attachDistances(this._lastDests);
    const hasLoc = this.hasUserLocation();
    const nearbyGrid = document.getElementById("destNearbyGrid");
    const otherGrid = document.getElementById("destinationsGrid");
    const nearbySection = document.getElementById("destNearbySection");
    const otherTitle = document.getElementById("destOtherTitle");
    const otherHint = document.getElementById("destOtherHint");
    const viewAllBtn = document.getElementById("btnViewAllNearby");

    if (!otherGrid) return;

    if (!enriched.length) {
      if (nearbySection) nearbySection.hidden = true;
      otherGrid.innerHTML = `
        <div class="dest-empty-state">
          <i class="fa-solid fa-map-location-dot" aria-hidden="true"></i>
          <p>No destinations match your filters.</p>
        </div>`;
      return;
    }

    // Sort nearby by distance
    const withCoords = enriched.filter((d) => d.lat != null && d.lng != null);
    const radiusKm = this.nearbyRadiusKm || this.NEARBY_RADIUS_KM;
    const nearbyAll = hasLoc
      ? withCoords
          .filter((d) => d._distanceKm != null && d._distanceKm <= radiusKm)
          .sort((a, b) => a._distanceKm - b._distanceKm)
      : [];

    const nearbyIds = new Set(nearbyAll.map((d) => d.id));
    let nearbyShow = nearbyAll;
    if (!this.showAllNearby && nearbyAll.length > this.NEARBY_PREVIEW) {
      nearbyShow = nearbyAll.slice(0, this.NEARBY_PREVIEW);
    }

    const useNearMode = this.mode === "near" && hasLoc;

    if (useNearMode) {
      if (nearbySection) {
        nearbySection.hidden = false;
        nearbySection.classList.remove("dest-panel-hidden");
      }
      if (nearbyGrid) {
        if (nearbyShow.length) {
          nearbyGrid.innerHTML = nearbyShow.map((d) => this.buildCard(d)).join("");
          this.bindCardClicks(nearbyGrid);
        } else {
          nearbyGrid.innerHTML = `
            <div class="dest-empty-state compact">
              <p>No nearby destinations found within ${radiusKm} km.</p>
              <p class="muted">Here are other destinations you can explore.</p>
            </div>`;
        }
      }
      if (viewAllBtn) {
        const previewTruncated = nearbyAll.length > this.NEARBY_PREVIEW && !this.showAllNearby;
        const canWiden =
          this.nearbyRadiusKm < this.NEARBY_EXPANDED_RADIUS_KM &&
          withCoords.some(
            (d) =>
              d._distanceKm != null &&
              d._distanceKm > radiusKm &&
              d._distanceKm <= this.NEARBY_EXPANDED_RADIUS_KM
          );
        const canShowAll =
          this.nearbyRadiusKm >= this.NEARBY_EXPANDED_RADIUS_KM &&
          enriched.some((d) => !nearbyIds.has(d.id));
        const more = previewTruncated || canWiden || canShowAll;
        viewAllBtn.hidden = !more;
        viewAllBtn.classList.toggle("dest-panel-hidden", !more);
        if (previewTruncated) {
          viewAllBtn.innerHTML = `View all nearby (${nearbyAll.length}) <i class="fa-solid fa-arrow-right" aria-hidden="true"></i>`;
        } else if (canWiden) {
          viewAllBtn.innerHTML = `Show more nearby <i class="fa-solid fa-arrow-right" aria-hidden="true"></i>`;
        } else if (canShowAll) {
          viewAllBtn.innerHTML = `Browse all destinations <i class="fa-solid fa-arrow-right" aria-hidden="true"></i>`;
        }
      }
      if (otherTitle) otherTitle.textContent = "Other destinations";
      if (otherHint) otherHint.textContent = "Further away or outside your nearby radius";

      const others = enriched
        .filter((d) => !nearbyIds.has(d.id))
        .sort((a, b) => {
          if (a._distanceKm == null && b._distanceKm == null) return 0;
          if (a._distanceKm == null) return 1;
          if (b._distanceKm == null) return -1;
          return a._distanceKm - b._distanceKm;
        });

      otherGrid.innerHTML = others.length
        ? others.map((d) => this.buildCard(d)).join("")
        : `<div class="dest-empty-state compact"><p>All matching destinations are nearby.</p></div>`;
      this.bindCardClicks(otherGrid);
    } else {
      // All destinations mode (or no location)
      if (nearbySection) {
        nearbySection.hidden = true;
        nearbySection.classList.add("dest-panel-hidden");
      }
      if (viewAllBtn) {
        viewAllBtn.hidden = true;
        viewAllBtn.classList.add("dest-panel-hidden");
      }
      if (otherTitle) otherTitle.textContent = hasLoc ? "All destinations" : "Destinations";
      if (otherHint)
        otherHint.textContent = hasLoc
          ? "Sorted by distance from you"
          : "Select any spot for safety ratings, on-site pulse & emergency services";

      let list = [...enriched];
      if (hasLoc) {
        list.sort((a, b) => {
          if (a._distanceKm == null && b._distanceKm == null) return 0;
          if (a._distanceKm == null) return 1;
          if (b._distanceKm == null) return -1;
          return a._distanceKm - b._distanceKm;
        });
      }
      otherGrid.innerHTML = list.map((d) => this.buildCard(d)).join("");
      this.bindCardClicks(otherGrid);
    }

    if (this.view === "map") {
      this.refreshSideMap(enriched);
    }
  },

  ensureSideMap() {
    if (this._sideMap || typeof L === "undefined") return;
    const el = document.getElementById("destinationsSideMap");
    if (!el) return;

    this._sideMap = L.map(el, {
      zoomControl: true,
      attributionControl: true,
      minZoom: 4,
      maxZoom: 16,
    }).setView([22.5, 79.5], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>',
      subdomains: "abc",
      maxZoom: 19,
      className: "safetour-osm-dark",
    }).addTo(this._sideMap);

    this._sideMarkers = L.layerGroup().addTo(this._sideMap);
  },

  refreshSideMap(destinations) {
    this.ensureSideMap();
    if (!this._sideMap || !this._sideMarkers) return;

    this._sideMarkers.clearLayers();
    if (this._userMarker) {
      try {
        this._sideMap.removeLayer(this._userMarker);
      } catch (_) {}
      this._userMarker = null;
    }

    const enriched = this.attachDistances(destinations || this._lastDests);
    const hasLoc = this.hasUserLocation();
    const pos = this.getUserPos();

    let toShow = enriched.filter((d) => d.lat != null && d.lng != null);
    if (this.mode === "near" && hasLoc) {
      const radiusKm = this.nearbyRadiusKm || this.NEARBY_RADIUS_KM;
      const nearby = toShow
        .filter((d) => d._distanceKm != null && d._distanceKm <= radiusKm)
        .sort((a, b) => a._distanceKm - b._distanceKm);
      if (nearby.length) toShow = nearby;
    }

    const bounds = [];
    toShow.forEach((dest) => {
      const tierInfo =
        typeof getTierDetails === "function"
          ? getTierDetails(dest.risk_tier)
          : { cssClass: "safe" };
      const color =
        tierInfo.cssClass === "caution"
          ? "#f97316"
          : tierInfo.cssClass === "moderate"
            ? "#f59e0b"
            : "#10b981";
      const dist = this.formatDistance(dest._distanceKm) || "Distance unavailable";
      const icon = L.divIcon({
        className: "dest-side-marker",
        html: `<div class="dest-side-pin" style="background:${color}">${dest.overall_safety_score}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -16],
      });
      const marker = L.marker([dest.lat, dest.lng], { icon });
      marker.bindPopup(`
        <div class="popup-dest-card">
          <strong style="color:#fff;">${this.escapeHtml(dest.name)}</strong>
          <p style="margin:6px 0 0;font-size:12px;color:#cbd5e1;">
            <i class="fa-solid fa-shield-halved"></i> Safety: ${dest.overall_safety_score}<br>
            <i class="fa-solid fa-location-dot"></i> ${dist}<br>
            ${this.escapeHtml(dest.category || "")}
          </p>
          <button type="button" class="popup-btn-inspect" onclick="window.selectDestinationById(${dest.id})">
            View Details
          </button>
        </div>
      `);
      marker.addTo(this._sideMarkers);
      bounds.push([dest.lat, dest.lng]);
    });

    if (hasLoc && pos) {
      const userIcon = L.divIcon({
        className: "dest-user-marker",
        html: `<div class="dest-you-here" title="You are here"><span></span></div>`,
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });
      this._userMarker = L.marker([pos.lat, pos.lng], { icon: userIcon, zIndexOffset: 1000 })
        .bindPopup("<strong>You are here</strong>")
        .addTo(this._sideMap);
      bounds.push([pos.lat, pos.lng]);

      if (this.mode === "near") {
        this._sideMap.setView([pos.lat, pos.lng], 11);
      }
    }

    if (bounds.length > 1 && !(this.mode === "near" && hasLoc)) {
      try {
        this._sideMap.fitBounds(bounds, { padding: [28, 28], maxZoom: 12 });
      } catch (_) {}
    } else if (bounds.length === 1) {
      this._sideMap.setView(bounds[0], 10);
    }

    setTimeout(() => {
      try {
        this._sideMap.invalidateSize();
      } catch (_) {}
    }, 80);
  },
};

window.DestinationsPanel = DestinationsPanel;

document.addEventListener("DOMContentLoaded", () => {
  DestinationsPanel.init();
});
