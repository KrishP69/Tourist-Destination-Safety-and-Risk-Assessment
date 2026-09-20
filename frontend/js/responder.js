// Emergency Services Command Center (EOC) Controller — SafeTour Bharat
// Multi-Department Emergency Operations Body Management (Police, Hospitals, Fire & NDRF)

let eocMap = null;
let incidentRadarLayer = null;
let facilitiesRadarLayer = null;
let baseDarkLayer = null;
let satelliteLayer = null;
let activeAgencyFilter = "All";
let currentIncidents = [];
let allDirectoryStations = [];
let allDestinationsList = [];
let currentOfficerProfile = null;
let telemetryInterval = null;

document.addEventListener("DOMContentLoaded", async () => {
  setupLoginGate();
  setupNavigationModes();
  setupAgencyTabs();
  setupAddStationModal();
  setupAdvisoryBroadcastForm();

  // Check authentication session on page load
  await verifyOfficerSession();
});

// =========================================================================
// 1. OFFICER AUTHENTICATION & GATEKEEPER
// =========================================================================

function setupLoginGate() {
  const loginForm = document.getElementById("eocLoginForm");
  const deptPills = document.querySelectorAll(".dept-pill");

  // Department pill selection
  deptPills.forEach(pill => {
    pill.addEventListener("click", () => {
      deptPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");

      const demoId = pill.dataset.demoId;
      const demoPwd = pill.dataset.demoPwd;
      if (demoId && demoPwd) {
        document.getElementById("eocOfficerId").value = demoId;
        document.getElementById("eocPassword").value = demoPwd;
      }
    });
  });

  // Login form submission
  loginForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const loginId = document.getElementById("eocOfficerId").value.trim();
    const password = document.getElementById("eocPassword").value.trim();
    const activePill = document.querySelector(".dept-pill.active");
    const agency = activePill ? activePill.dataset.dept : "All";
    const errorEl = document.getElementById("eocLoginError");
    const errorMsgEl = document.getElementById("eocLoginErrorMsg");
    const btnSubmit = document.getElementById("btnSubmitEocLogin");

    errorEl.style.display = "none";
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Authenticating...';

    try {
      const res = await fetch("/api/emergency/responder/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login_id: loginId, password: password, agency: agency })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        localStorage.setItem("responderOfficerToken", data.access_token);
        localStorage.setItem("responderOfficerProfile", JSON.stringify(data.officer));
        
        applyOfficerSession(data.officer);
        showEocToast(`🛡️ ${data.message}`);
      } else {
        errorEl.style.display = "flex";
        errorMsgEl.innerText = data.detail || "Authentication failed. Verify credentials.";
      }
    } catch (err) {
      errorEl.style.display = "flex";
      errorMsgEl.innerText = "Network failure while verifying credentials: " + err.message;
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = '<i class="fa-solid fa-shield-check"></i> Authenticate & Enter Command Center';
    }
  });

  // Logout button
  document.getElementById("eocLogoutBtn")?.addEventListener("click", () => {
    if (confirm("Confirm signing out of the Emergency Services Command Center?")) {
      logoutOfficer();
    }
  });
}

window.fillDemoOfficer = function(loginId, pwd, agency) {
  document.getElementById("eocOfficerId").value = loginId;
  document.getElementById("eocPassword").value = pwd;
  document.querySelectorAll(".dept-pill").forEach(p => {
    if (p.dataset.dept === agency) p.classList.add("active");
    else p.classList.remove("active");
  });
  // Auto-trigger submit
  document.getElementById("eocLoginForm")?.dispatchEvent(new Event("submit"));
};

async function verifyOfficerSession() {
  const token = localStorage.getItem("responderOfficerToken");
  if (!token) {
    showLoginScreen();
    return;
  }

  try {
    const res = await fetch("/api/emergency/responder/me", {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (res.ok) {
      const data = await res.json();
      applyOfficerSession(data.officer);
    } else {
      logoutOfficer(false);
    }
  } catch (err) {
    console.warn("Session check offline, checking local cached profile:", err);
    const cached = localStorage.getItem("responderOfficerProfile");
    if (cached) {
      applyOfficerSession(JSON.parse(cached));
    } else {
      showLoginScreen();
    }
  }
}

function applyOfficerSession(officer) {
  currentOfficerProfile = officer;
  document.getElementById("eocLoginGate").style.display = "none";
  document.getElementById("eocMainApp").style.display = "block";

  // Update header profile
  document.getElementById("officerDisplayName").innerText = officer.full_name;
  document.getElementById("officerCallsign").innerText = officer.callsign;
  document.getElementById("officerClearance").innerText = officer.clearance_level || "TIER-1";
  document.getElementById("eocDepartmentName").innerText = officer.department || "Emergency Operations Body";

  // Agency badge pill color
  const pill = document.getElementById("officerAgencyPill");
  const emblem = document.getElementById("eocActiveEmblem");
  const agencyLower = (officer.agency || "All").toLowerCase();

  if (agencyLower.includes("police")) {
    pill.className = "agency-status-pill police";
    pill.innerHTML = '<span class="live-dot" style="background: #38bdf8;"></span> POLICE 112';
    emblem.style.background = "linear-gradient(135deg, #0284c7, #0369a1)";
  } else if (agencyLower.includes("ambulance") || agencyLower.includes("medical")) {
    pill.className = "agency-status-pill medical";
    pill.innerHTML = '<span class="live-dot" style="background: #f472b6;"></span> EMS & HOSPITALS 108';
    emblem.style.background = "linear-gradient(135deg, #e11d48, #be123c)";
  } else if (agencyLower.includes("fire")) {
    pill.className = "agency-status-pill fire";
    pill.innerHTML = '<span class="live-dot" style="background: #fb923c;"></span> FIRE & RESCUE 101';
    emblem.style.background = "linear-gradient(135deg, #ea580c, #c2410c)";
  } else if (agencyLower.includes("ndrf")) {
    pill.className = "agency-status-pill ndrf";
    pill.innerHTML = '<span class="live-dot" style="background: #c084fc;"></span> NDRF DISASTER';
    emblem.style.background = "linear-gradient(135deg, #9333ea, #7e22ce)";
  } else {
    pill.className = "agency-status-pill unified";
    pill.innerHTML = '<span class="live-dot" style="background: #10b981;"></span> UNIFIED ALL-DEPTS';
    emblem.style.background = "linear-gradient(135deg, #059669, #047857)";
  }

  // Set default agency tab filter to match officer's agency
  if (officer.agency && officer.agency !== "All") {
    activeAgencyFilter = officer.agency;
    document.querySelectorAll(".agency-tab").forEach(tab => {
      if (tab.dataset.agency.toLowerCase().includes(officer.agency.toLowerCase())) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });
  }

  // Initialize operational workspace
  initRadarMap();
  loadEocTelemetry();
  loadEocFacilities();
  loadDestinationsForAdvisories();

  // Setup periodic refresh
  if (telemetryInterval) clearInterval(telemetryInterval);
  telemetryInterval = setInterval(() => {
    loadEocTelemetry(true);
  }, 5000);

  document.getElementById("eocRefreshBtn")?.addEventListener("click", () => {
    loadEocTelemetry();
    loadEocFacilities();
    showEocToast("⚡ Emergency telemetry and stations directory refreshed.");
  });
}

function showLoginScreen() {
  document.getElementById("eocLoginGate").style.display = "flex";
  document.getElementById("eocMainApp").style.display = "none";
  if (telemetryInterval) clearInterval(telemetryInterval);
}

function logoutOfficer(notify = true) {
  localStorage.removeItem("responderOfficerToken");
  localStorage.removeItem("responderOfficerProfile");
  currentOfficerProfile = null;
  showLoginScreen();
  if (notify) showEocToast("🔒 Officer terminal signed out successfully.");
}

function showEocToast(msg) {
  const toast = document.getElementById("eocLiveToast");
  const msgEl = document.getElementById("eocToastMsg");
  if (!toast || !msgEl) return;
  msgEl.innerText = msg;
  toast.style.display = "flex";
  setTimeout(() => { toast.style.display = "none"; }, 4000);
}

// =========================================================================
// 2. OPERATIONAL MODE NAVIGATION
// =========================================================================

function setupNavigationModes() {
  const modeButtons = document.querySelectorAll(".btn-mode-tab");
  const viewSections = document.querySelectorAll(".view-section");
  const agencyFilterStrip = document.getElementById("agencyFilterStrip");

  modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      modeButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const viewId = btn.dataset.view;
      viewSections.forEach(sec => sec.style.display = "none");

      if (viewId === "dispatchQueue") {
        document.getElementById("viewDispatchQueue").style.display = "grid";
        agencyFilterStrip.style.display = "block";
        if (eocMap) eocMap.invalidateSize();
      } else if (viewId === "stationsDirectory") {
        document.getElementById("viewStationsDirectory").style.display = "grid";
        agencyFilterStrip.style.display = "none";
        renderStationsDirectory(allDirectoryStations);
      } else if (viewId === "broadcastAdvisories") {
        document.getElementById("viewBroadcastAdvisories").style.display = "grid";
        agencyFilterStrip.style.display = "none";
      }
    });
  });

  // Filter tabs for Stations Directory
  const stationTabs = document.querySelectorAll(".station-tab");
  stationTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      stationTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      filterStationsList();
    });
  });

  // Search input for Stations
  document.getElementById("searchStationsInput")?.addEventListener("input", () => {
    filterStationsList();
  });
}

function filterStationsList() {
  const activeTab = document.querySelector(".station-tab.active")?.dataset.type || "All";
  const search = (document.getElementById("searchStationsInput")?.value || "").toLowerCase().trim();

  let filtered = allDirectoryStations;
  if (activeTab !== "All") {
    filtered = filtered.filter(s => (s.facility_type || '').toLowerCase().includes(activeTab.toLowerCase()));
  }

  if (search) {
    filtered = filtered.filter(s => 
      (s.facility_name || '').toLowerCase().includes(search) ||
      (s.destination_name || '').toLowerCase().includes(search) ||
      (s.address || '').toLowerCase().includes(search) ||
      (s.phone || '').includes(search)
    );
  }

  renderStationsDirectory(filtered);
}

// =========================================================================
// 3. TACTICAL RADAR MAP & INCIDENTS
// =========================================================================

function initRadarMap() {
  const mapEl = document.getElementById("eocRadarMap");
  if (!mapEl || eocMap) return;

  eocMap = L.map("eocRadarMap", {
    center: [22.5937, 78.9629],
    zoom: 5,
    minZoom: 4,
    maxZoom: 18
  });

  baseDarkLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 16,
    attribution: "&copy; Esri, HERE, Garmin"
  }).addTo(eocMap);

  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 16,
    zIndex: 400
  }).addTo(eocMap);

  satelliteLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 18,
    attribution: "&copy; Esri, Maxar"
  });

  document.getElementById("eocToggleSatellite")?.addEventListener("change", (e) => {
    if (e.target.checked) {
      eocMap.removeLayer(baseDarkLayer);
      eocMap.addLayer(satelliteLayer);
    } else {
      eocMap.removeLayer(satelliteLayer);
      eocMap.addLayer(baseDarkLayer);
    }
  });

  incidentRadarLayer = L.layerGroup().addTo(eocMap);
  facilitiesRadarLayer = L.layerGroup().addTo(eocMap);
}

async function loadEocTelemetry(isSilent = false) {
  try {
    const [feedRes, kpiRes] = await Promise.all([
      fetch(`/api/emergency/responder/feed?agency=${encodeURIComponent(activeAgencyFilter)}`),
      fetch("/api/emergency/responder/kpis")
    ]);

    currentIncidents = await feedRes.json();
    const kpis = await kpiRes.json();

    document.getElementById("kpiDistressCount").innerText = kpis.active_distress_calls || 0;
    document.getElementById("kpiActiveUnitsCount").innerText = kpis.active_units_deployed || 0;
    document.getElementById("kpiAvgEta").innerText = `${kpis.average_response_eta_minutes || 4.5}m`;
    document.getElementById("kpiResolvedCount").innerText = kpis.incidents_resolved || 0;
    document.getElementById("eocQueueCount").innerText = currentIncidents.length;

    renderIncidentQueue(currentIncidents);
    renderRadarIncidentPins(currentIncidents);
  } catch (err) {
    if (!isSilent) console.error("Error loading EOC telemetry:", err);
  }
}

function renderIncidentQueue(incidents) {
  const container = document.getElementById("eocFeedList");
  if (!container) return;

  if (incidents.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px; color: #64748b;">
        <i class="fa-solid fa-shield-check fa-3x" style="color: #10b981; margin-bottom: 12px;"></i>
        <h4 style="color: #f1f5f9; font-size: 1rem;">No Active Unresolved Emergencies</h4>
        <p style="font-size: 0.8rem; margin-top: 4px;">All regional distress signals in ${activeAgencyFilter} department currently stabilized.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = incidents.map(inc => {
    const sevClass = (inc.severity || "medium").toLowerCase();
    const dispatchStatus = inc.dispatch_status || "PENDING";
    const unitCallsign = inc.unit_callsign || "NO UNIT ASSIGNED";
    const agencyType = inc.agency_type || "General";
    const isResolved = dispatchStatus === "RESOLVED" || inc.incident_status === "Resolved";

    return `
      <div class="eoc-card ${sevClass} ${isResolved ? 'resolved' : ''}" id="eoc-card-${inc.incident_id}">
        <div class="eoc-card-top">
          <div class="eoc-incident-title">
            <i class="fa-solid fa-triangle-exclamation" style="color: ${sevClass === 'critical' ? '#ef4444' : '#f59e0b'};"></i>
            ${inc.title}
          </div>
          <span class="eoc-severity-pill ${sevClass}">${inc.severity}</span>
        </div>

        <div class="eoc-meta-bar">
          <span><i class="fa-solid fa-location-dot"></i> ${inc.destination_name || 'Destination'} (${inc.state_name || 'India'})</span>
          <span>•</span>
          <span><i class="fa-solid fa-layer-group"></i> ${inc.category}</span>
          <span>•</span>
          <span><i class="fa-solid fa-crosshairs"></i> ${inc.lat.toFixed(4)}, ${inc.lng.toFixed(4)}</span>
          <span>•</span>
          <span><i class="fa-regular fa-clock"></i> ${inc.reported_at || 'Just Now'}</span>
        </div>

        <div class="eoc-desc-text">
          ${inc.description}
        </div>

        <!-- Dispatch Status Strip -->
        <div class="eoc-dispatch-strip">
          <div class="eoc-unit-callsign">
            <i class="fa-solid fa-shield"></i>
            <span>${unitCallsign} [${agencyType}]</span>
            ${inc.eta_minutes !== null && inc.eta_minutes !== undefined ? `<span style="font-size:0.75rem; color:#f59e0b;">(ETA: ${inc.eta_minutes}m)</span>` : ''}
          </div>
          <span class="status-pill-dispatch ${dispatchStatus}">${dispatchStatus}</span>
        </div>

        <!-- Act Fast Action Buttons -->
        <div class="eoc-actions-grid">
          ${!isResolved ? `
            <button class="btn-act-fast police" onclick="dispatchUnitPrompt(${inc.incident_id}, 'Police')">
              <i class="fa-solid fa-car-side"></i> Dispatch Police PCR
            </button>
            <button class="btn-act-fast ambulance" onclick="dispatchUnitPrompt(${inc.incident_id}, 'Ambulance')">
              <i class="fa-solid fa-truck-medical"></i> Dispatch ALS Ambulance
            </button>
            <button class="btn-act-fast fire" onclick="dispatchUnitPrompt(${inc.incident_id}, 'Fire & Rescue')">
              <i class="fa-solid fa-fire-extinguisher"></i> Deploy Fire Unit
            </button>
            ${inc.dispatch_id ? `
              <button class="btn-act-fast status-step" onclick="cycleDispatchStatus(${inc.dispatch_id}, '${dispatchStatus}')">
                <i class="fa-solid fa-forward-step"></i> Advance State
              </button>
            ` : ''}
            <button class="btn-act-fast resolve" onclick="markIncidentResolved(${inc.incident_id}, ${inc.dispatch_id || 'null'})">
              <i class="fa-solid fa-check-double"></i> Mark Resolved
            </button>
          ` : `
            <span style="color: #34d399; font-size: 0.8rem; font-weight: 700;">
              <i class="fa-solid fa-circle-check"></i> Case Stabilized & Resolved
            </span>
          `}
          <button class="btn-act-fast status-step" style="margin-left: auto;" onclick="flyToIncident(${inc.lat}, ${inc.lng}, '${inc.title.replace(/'/g, "\\'")}')">
            <i class="fa-solid fa-crosshairs"></i> Radar Lock
          </button>
        </div>
      </div>
    `;
  }).join("");
}

function renderRadarIncidentPins(incidents) {
  if (!eocMap || !incidentRadarLayer) return;
  incidentRadarLayer.clearLayers();

  incidents.forEach(inc => {
    const isCritical = inc.severity === "Critical";
    const color = isCritical ? "#ef4444" : "#f59e0b";

    const pulseHtml = `
      <div style="position: relative; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center;">
        <div style="position: absolute; width: 100%; height: 100%; border-radius: 50%; background: ${isCritical ? 'rgba(239, 68, 68, 0.4)' : 'rgba(245, 158, 11, 0.4)'}; animation: alertBlink 1.5s infinite;"></div>
        <div style="width: 16px; height: 16px; border-radius: 50%; background: ${color}; border: 2px solid #fff; box-shadow: 0 0 12px ${color};"></div>
      </div>
    `;

    const beaconIcon = L.divIcon({
      className: "eoc-beacon-marker",
      html: pulseHtml,
      iconSize: [34, 34],
      iconAnchor: [17, 17],
      popupAnchor: [0, -18]
    });

    const marker = L.marker([inc.lat, inc.lng], { icon: beaconIcon });
    marker.bindPopup(`
      <div style="background: #0f172a; color: #fff; padding: 6px; font-family: 'Inter', sans-serif; min-width: 180px;">
        <strong style="color: ${color}; font-size: 0.88rem;">${inc.title}</strong>
        <p style="font-size: 0.75rem; color: #cbd5e1; margin: 4px 0;">${inc.location_name} • ${inc.destination_name || ''}</p>
        <div style="font-size: 0.72rem; color: #94a3b8;">Severity: <strong style="color:${color}">${inc.severity}</strong></div>
        <div style="font-size: 0.72rem; color: #38bdf8; margin-top: 4px;">Assigned: ${inc.unit_callsign || 'Pending Dispatch'}</div>
      </div>
    `);
    marker.addTo(incidentRadarLayer);

    L.circle([inc.lat, inc.lng], {
      radius: 10000,
      color: color,
      fillColor: color,
      fillOpacity: 0.04,
      weight: 1.2,
      dashArray: "4, 6"
    }).addTo(incidentRadarLayer);
  });
}

// =========================================================================
// 4. DEPARTMENT STATIONS DIRECTORY & MANAGEMENT
// =========================================================================

async function loadEocFacilities() {
  try {
    const res = await fetch("/api/emergency/facilities");
    const facilities = await res.json();
    allDirectoryStations = facilities;

    // Update counts
    document.getElementById("totalStationsCount").innerText = facilities.length;
    document.getElementById("stAllCount").innerText = facilities.length;
    
    const policeCount = facilities.filter(f => (f.facility_type || '').toLowerCase().includes("police")).length;
    const hospCount = facilities.filter(f => (f.facility_type || '').toLowerCase().includes("hospital") || (f.facility_type || '').toLowerCase().includes("health")).length;
    const rescueCount = facilities.filter(f => (f.facility_type || '').toLowerCase().includes("fire") || (f.facility_type || '').toLowerCase().includes("rescue")).length;

    document.getElementById("stPoliceCount").innerText = policeCount;
    document.getElementById("stHospitalCount").innerText = hospCount;
    document.getElementById("stRescueCount").innerText = rescueCount;

    // Render in Directory tab
    renderStationsDirectory(facilities);

    // Render markers on radar map
    if (eocMap && facilitiesRadarLayer) {
      facilitiesRadarLayer.clearLayers();
      facilities.forEach(fac => {
        if (!fac.lat || !fac.lng) return;

        const isPolice = fac.facility_type.toLowerCase().includes("police");
        const isFire = fac.facility_type.toLowerCase().includes("fire");
        const iconClass = isPolice ? "fa-shield-halved" : isFire ? "fa-fire" : "fa-notes-medical";
        const iconColor = isPolice ? "#38bdf8" : isFire ? "#fb923c" : "#f472b6";

        const facHtml = `
          <div style="background: #0f172a; border: 2px solid ${iconColor}; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px ${iconColor}; font-size: 0.75rem; color: ${iconColor};">
            <i class="fa-solid ${iconClass}"></i>
          </div>
        `;

        const facIcon = L.divIcon({
          className: "eoc-facility-marker",
          html: facHtml,
          iconSize: [26, 26],
          iconAnchor: [13, 13]
        });

        const marker = L.marker([fac.lat, fac.lng], { icon: facIcon, zIndexOffset: -100 });
        marker.bindPopup(`
          <div style="background: #0f172a; color: #fff; padding: 4px; font-family: 'Inter', sans-serif;">
            <strong style="color: ${iconColor}; font-size: 0.82rem;">${fac.facility_name}</strong>
            <p style="font-size: 0.72rem; color: #94a3b8; margin: 2px 0;">${fac.facility_type} • ${fac.address || ''}</p>
            <a href="tel:${fac.phone}" style="color: #38bdf8; font-size: 0.75rem; font-weight:700;"><i class="fa-solid fa-phone"></i> ${fac.phone}</a>
          </div>
        `);
        marker.addTo(facilitiesRadarLayer);
      });
    }
  } catch (err) {
    console.error("Failed to load facilities:", err);
  }
}

function renderStationsDirectory(stations) {
  const grid = document.getElementById("eocStationsGrid");
  if (!grid) return;

  if (stations.length === 0) {
    grid.innerHTML = '<div style="color: #94a3b8; padding: 24px; text-align: center; grid-column: 1/-1;">No department stations matching search filter.</div>';
    return;
  }

  grid.innerHTML = stations.map(s => {
    const isPolice = (s.facility_type || '').toLowerCase().includes("police");
    const isFire = (s.facility_type || '').toLowerCase().includes("fire");
    const icon = isPolice ? "fa-shield-halved" : (isFire ? "fa-fire" : "fa-notes-medical");
    const badgeColor = isPolice ? "#38bdf8" : (isFire ? "#fb923c" : "#f472b6");
    const typeClass = isPolice ? "police" : (isFire ? "fire" : "hospital");

    return `
      <div class="station-card ${typeClass}">
        <div class="station-card-top">
          <span class="station-badge" style="color: ${badgeColor}; border: 1px solid ${badgeColor}; background: rgba(255,255,255,0.04);">
            <i class="fa-solid ${icon}"></i> ${s.facility_type}
          </span>
          <span class="station-dest-tag"><i class="fa-solid fa-map-pin"></i> ${s.destination_name || 'India'}</span>
        </div>
        <h4 class="station-name">${s.facility_name}</h4>
        <p class="station-address">${s.address || 'Central District Headquarters'}</p>
        <div class="station-actions">
          <a href="tel:${s.phone}" class="btn-station-phone"><i class="fa-solid fa-phone"></i> ${s.phone}</a>
          <button class="btn-station-locate" onclick="window.locateStationOnMap(${s.lat}, ${s.lng}, '${(s.facility_name || '').replace(/'/g, "\\'")}')">
            <i class="fa-solid fa-crosshairs"></i> View on Radar
          </button>
        </div>
      </div>
    `;
  }).join("");
}

window.locateStationOnMap = function(lat, lng, title) {
  // Switch to radar map tab
  document.querySelector('.btn-mode-tab[data-view="dispatchQueue"]')?.click();
  setTimeout(() => {
    if (eocMap) {
      eocMap.flyTo([lat, lng], 14, { duration: 1.4 });
      showEocToast(`📍 Radar locked on station: ${title}`);
    }
  }, 200);
};

function setupAddStationModal() {
  const modal = document.getElementById("addStationModal");
  const openBtn = document.getElementById("btnOpenAddStationModal");
  const closeBtn = document.getElementById("closeAddStationModal");
  const form = document.getElementById("addStationForm");

  openBtn?.addEventListener("click", () => {
    modal.style.display = "flex";
  });

  closeBtn?.addEventListener("click", () => {
    modal.style.display = "none";
  });

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const destId = parseInt(document.getElementById("modalStationDest").value);
    const name = document.getElementById("modalStationName").value.trim();
    const type = document.getElementById("modalStationType").value;
    const phone = document.getElementById("modalStationPhone").value.trim();
    const address = document.getElementById("modalStationAddress").value.trim();

    // Look up destination lat/lng
    const dest = allDestinationsList.find(d => d.id === destId);
    const lat = dest ? dest.lat : 28.6139;
    const lng = dest ? dest.lng : 77.2090;

    try {
      const res = await fetch("/api/emergency/facilities/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination_id: destId,
          facility_name: name,
          facility_type: type,
          phone: phone,
          address: address,
          lat: lat,
          lng: lng
        })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        showEocToast(`✓ ${data.message}`);
        modal.style.display = "none";
        form.reset();
        await loadEocFacilities();
      } else {
        alert("Registration failed: " + (data.detail || "Server error"));
      }
    } catch (err) {
      alert("Error: " + err.message);
    }
  });
}

// =========================================================================
// 5. BROADCAST OFFICIAL ADVISORIES
// =========================================================================

async function loadDestinationsForAdvisories() {
  try {
    const res = await fetch("/api/destinations");
    const dests = await res.json();
    allDestinationsList = dests;

    // Populate dropdowns
    const advSelect = document.getElementById("advDestinationSelect");
    const modalSelect = document.getElementById("modalStationDest");

    const optionsHtml = dests.map(d => `<option value="${d.id}">${d.name} (${d.state})</option>`).join("");
    if (advSelect) advSelect.innerHTML = optionsHtml;
    if (modalSelect) modalSelect.innerHTML = optionsHtml;

    // Load recent advisories log
    loadRecentAdvisoriesLog();
  } catch (err) {
    console.warn("Could not load destinations list:", err);
  }
}

function setupAdvisoryBroadcastForm() {
  const form = document.getElementById("broadcastAdvisoryForm");
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const destId = parseInt(document.getElementById("advDestinationSelect").value);
    const alertLevel = document.getElementById("advAlertLevel").value;
    const title = document.getElementById("advTitle").value.trim();
    const summary = document.getElementById("advSummary").value.trim();
    const officerName = currentOfficerProfile ? `${currentOfficerProfile.full_name} (${currentOfficerProfile.department})` : "Emergency Operations Command";

    try {
      const res = await fetch("/api/emergency/responder/broadcast-advisory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination_id: destId,
          title: title,
          alert_level: alertLevel,
          summary: summary,
          issued_by: officerName
        })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        showEocToast(`📢 ${data.message}`);
        form.reset();
        await loadRecentAdvisoriesLog();
      } else {
        alert("Advisory broadcast failed: " + (data.detail || "Server error"));
      }
    } catch (err) {
      alert("Network error: " + err.message);
    }
  });
}

async function loadRecentAdvisoriesLog() {
  const feed = document.getElementById("activeAdvisoriesFeed");
  if (!feed) return;

  try {
    const res = await fetch("/api/destinations/news/live-travel-alerts");
    const data = await res.json();
    if (data.alerts && data.alerts.length > 0) {
      feed.innerHTML = data.alerts.slice(0, 6).map(a => `
        <div class="advisory-log-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="adv-badge ${a.severity}">${a.tag || 'Advisory'}</span>
            <span style="font-size:0.7rem; color:#94a3b8;">${a.source}</span>
          </div>
          <h5 style="color:#fff; margin:6px 0 2px 0; font-size:0.85rem;">${a.title}</h5>
          <p style="font-size:0.75rem; color:#cbd5e1; margin:0;">${a.summary}</p>
        </div>
      `).join("");
    }
  } catch (err) {
    console.warn("Could not load advisory log:", err);
  }
}

// =========================================================================
// 6. ACT FAST DISPATCH HANDLERS
// =========================================================================

window.dispatchUnitPrompt = async function(incidentId, agencyType) {
  const callsignPrefix = agencyType === "Police" ? "PCR-VAN" : agencyType === "Fire & Rescue" ? "FIRE-TENDER" : "ALS-AMBULANCE";
  const randomNum = Math.floor(10 + Math.random() * 90);
  const defaultCallsign = `${callsignPrefix}-${randomNum}`;
  const unitCallsign = prompt(`Confirm callsign for rapid dispatch of ${agencyType}:`, defaultCallsign);
  if (!unitCallsign) return;

  const etaMinutes = parseInt(prompt("Estimated Response Time (ETA in minutes):", "4")) || 4;

  try {
    const res = await fetch("/api/emergency/responder/dispatch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        incident_id: incidentId,
        agency_type: agencyType,
        unit_callsign: unitCallsign,
        eta_minutes: etaMinutes,
        responder_notes: `Emergency dispatch activated by ${currentOfficerProfile ? currentOfficerProfile.full_name : 'EOC'}. Unit ${unitCallsign} en route.`
      })
    });

    const data = await res.json();
    if (data.success) {
      showEocToast(`🚔 ${data.message}`);
      await loadEocTelemetry();
    }
  } catch (err) {
    alert("Dispatch failed: " + err.message);
  }
};

window.cycleDispatchStatus = async function(dispatchId, currentStatus) {
  const sequence = ["DISPATCHED", "EN_ROUTE", "ON_SCENE", "RESOLVED"];
  const currIdx = sequence.indexOf(currentStatus);
  const nextStatus = sequence[Math.min(currIdx + 1, sequence.length - 1)];

  try {
    const res = await fetch(`/api/emergency/responder/dispatch/${dispatchId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: nextStatus })
    });

    const data = await res.json();
    if (data.success) {
      showEocToast(`Unit status advanced to: ${nextStatus}`);
      await loadEocTelemetry();
    }
  } catch (err) {
    alert("Status update failed: " + err.message);
  }
};

window.markIncidentResolved = async function(incidentId, dispatchId) {
  if (!confirm("Are you sure you want to mark this emergency incident as RESOLVED?")) return;

  try {
    if (dispatchId) {
      await fetch(`/api/emergency/responder/dispatch/${dispatchId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "RESOLVED", notes: "Case resolved and emergency scene cleared." })
      });
    } else {
      await fetch(`/api/admin/incidents/${incidentId}/resolve?action=Resolved`, {
        method: "PATCH"
      });
    }

    showEocToast(`✓ Incident #${incidentId} stabilized and cleared.`);
    await loadEocTelemetry();
  } catch (err) {
    alert("Error resolving incident: " + err.message);
  }
};

window.flyToIncident = function(lat, lng, title) {
  if (!eocMap) return;
  eocMap.flyTo([lat, lng], 12, { duration: 1.5 });
  showEocToast(`📍 Radar locked on: ${title}`);
};

function setupAgencyTabs() {
  document.querySelectorAll(".agency-tab").forEach(tab => {
    tab.addEventListener("click", async () => {
      document.querySelectorAll(".agency-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      activeAgencyFilter = tab.dataset.agency;
      await loadEocTelemetry();
    });
  });
}
