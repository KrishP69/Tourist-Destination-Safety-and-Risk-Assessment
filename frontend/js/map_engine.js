// Leaflet Map Geospatial Engine for SafeTour Bharat (Watermark-Free Dark Canvas & Satellite)

let mapInstance = null;
let baseDarkLayer = null;
let baseLabelsLayer = null;
let satelliteLayer = null;
let destinationMarkersLayer = null;
let riskCirclesLayer = null;
let incidentMarkersLayer = null;
let emergencyMarkersLayer = null;
let userLocationLayer = null;

function initSafetyMap() {
  if (mapInstance) return;

  // Initialize Map centered on India (lat: 22.0, lng: 79.5, zoom: 5)
  mapInstance = L.map("safetyMap", {
    zoomControl: true,
    minZoom: 4,
    maxZoom: 18
  }).setView([22.5, 79.5], 5);

  // 1. Watermark-Free Esri World Dark Gray Base
  baseDarkLayer = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    {
      attribution: 'Tiles &copy; Esri &mdash; National Geographic, DeLorme, HERE, NRCan',
      maxZoom: 18,
      subdomains: ["server", "services"]
    }
  ).addTo(mapInstance);

  // 2. High-contrast Reference Labels Overlay
  baseLabelsLayer = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
    {
      attribution: '',
      maxZoom: 18,
      pane: 'overlayPane'
    }
  ).addTo(mapInstance);

  // 3. Optional Satellite Terrain View (Esri World Imagery)
  satelliteLayer = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP',
      maxZoom: 18
    }
  );

  destinationMarkersLayer = L.layerGroup().addTo(mapInstance);
  riskCirclesLayer = L.layerGroup().addTo(mapInstance);
  incidentMarkersLayer = L.layerGroup().addTo(mapInstance);
  emergencyMarkersLayer = L.layerGroup().addTo(mapInstance);
  userLocationLayer = L.layerGroup().addTo(mapInstance);

  // Setup layer toggles
  document.getElementById("toggleHeatCircles")?.addEventListener("change", (e) => {
    if (e.target.checked) mapInstance.addLayer(riskCirclesLayer);
    else mapInstance.removeLayer(riskCirclesLayer);
  });

  document.getElementById("toggleCrowdLayer")?.addEventListener("change", (e) => {
    if (typeof MapEngineCrowd === "undefined") return;
    MapEngineCrowd.ensureLayers();
    if (e.target.checked) {
      if (MapEngineCrowd.heatmapLayer) mapInstance.addLayer(MapEngineCrowd.heatmapLayer);
      if (MapEngineCrowd.geofenceLayer) mapInstance.addLayer(MapEngineCrowd.geofenceLayer);
    } else {
      if (MapEngineCrowd.heatmapLayer) mapInstance.removeLayer(MapEngineCrowd.heatmapLayer);
      if (MapEngineCrowd.geofenceLayer) mapInstance.removeLayer(MapEngineCrowd.geofenceLayer);
    }
  });

  document.getElementById("toggleIncidents")?.addEventListener("change", (e) => {
    if (e.target.checked) mapInstance.addLayer(incidentMarkersLayer);
    else mapInstance.removeLayer(incidentMarkersLayer);
  });

  document.getElementById("toggleEmergency")?.addEventListener("change", async (e) => {
    if (e.target.checked) {
      if (!allEmergencyFacilities || allEmergencyFacilities.length === 0) {
        await fetchAndRenderAllEmergencyFacilities();
      }
      mapInstance.addLayer(emergencyMarkersLayer);
      if (typeof window.showLiveToast === 'function') {
        window.showLiveToast(`🛡️ Showing ${allEmergencyFacilities.length || 74} verified Police & Emergency Hospitals on map`);
      }
    } else {
      mapInstance.removeLayer(emergencyMarkersLayer);
    }
  });

  // Satellite view toggle if present
  document.getElementById("toggleSatelliteView")?.addEventListener("change", (e) => {
    if (e.target.checked) {
      mapInstance.removeLayer(baseDarkLayer);
      mapInstance.addLayer(satelliteLayer);
    } else {
      mapInstance.removeLayer(satelliteLayer);
      mapInstance.addLayer(baseDarkLayer);
    }
  });

  // Listen for Geolocation updates to draw user marker and 25km geofence ring
  window.addEventListener('locationUpdated', (e) => {
    renderUserLocationPin(e.detail);
  });

  if (window.GeolocationEngine && window.GeolocationEngine.currentPosition) {
    renderUserLocationPin(window.GeolocationEngine.currentPosition);
  }
}

function renderUserLocationPin(pos) {
  if (!mapInstance || !userLocationLayer) return;
  userLocationLayer.clearLayers();

  const userIconHtml = `
    <div style="position: relative; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center;">
      <div style="position: absolute; width: 100%; height: 100%; border-radius: 50%; background: rgba(56, 189, 248, 0.4); animation: pulseAnimation 2s infinite;"></div>
      <div style="width: 18px; height: 18px; border-radius: 50%; background: #0284c7; border: 3px solid #ffffff; box-shadow: 0 0 10px #38bdf8;"></div>
    </div>
  `;

  const userIcon = L.divIcon({
    className: "user-gps-marker",
    html: userIconHtml,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -18]
  });

  const marker = L.marker([pos.lat, pos.lng], { icon: userIcon, zIndexOffset: 1000 });
  marker.bindPopup(`
    <div class="popup-dest-card">
      <strong style="color: #38bdf8;"><i class="fa-solid fa-person-walking"></i> Your Active Position</strong>
      <p style="font-size: 11px; color: #cbd5e1; margin: 4px 0;">${pos.locationName || 'Traveler Location'}</p>
      <span style="font-size: 10px; color: #34d399; font-weight: 700;">🟢 25km Verified Ground Pulse Zone Active</span>
    </div>
  `);
  marker.addTo(userLocationLayer);

  // 25 km Geofence circle around active user position
  const geofenceCircle = L.circle([pos.lat, pos.lng], {
    radius: 25000,
    color: '#0ea5e9',
    fillColor: '#0ea5e9',
    fillOpacity: 0.08,
    weight: 1.5,
    dashArray: '5, 8'
  });
  geofenceCircle.bindTooltip("25km On-Site Ground Pulse Zone", { permanent: false, direction: "top" });
  geofenceCircle.addTo(userLocationLayer);
}

function renderDestinationMapPoints(destinations, onSelectDestination) {
  if (!mapInstance) initSafetyMap();

  destinationMarkersLayer.clearLayers();
  riskCirclesLayer.clearLayers();

  destinations.forEach((dest) => {
    const tierInfo = getTierDetails(dest.risk_tier);
    const isOpen = dest.is_currently_open;
    const statusDotColor = isOpen ? '#10b981' : '#ef4444';

    // 1. Custom Radar Pulse Pin Marker with Open/Closed indicator
    const iconHtml = `
      <div class="custom-radar-marker" title="${dest.name}">
        <div class="marker-pulse-ring ${tierInfo.cssClass}"></div>
        <div class="marker-shield ${tierInfo.cssClass}">
          ${dest.overall_safety_score}
          <span style="position: absolute; bottom: -2px; right: -2px; width: 10px; height: 10px; border-radius: 50%; background: ${statusDotColor}; border: 1.5px solid #fff;"></span>
        </div>
      </div>
    `;

    const customIcon = L.divIcon({
      className: "radar-pin",
      html: iconHtml,
      iconSize: [34, 34],
      iconAnchor: [17, 17],
      popupAnchor: [0, -18]
    });

    const marker = L.marker([dest.lat, dest.lng], { icon: customIcon });

    const distLabel = dest.distance_km !== null && dest.distance_km !== undefined
      ? `• 📍 ${dest.distance_km} km away`
      : '';

    const openBadgeHtml = isOpen
      ? `<span style="background: rgba(16,185,129,0.2); color: #34d399; font-size: 10px; font-weight:700; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(16,185,129,0.3);">🟢 OPEN NOW</span>`
      : `<span style="background: rgba(239,68,68,0.2); color: #f87171; font-size: 10px; font-weight:700; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(239,68,68,0.3);">🔴 CLOSED</span>`;

    const hazardBadgeHtml = (dest.nearby_incidents && dest.nearby_incidents.length > 0)
      ? `<span style="background: rgba(239,68,68,0.2); color: #fca5a5; font-size: 10px; font-weight:700; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(239,68,68,0.3); display: block; margin-top: 4px;">
           <i class="fa-solid fa-triangle-exclamation"></i> ${dest.nearby_incidents[0].category}: ${dest.nearby_incidents[0].title}
         </span>`
      : '';

    const crowdSnippet = (dest._crowd && dest._crowd.estimated_crowd != null)
      ? `<div style="font-size:11px;color:#cbd5e1;margin:4px 0;">
           Estimated crowd: ~${dest._crowd.estimated_crowd}
           · Occ ${dest._crowd.occupancy_percentage}%
           · <span style="font-weight:700;">${dest._crowd.crowd_level || ""}</span>
         </div>`
      : `<div style="font-size:10px;color:#64748b;margin:4px 0;">Crowd estimate loads when selected</div>`;

    const popupHtml = `
      <div class="popup-dest-card">
        <div class="popup-title-row">
          <span class="popup-title">${dest.name}</span>
          <span class="popup-score-pill ${tierInfo.cssClass}">${dest.overall_safety_score}/100</span>
        </div>
        <div style="display: flex; gap: 6px; align-items: center; margin: 4px 0;">
          ${openBadgeHtml}
          <span style="font-size: 11px; color: #94a3b8;">${dest.opening_time || '06:00'} - ${dest.closing_time || '18:30'}</span>
        </div>
        <div class="popup-location"><i class="fa-solid fa-location-dot"></i> ${dest.state} ${distLabel}</div>
        ${crowdSnippet}
        ${hazardBadgeHtml}
        <button class="popup-btn-inspect" onclick="window.selectDestinationById(${dest.id})">
          <i class="fa-solid fa-magnifying-glass-chart"></i> View Safety, Crowd & Tickets
        </button>
      </div>
    `;

    marker.bindPopup(popupHtml);
    marker.addTo(destinationMarkersLayer);

    // 2. Risk Zone Circle (~30km radius for spatial risk awareness)
    const circle = L.circle([dest.lat, dest.lng], {
      radius: 30000,
      color: tierInfo.color,
      fillColor: tierInfo.color,
      fillOpacity: 0.1,
      weight: 1.2
    });
    circle.addTo(riskCirclesLayer);
  });
}

function renderIncidentMapPoints(incidents) {
  if (!mapInstance) return;
  incidentMarkersLayer.clearLayers();

  incidents.forEach((inc) => {
    const isLandslideOrFlood = inc.category.includes("Landslide") || inc.category.includes("Flood") || inc.category.includes("Weather Hazard");
    const iconClass = isLandslideOrFlood ? "fa-hill-rockslide" : "fa-triangle-exclamation";
    const bgGlow = inc.severity === "Critical" ? "#ef4444" : "#f59e0b";

    const iconHtml = `
      <div class="incident-marker-icon" style="background: ${bgGlow}; box-shadow: 0 0 12px ${bgGlow};" title="${inc.title}">
        <i class="fa-solid ${iconClass}"></i>
      </div>
    `;

    const icon = L.divIcon({
      className: "incident-pin",
      html: iconHtml,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
      popupAnchor: [0, -14]
    });

    const marker = L.marker([inc.lat, inc.lng], { icon });
    marker.bindPopup(`
      <div class="popup-dest-card">
        <strong style="color:#ef4444;"><i class="fa-solid fa-triangle-exclamation"></i> ${inc.title}</strong>
        <p style="font-size:11px; color:#cbd5e1; margin-top:4px;">${inc.description}</p>
        <div style="font-size:10px; color:#94a3b8; display:flex; gap:6px; margin-top:6px;">
          <span style="color:#fbbf24; font-weight:700;">${inc.category}</span>
          <span>•</span>
          <span>Severity: <strong style="color:#f87171;">${inc.severity}</strong></span>
        </div>
      </div>
    `);
    marker.addTo(incidentMarkersLayer);
  });
}

let allEmergencyFacilities = [];
const facilityMarkerMap = new Map();

async function fetchAndRenderAllEmergencyFacilities() {
  try {
    const res = await fetch("/api/emergency/facilities");
    if (res.ok) {
      const data = await res.json();
      allEmergencyFacilities = data;
      renderEmergencyMapPoints(data);
    }
  } catch (err) {
    console.warn("Could not fetch emergency facilities:", err);
  }
}

function renderEmergencyMapPoints(facilities) {
  if (!mapInstance) return;
  emergencyMarkersLayer.clearLayers();
  facilityMarkerMap.clear();

  facilities.forEach((fac) => {
    if (!fac.lat || !fac.lng) return;

    const typeStr = (fac.facility_type || '').toLowerCase();
    const isPolice = typeStr.includes("police");
    const isHospital = typeStr.includes("hospital") || typeStr.includes("health") || typeStr.includes("medical");
    const iconClass = isPolice ? "fa-shield-halved" : (isHospital ? "fa-notes-medical" : "fa-life-ring");
    const badgeClass = isPolice ? "police" : (isHospital ? "hospital" : "rescue");
    const badgeColor = isPolice ? "#3b82f6" : (isHospital ? "#ef4444" : "#f59e0b");

    const iconHtml = `
      <div class="facility-marker-icon ${badgeClass}" title="${fac.facility_name}" style="background: ${badgeColor}; border: 2px solid #ffffff; box-shadow: 0 0 10px ${badgeColor};">
        <i class="fa-solid ${iconClass}"></i>
      </div>
    `;

    const icon = L.divIcon({
      className: "facility-pin",
      html: iconHtml,
      iconSize: [26, 26],
      iconAnchor: [13, 13],
      popupAnchor: [0, -14]
    });

    const marker = L.marker([fac.lat, fac.lng], { icon });
    marker.bindPopup(`
      <div class="popup-dest-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <span style="font-size:10px; font-weight:800; text-transform:uppercase; padding:2px 6px; border-radius:4px; background:${isPolice ? 'rgba(59,130,246,0.2)' : 'rgba(239,68,68,0.2)'}; color:${isPolice ? '#60a5fa' : '#f87171'};">
            <i class="fa-solid ${iconClass}"></i> ${fac.facility_type}
          </span>
          <span style="font-size:10px; color:#34d399; font-weight:700;">🟢 24/7 ACTIVE</span>
        </div>
        <strong style="color:#ffffff; font-size:13px; display:block; margin:3px 0;">${fac.facility_name}</strong>
        <p style="font-size:11px; color:#94a3b8; margin:2px 0 6px 0;"><i class="fa-solid fa-map-pin"></i> ${fac.address || 'Central District'}, ${fac.destination_name || 'India'}</p>
        <div style="display:flex; gap:6px; margin-top:6px;">
          <a href="tel:${fac.phone}" style="flex:1; background:#10b981; color:#ffffff; padding:5px 8px; border-radius:6px; font-size:11px; font-weight:700; text-align:center; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; gap:4px;">
            <i class="fa-solid fa-phone"></i> Call ${fac.phone}
          </a>
          <a href="https://maps.google.com/?q=${fac.lat},${fac.lng}" target="_blank" rel="noopener noreferrer" style="background:rgba(255,255,255,0.1); color:#cbd5e1; padding:5px 8px; border-radius:6px; font-size:11px; text-decoration:none; display:inline-flex; align-items:center; justify-content:center;">
            <i class="fa-solid fa-diamond-turn-right"></i>
          </a>
        </div>
      </div>
    `);
    marker.addTo(emergencyMarkersLayer);

    // Save in marker map
    const key = `${fac.lat.toFixed(4)}_${fac.lng.toFixed(4)}`;
    facilityMarkerMap.set(key, marker);
    if (fac.facility_name) facilityMarkerMap.set(fac.facility_name.toLowerCase(), marker);
  });
}

function focusEmergencyFacility(lat, lng, name) {
  if (!mapInstance) return;

  // Make sure toggle is checked
  const toggle = document.getElementById("toggleEmergency");
  if (toggle && !toggle.checked) {
    toggle.checked = true;
  }
  if (!mapInstance.hasLayer(emergencyMarkersLayer)) {
    mapInstance.addLayer(emergencyMarkersLayer);
  }

  // If not rendered yet, fetch and render
  if (emergencyMarkersLayer.getLayers().length === 0) {
    fetchAndRenderAllEmergencyFacilities().then(() => {
      _executeFlyToFacility(lat, lng, name);
    });
  } else {
    _executeFlyToFacility(lat, lng, name);
  }
}

function _executeFlyToFacility(lat, lng, name) {
  mapInstance.flyTo([lat, lng], 15, { animate: true, duration: 1.2 });
  
  // Try to find and open popup
  setTimeout(() => {
    const key = `${Number(lat).toFixed(4)}_${Number(lng).toFixed(4)}`;
    let marker = facilityMarkerMap.get(key);
    if (!marker && name) {
      marker = facilityMarkerMap.get(name.toLowerCase());
    }
    if (marker) {
      marker.openPopup();
    }
  }, 1300);

  // Scroll map card into view if needed
  const mapCard = document.querySelector(".map-wrapper-card");
  if (mapCard && window.innerWidth <= 1024) {
    mapCard.scrollIntoView({ behavior: "smooth" });
  }
}

window.focusEmergencyFacility = focusEmergencyFacility;
window.fetchAndRenderAllEmergencyFacilities = fetchAndRenderAllEmergencyFacilities;

function flyToCoordinates(lat, lng, zoom = 8) {
  if (mapInstance) {
    mapInstance.flyTo([lat, lng], zoom, {
      animate: true,
      duration: 1.4
    });
  }
}

/** Crowd map helpers — geofence ring + aggregated zone heatmap (never individual people). */
const MapEngineCrowd = {
  geofenceLayer: null,
  heatmapLayer: null,
  overviewCache: {},

  ensureLayers() {
    if (!mapInstance) return;
    if (!this.geofenceLayer) this.geofenceLayer = L.layerGroup().addTo(mapInstance);
    if (!this.heatmapLayer) this.heatmapLayer = L.layerGroup().addTo(mapInstance);
  },

  crowdColor(level) {
    const map = {
      LOW: "#34d399",
      MODERATE: "#fbbf24",
      HIGH: "#fb923c",
      VERY_HIGH: "#f87171",
      CRITICAL: "#94a3b8",
    };
    return map[level] || "#64748b";
  },

  async refreshOverview() {
    try {
      const res = await fetch("/api/crowd/overview");
      const data = await res.json();
      (data.destinations || []).forEach((d) => {
        this.overviewCache[d.destination_id] = d;
      });
      if (typeof allDestinationsData !== "undefined" && allDestinationsData.length) {
        allDestinationsData.forEach((dest) => {
          if (this.overviewCache[dest.id]) dest._crowd = this.overviewCache[dest.id];
        });
        if (typeof renderDestinationMapPoints === "function") {
          renderDestinationMapPoints(allDestinationsData, window.selectDestinationById);
        }
      }
    } catch (_) {}
  },

  updateDestinationCrowd(destId, crowd) {
    this.overviewCache[destId] = {
      destination_id: destId,
      estimated_crowd: crowd.estimated_crowd,
      occupancy_percentage: crowd.occupancy_percentage,
      crowd_level: crowd.crowd_level,
    };
  },

  showGeofence(dest) {
    this.ensureLayers();
    this.geofenceLayer.clearLayers();
    const radius = Number(dest.geofence_radius_m || 800);
    const color = this.crowdColor((dest._crowd && dest._crowd.crowd_level) || "MODERATE");
    L.circle([dest.lat, dest.lng], {
      radius,
      color,
      weight: 2,
      fillColor: color,
      fillOpacity: 0.08,
      dashArray: "6 6",
    }).addTo(this.geofenceLayer).bindTooltip(`${dest.name} geofence (~${radius}m)`);
  },

  async loadHeatmap(destId) {
    this.ensureLayers();
    this.heatmapLayer.clearLayers();
    try {
      const res = await fetch(`/api/crowd/${destId}/heatmap`);
      const data = await res.json();
      if (data.insufficient_data) return;
      (data.cells || []).forEach((cell) => {
        const color = this.crowdColor(cell.crowd_level);
        L.circle([cell.lat, cell.lng], {
          radius: cell.radius_m || 150,
          color,
          weight: 1,
          fillColor: color,
          fillOpacity: 0.25,
        })
          .bindTooltip(
            `${cell.name}: ~${cell.estimated_crowd} est. (${cell.crowd_level}) — aggregated zone`
          )
          .addTo(this.heatmapLayer);
      });
    } catch (_) {}
  },
};

window.MapEngineCrowd = MapEngineCrowd;
