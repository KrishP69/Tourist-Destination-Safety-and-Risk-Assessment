// Admin / Tourism Authority Portal Controller

let adminToken = localStorage.getItem("safetour_admin_token") || "";
let adminUser = null;
try {
  adminUser = JSON.parse(localStorage.getItem("safetour_admin_user") || "null");
} catch (e) {
  adminUser = null;
}

document.addEventListener("DOMContentLoaded", async () => {
  setupAdminAuthHandlers();
  if (checkAdminAuth()) {
    await initializeAdminConsole();
  }
});

function getAdminHeaders() {
  const headers = { "Content-Type": "application/json" };
  if (adminToken) {
    headers["Authorization"] = `Bearer ${adminToken}`;
  }
  return headers;
}

function checkAdminAuth() {
  const modal = document.getElementById("adminAuthModal");
  const officerBadge = document.getElementById("adminOfficerBadge");
  const officerName = document.getElementById("adminOfficerName");
  const logoutBtn = document.getElementById("adminLogoutBtn");

  if (adminToken && adminUser && adminUser.role === "admin") {
    if (modal) modal.style.display = "none";
    if (officerBadge) officerBadge.style.display = "inline-flex";
    if (officerName) officerName.innerText = adminUser.full_name || "Chief Safety Officer";
    if (logoutBtn) logoutBtn.style.display = "inline-flex";
    return true;
  } else {
    if (modal) modal.style.display = "flex";
    if (officerBadge) officerBadge.style.display = "none";
    if (logoutBtn) logoutBtn.style.display = "none";
    return false;
  }
}

function setupAdminAuthHandlers() {
  // Pre-fill demo pass
  document.getElementById("btnFillDemoAdminPass")?.addEventListener("click", () => {
    const emailInput = document.getElementById("adminEmailInput");
    const passInput = document.getElementById("adminPassInput");
    if (emailInput) emailInput.value = "admin@safetour.gov.in";
    if (passInput) passInput.value = "AdminPass#2026";
  });

  // Admin login form submit
  document.getElementById("adminLoginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("adminEmailInput")?.value.trim();
    const password = document.getElementById("adminPassInput")?.value;
    const errEl = document.getElementById("adminLoginError");
    const submitBtn = document.getElementById("btnSubmitAdminPass");

    if (errEl) errEl.style.display = "none";
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Verifying Pass...`;
    }

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Authentication failed. Invalid email or password.");
      }

      if (data.user.role !== "admin") {
        throw new Error("Access Denied: Account lacks administrative privileges. Officer credentials required.");
      }

      // Successful admin login
      adminToken = data.access_token;
      adminUser = data.user;
      localStorage.setItem("safetour_admin_token", adminToken);
      localStorage.setItem("safetour_admin_user", JSON.stringify(adminUser));

      checkAdminAuth();
      await initializeAdminConsole();
      showAdminToast(`✓ Welcome, ${adminUser.full_name}. Authority console unlocked.`);
    } catch (err) {
      if (errEl) {
        errEl.innerText = err.message;
        errEl.style.display = "block";
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-lock-open"></i> Authenticate & Unlock Console`;
      }
    }
  });

  // Logout handler
  document.getElementById("adminLogoutBtn")?.addEventListener("click", () => {
    adminToken = "";
    adminUser = null;
    localStorage.removeItem("safetour_admin_token");
    localStorage.removeItem("safetour_admin_user");
    checkAdminAuth();
    showAdminToast("Console locked. Administrative session terminated.");
  });
}

async function initializeAdminConsole() {
  await loadAdminDestinations();
  await loadAdminIncidents();
  setupAdminForms();
  setupAdminBatchSync();
  setupCreateDestinationForm();
  setupCrowdAdminPanel();
  await refreshAdminCrowdPanel();
}

let destinationsList = [];

function showAdminToast(msg) {
  const toast = document.getElementById("adminLiveToast");
  const msgEl = document.getElementById("adminToastMsg");
  if (!toast || !msgEl) return;
  msgEl.innerText = msg;
  toast.style.display = "flex";
  setTimeout(() => { toast.style.display = "none"; }, 4000);
}

async function loadAdminDestinations() {
  try {
    const res = await fetch("/api/destinations");
    destinationsList = await res.json();

    const advSelect = document.getElementById("advDestination");
    const metricSelect = document.getElementById("metricDestSelect");

    const optionsHtml = destinationsList.map(d => `<option value="${d.id}">${d.name} (${d.state}) — Score: ${d.overall_safety_score}</option>`).join("");

    if (advSelect) advSelect.innerHTML = optionsHtml;
    if (metricSelect) {
      metricSelect.innerHTML = optionsHtml;
      if (destinationsList.length > 0) syncSlidersWithDest(destinationsList[0]);
    }
    const crowdSelect = document.getElementById("crowdConfigDestSelect");
    if (crowdSelect) {
      crowdSelect.innerHTML = optionsHtml;
      crowdSelect.onchange = () => fillCrowdConfigForm(parseInt(crowdSelect.value, 10));
      if (destinationsList.length > 0) fillCrowdConfigForm(destinationsList[0].id);
    }
  } catch (err) {
    console.error("Failed to load destinations in admin:", err);
  }
}

function syncSlidersWithDest(dest) {
  document.getElementById("sliderCrime").value = dest.crime_index || 20;
  document.getElementById("dispCrimeVal").innerText = dest.crime_index || 20;

  document.getElementById("sliderScam").value = dest.scam_index || 25;
  document.getElementById("dispScamVal").innerText = dest.scam_index || 25;

  document.getElementById("sliderWeather").value = dest.weather_risk || 15;
  document.getElementById("dispWeatherVal").innerText = dest.weather_risk || 15;

  document.getElementById("sliderNight").value = dest.night_safety || 80;
  document.getElementById("dispNightVal").innerText = dest.night_safety || 80;
}

async function loadAdminIncidents() {
  const tbody = document.getElementById("adminIncidentsTableBody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/incidents?status=All");
    const incidents = await res.json();

    tbody.innerHTML = incidents.map(inc => `
      <tr>
        <td>#${inc.id}</td>
        <td><strong>${inc.destination_name}</strong></td>
        <td>${inc.category}</td>
        <td><span style="color:${inc.severity === 'Critical' ? '#ef4444' : '#f59e0b'}; font-weight:700;">${inc.severity}</span></td>
        <td>${inc.title}</td>
        <td>${inc.location_name}</td>
        <td>${inc.upvotes}</td>
        <td><span class="badge-tag">${inc.status}</span></td>
        <td>
          <button class="btn-action-small" onclick="setIncidentStatus(${inc.id}, 'Verified')"><i class="fa-solid fa-check"></i> Verify</button>
          <button class="btn-action-small" onclick="setIncidentStatus(${inc.id}, 'Resolved')"><i class="fa-solid fa-circle-check"></i> Resolve</button>
          <button class="btn-action-small" onclick="setIncidentStatus(${inc.id}, 'False Alarm')"><i class="fa-solid fa-ban"></i> Dismiss</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Failed to load admin incidents:", err);
  }
}

window.setIncidentStatus = async function(incidentId, status) {
  try {
    const res = await fetch(`/api/admin/incidents/${incidentId}/resolve?action=${status}`, {
      method: "PATCH",
      headers: getAdminHeaders()
    });
    if (res.status === 401 || res.status === 403) {
      checkAdminAuth();
      alert("Administrative session expired. Please re-enter pass.");
      return;
    }
    const data = await res.json();
    if (data.success) {
      showAdminToast(`Incident #${incidentId} updated to: ${status}`);
      loadAdminIncidents();
    }
  } catch (err) {
    alert("Error updating status: " + err.message);
  }
};

function setupAdminBatchSync() {
  document.getElementById("adminBatchSyncBtn")?.addEventListener("click", async () => {
    showAdminToast("⚡ Querying Open-Meteo API: Synchronizing live weather for all destinations...");
    try {
      let updatedCount = 0;
      for (const d of destinationsList.slice(0, 10)) {
        await fetch(`/api/destinations/${d.id}/sync-live`, { method: "POST" });
        updatedCount++;
      }
      showAdminToast(`✓ Real-time atmospheric hazards calibrated for ${updatedCount} tourist destinations!`);
      await loadAdminDestinations();
    } catch (err) {
      showAdminToast("Atmospheric sync completed with fallback local data.");
    }
  });
}

function setupAdminForms() {
  const bindSlider = (sliderId, dispId) => {
    const s = document.getElementById(sliderId);
    const d = document.getElementById(dispId);
    if (s && d) {
      s.addEventListener("input", (e) => { d.innerText = e.target.value; });
    }
  };

  bindSlider("sliderCrime", "dispCrimeVal");
  bindSlider("sliderScam", "dispScamVal");
  bindSlider("sliderWeather", "dispWeatherVal");
  bindSlider("sliderNight", "dispNightVal");

  document.getElementById("metricDestSelect")?.addEventListener("change", (e) => {
    const destId = parseInt(e.target.value);
    const found = destinationsList.find(d => d.id === destId);
    if (found) syncSlidersWithDest(found);
  });

  document.getElementById("broadcastAdvisoryForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      destination_id: parseInt(document.getElementById("advDestination").value),
      title: document.getElementById("advTitle").value,
      alert_level: document.getElementById("advAlertLevel").value,
      issued_by: document.getElementById("advIssuer").value,
      summary: document.getElementById("advSummary").value
    };

    try {
      const res = await fetch("/api/admin/advisories", {
        method: "POST",
        headers: getAdminHeaders(),
        body: JSON.stringify(payload)
      });
      if (res.status === 401 || res.status === 403) {
        checkAdminAuth();
        alert("Administrative session expired. Please re-enter pass.");
        return;
      }
      const data = await res.json();
      if (data.success) {
        showAdminToast("✓ Official safety advisory broadcasted successfully!");
        document.getElementById("broadcastAdvisoryForm").reset();
      }
    } catch (err) {
      alert("Failed to publish advisory: " + err.message);
    }
  });

  document.getElementById("updateMetricsForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const destId = parseInt(document.getElementById("metricDestSelect").value);
    const payload = {
      crime_index: parseFloat(document.getElementById("sliderCrime").value),
      scam_index: parseFloat(document.getElementById("sliderScam").value),
      weather_risk: parseFloat(document.getElementById("sliderWeather").value),
      night_safety: parseFloat(document.getElementById("sliderNight").value)
    };

    try {
      const res = await fetch(`/api/admin/destinations/${destId}/metrics`, {
        method: "PUT",
        headers: getAdminHeaders(),
        body: JSON.stringify(payload)
      });
      if (res.status === 401 || res.status === 403) {
        checkAdminAuth();
        alert("Administrative session expired. Please re-enter pass.");
        return;
      }
      const data = await res.json();
      if (data.success) {
        showAdminToast(`✓ Metrics updated! New Safety Score: ${data.overall_safety_score} (${data.risk_tier})`);
        await loadAdminDestinations();
      }
    } catch (err) {
      alert("Failed to update metrics: " + err.message);
    }
  });
}

function setupCreateDestinationForm() {
  const form = document.getElementById("createDestinationForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = document.getElementById("btnSubmitNewDest");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Registering Destination...`;
    }

    const payload = {
      name: document.getElementById("newDestName")?.value.trim(),
      state: document.getElementById("newDestState")?.value,
      region: document.getElementById("newDestRegion")?.value,
      category: document.getElementById("newDestCategory")?.value,
      lat: parseFloat(document.getElementById("newDestLat")?.value),
      lng: parseFloat(document.getElementById("newDestLng")?.value),
      image_url: document.getElementById("newDestImage")?.value.trim() || "",
      best_visit_time: document.getElementById("newDestSeason")?.value.trim() || "October to March",
      opening_time: document.getElementById("newDestOpening")?.value.trim() || "06:00",
      closing_time: document.getElementById("newDestClosing")?.value.trim() || "18:30",
      weekly_off_day: document.getElementById("newDestWeeklyOff")?.value || "None",
      peak_rush_hours: document.getElementById("newDestPeakRush")?.value.trim() || "10:30 AM - 03:00 PM",
      entry_fee_domestic: document.getElementById("newDestDomesticFee")?.value.trim() || "Rs 50",
      entry_fee_foreign: document.getElementById("newDestForeignFee")?.value.trim() || "Rs 500",
      booking_portal_url: document.getElementById("newDestBookingUrl")?.value.trim() || "",
      description: document.getElementById("newDestDesc")?.value.trim(),
      dress_code_etiquette: document.getElementById("newDestEtiquette")?.value.trim() || "Modest attire recommended.",
      emergency_facility_name: document.getElementById("newDestPolice")?.value.trim() || "Tourist Police Desk",
      emergency_facility_phone: document.getElementById("newDestPolicePhone")?.value.trim() || "112",
      crime_index: parseFloat(document.getElementById("newDestCrime")?.value || 18.0),
      scam_index: parseFloat(document.getElementById("newDestScam")?.value || 22.0)
    };

    try {
      const res = await fetch("/api/admin/destinations", {
        method: "POST",
        headers: getAdminHeaders(),
        body: JSON.stringify(payload)
      });

      if (res.status === 401 || res.status === 403) {
        checkAdminAuth();
        alert("Administrative authorization expired. Please log in with admin pass.");
        return;
      }

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to add destination.");
      }

      showAdminToast(`✓ Destination '${data.name}' registered! Safety Score: ${data.overall_safety_score}/100`);
      form.reset();
      await loadAdminDestinations();
    } catch (err) {
      alert("Error adding tourist spot: " + err.message);
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-circle-plus"></i> Add Tourist Spot to Bharat Safety Network`;
      }
    }
  });
}

let adminCrowdCache = [];

async function refreshAdminCrowdPanel() {
  const list = document.getElementById("adminCrowdLiveList");
  const badge = document.getElementById("adminDemoModeBadge");
  try {
    const res = await fetch("/api/admin/crowd", { headers: getAdminHeaders() });
    if (!res.ok) throw new Error("Failed to load crowd overview");
    const data = await res.json();
    adminCrowdCache = data.destinations || [];
    if (badge) {
      badge.textContent = data.demo_mode ? "DEMO DATA ON" : "DEMO OFF";
      badge.classList.toggle("visible", !!data.demo_mode);
      badge.style.display = "inline-flex";
    }
    if (list) {
      list.innerHTML = adminCrowdCache
        .slice(0, 20)
        .map((d) => {
          const live = d.live || {};
          const est = live.estimated_crowd != null ? `~${live.estimated_crowd}` : "n/a";
          return `<div style="padding:6px 0;border-bottom:1px solid rgba(148,163,184,0.12);">
            <strong>${d.name}</strong> — Est ${est} · Obs ${live.observed_users ?? 0} ·
            Cap ${d.maximum_capacity} · ${live.crowd_level || "—"} · Conf ${live.confidence ?? "—"}%
            ${live.is_demo_data ? ' <span style="color:#fbbf24;">[DEMO]</span>' : ""}
          </div>`;
        })
        .join("");
    }
    const sel = document.getElementById("crowdConfigDestSelect");
    if (sel && sel.value) fillCrowdConfigForm(parseInt(sel.value, 10));
  } catch (err) {
    if (list) list.innerHTML = `<span style="color:#f87171;">${err.message}</span>`;
  }
}

function fillCrowdConfigForm(destId) {
  const row = adminCrowdCache.find((d) => d.id === destId);
  const fallback = destinationsList.find((d) => d.id === destId) || {};
  const src = row || fallback;
  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.value = val ?? "";
  };
  set("crowdMaxCapacity", src.maximum_capacity ?? 1000);
  set("crowdComfortCapacity", src.comfortable_capacity ?? 600);
  set("crowdEmergencyCap", src.emergency_capacity_override ?? "");
  set("crowdGeofenceRadius", src.geofence_radius_m ?? 800);
  set("crowdAreaSqm", src.area_sq_meters ?? "");
  set("crowdThreshLow", src.threshold_low_max ?? 60);
  set("crowdThreshMod", src.threshold_moderate_max ?? 75);
  set("crowdThreshHigh", src.threshold_high_max ?? 90);
  set("crowdThreshVH", src.threshold_very_high_max ?? 100);
}

function setupCrowdAdminPanel() {
  document.getElementById("btnEnableDemoMode")?.addEventListener("click", async () => {
    const res = await fetch("/api/admin/demo-mode", {
      method: "POST",
      headers: getAdminHeaders(),
      body: JSON.stringify({ enabled: true, bootstrap_history: true }),
    });
    const data = await res.json();
    if (!res.ok) return alert(data.detail || "Failed");
    showAdminToast("DEMO MODE enabled — data is labeled DEMO DATA");
    await refreshAdminCrowdPanel();
  });

  document.getElementById("btnDisableDemoMode")?.addEventListener("click", async () => {
    const res = await fetch("/api/admin/demo-mode", {
      method: "POST",
      headers: getAdminHeaders(),
      body: JSON.stringify({ enabled: false }),
    });
    if (!res.ok) return alert("Failed to disable demo mode");
    showAdminToast("DEMO MODE disabled");
    await refreshAdminCrowdPanel();
  });

  document.getElementById("btnRunDemoTick")?.addEventListener("click", async () => {
    const res = await fetch("/api/admin/demo-tick", { method: "POST", headers: getAdminHeaders() });
    const data = await res.json();
    if (!res.ok) return alert(data.detail || "Demo tick failed");
    showAdminToast(`Demo tick updated ${data.updated || 0} destinations`);
    await refreshAdminCrowdPanel();
  });

  document.getElementById("btnRefreshAdminCrowd")?.addEventListener("click", () => refreshAdminCrowdPanel());

  document.getElementById("btnSaveCrowdConfig")?.addEventListener("click", async () => {
    const destId = parseInt(document.getElementById("crowdConfigDestSelect").value, 10);
    const emergencyRaw = document.getElementById("crowdEmergencyCap").value;
    const payload = {
      maximum_capacity: parseInt(document.getElementById("crowdMaxCapacity").value, 10),
      comfortable_capacity: parseInt(document.getElementById("crowdComfortCapacity").value, 10),
      geofence_radius_m: parseFloat(document.getElementById("crowdGeofenceRadius").value),
      area_sq_meters: parseFloat(document.getElementById("crowdAreaSqm").value) || null,
      threshold_low_max: parseFloat(document.getElementById("crowdThreshLow").value),
      threshold_moderate_max: parseFloat(document.getElementById("crowdThreshMod").value),
      threshold_high_max: parseFloat(document.getElementById("crowdThreshHigh").value),
      threshold_very_high_max: parseFloat(document.getElementById("crowdThreshVH").value),
    };
    if (emergencyRaw !== "") payload.emergency_capacity_override = parseInt(emergencyRaw, 10);
    else payload.emergency_capacity_override = null;

    const res = await fetch(`/api/admin/destinations/${destId}/crowd-config`, {
      method: "PUT",
      headers: getAdminHeaders(),
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) return alert(data.detail || "Save failed");
    showAdminToast("Crowd configuration saved");
    await refreshAdminCrowdPanel();
  });

  document.getElementById("btnEnsureTodaySlots")?.addEventListener("click", async () => {
    const destId = parseInt(document.getElementById("crowdConfigDestSelect").value, 10);
    const res = await fetch(`/api/admin/destinations/${destId}/ensure-slots`, {
      method: "POST",
      headers: getAdminHeaders(),
    });
    const data = await res.json();
    if (!res.ok) return alert(data.detail || "Failed");
    showAdminToast(`Ensured ${data.slots} slots for ${data.date}`);
  });
}
