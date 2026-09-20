// Core SPA Controller & Real-Time Telemetry Management for SafeTour Bharat

let allDestinationsData = [];
let activeFilters = {
  search: "",
  region: "All",
  risk_tier: "All",
  category: "All"
};
let currentSelectedDestination = null;

document.addEventListener("DOMContentLoaded", async () => {
  // Initialize Core Subsystems
  AuthService.renderHeaderUser();
  GeolocationEngine.init();
  initSafetyMap();
  initSosHub();

  await loadOverviewKPIs();
  await fetchAndRenderDestinations();
  await loadIncidentFeed();

  setupFilterEvents();
  setupSearchEvents();
  setupLiveSyncControls();
  initIncidentModal(allDestinationsData);

  // Listen for Geolocation updates from simulator or real GPS
  window.addEventListener('locationUpdated', async () => {
    await fetchAndRenderDestinations();
    if (currentSelectedDestination) {
      window.selectDestinationById(currentSelectedDestination.id);
    }
  });

  // Listen for Auth changes
  window.addEventListener('authChanged', () => {
    if (currentSelectedDestination) {
      window.selectDestinationById(currentSelectedDestination.id);
    }
  });

  // Background real-time polling (every 30 seconds)
  setInterval(() => {
    loadOverviewKPIs();
    loadIncidentFeed();
  }, 30000);
});

// Toast Notification Helper
function showLiveToast(msg) {
  const toast = document.getElementById("liveToastNotification");
  const msgEl = document.getElementById("toastMessage");
  if (!toast || !msgEl) return;
  msgEl.innerText = msg;
  toast.style.display = "flex";
  setTimeout(() => { toast.style.display = "none"; }, 4000);
}

// Format 24h time to 12h AM/PM
function formatTime12h(timeStr) {
  if (!timeStr) return '--:--';
  const parts = timeStr.split(':');
  if (parts.length < 2) return timeStr;
  let h = parseInt(parts[0], 10);
  const m = parts[1];
  const ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12;
  h = h ? h : 12;
  return `${h.toString().padStart(2, '0')}:${m} ${ampm}`;
}

// Fetch KPI Metrics
async function loadOverviewKPIs() {
  try {
    const res = await fetch("/api/destinations/stats/overview");
    const stats = await res.json();
    document.getElementById("kpiTotalDest").innerText = stats.total_destinations;
    document.getElementById("kpiAvgScore").innerText = stats.average_safety_score + " / 100";
    document.getElementById("kpiPulseVotes").innerText = stats.total_ground_pulse_votes || 0;
    document.getElementById("kpiActiveIncidents").innerText = stats.active_incidents || 0;
  } catch (err) {
    console.error("Failed to load KPIs:", err);
  }
}

// Fetch and render Indian destinations with distance telemetry
async function fetchAndRenderDestinations() {
  const url = new URL("/api/destinations", window.location.origin);
  if (activeFilters.search) url.searchParams.set("search", activeFilters.search);
  if (activeFilters.region !== "All") url.searchParams.set("region", activeFilters.region);
  if (activeFilters.risk_tier !== "All") url.searchParams.set("risk_tier", activeFilters.risk_tier);
  if (activeFilters.category !== "All") url.searchParams.set("category", activeFilters.category);

  // Send current active coordinates to calculate distance
  const pos = GeolocationEngine.currentPosition;
  if (pos && pos.lat && pos.lng) {
    url.searchParams.set("user_lat", pos.lat);
    url.searchParams.set("user_lon", pos.lng);
  }

  try {
    const res = await fetch(url.toString());
    allDestinationsData = await res.json();
    renderDestinationsList(allDestinationsData);
    renderDestinationMapPoints(allDestinationsData, selectDestinationById);
    document.getElementById("destCountBadge").innerText = allDestinationsData.length;
  } catch (err) {
    console.error("Failed to fetch destinations:", err);
  }
}

function renderDestinationsList(destinations) {
  const container = document.getElementById("destinationsGrid");
  if (!container) return;

  if (destinations.length === 0) {
    container.innerHTML = `
      <div style="text-align:center; padding:40px 20px; color:#94a3b8;">
        <i class="fa-solid fa-map-location-dot" style="font-size:32px; margin-bottom:10px; color:#475569;"></i>
        <p>No Indian destinations match your active filters.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = destinations.map(dest => {
    const tierInfo = getTierDetails(dest.risk_tier);
    const inRange = dest.is_within_geofence;
    const distText = dest.distance_km !== null && dest.distance_km !== undefined
      ? `${dest.distance_km} km`
      : 'Calculating...';

    const openStatusHtml = dest.is_currently_open
      ? `<span class="live-status-pill open" style="font-size: 0.65rem; padding: 2px 7px;"><span class="status-dot-pulse"></span> OPEN</span>`
      : `<span class="live-status-pill closed" style="font-size: 0.65rem; padding: 2px 7px;"><span class="status-dot-pulse"></span> CLOSED</span>`;

    const hazardBadgeHtml = (dest.nearby_incidents && dest.nearby_incidents.length > 0)
      ? `<span class="badge-tag" style="background: rgba(239,68,68,0.25); color: #f87171; border: 1px solid #ef4444; font-weight:700;"><i class="fa-solid fa-triangle-exclamation"></i> Alert Active</span>`
      : '';

    return `
      <div class="destination-card" onclick="selectDestinationById(${dest.id})">
        <img src="${dest.image_url}" alt="${dest.name}" class="dest-thumb" onerror="this.src='https://images.unsplash.com/photo-1564507592333-c60657eea523?w=300'">
        <div class="dest-card-info">
          <div class="dest-card-title-row">
            <span class="dest-name">${dest.name}</span>
            <div style="display: flex; gap: 4px; align-items: center;">
              ${openStatusHtml}
              <span class="tier-pill ${tierInfo.cssClass}">${dest.risk_tier}</span>
            </div>
          </div>
          <div class="dest-meta">
            <span><i class="fa-solid fa-location-dot"></i> ${dest.state}</span>
            <span>•</span>
            <span>${dest.category}</span>
            <span>•</span>
            <span style="color: #94a3b8;"><i class="fa-regular fa-clock"></i> ${formatTime12h(dest.opening_time)} - ${formatTime12h(dest.closing_time)}</span>
          </div>
          <div class="dest-card-badges">
            <span class="proximity-badge ${inRange ? 'in-range' : 'out-range'}" style="font-size: 0.7rem; padding: 2px 7px;">
              ${inRange ? '<span class="pulse-dot"></span> In Range (' + distText + ')' : '📍 ' + distText}
            </span>
            <span class="badge-tag" style="color:#10b981; font-weight:700;">
              <i class="fa-solid fa-thumbs-up"></i> ${dest.recommend_percentage}% Rec.
            </span>
            ${hazardBadgeHtml}
            ${dest.active_advisories_count > 0 ? '<span class="badge-tag" style="color:#f59e0b;"><i class="fa-solid fa-bullhorn"></i> ' + dest.active_advisories_count + ' Advisory</span>' : ''}
          </div>
        </div>
        <div class="score-badge-circle ${tierInfo.cssClass}">
          ${dest.overall_safety_score}
        </div>
      </div>
    `;
  }).join("");
}

// Select Destination & View Details
window.selectDestinationById = async function(destId) {
  try {
    const pos = GeolocationEngine.currentPosition;
    let url = `/api/destinations/${destId}`;
    if (pos) {
      url += `?user_lat=${pos.lat}&user_lon=${pos.lng}`;
    }

    const res = await fetch(url);
    const dest = await res.json();
    currentSelectedDestination = dest;
    populateDestinationDetails(dest);
    flyToCoordinates(dest.lat, dest.lng, 8);
    
    // Automatically fetch real-time consensus & reviews
    await refreshDestinationConsensus(destId);

    // Trigger live atmospheric sync in the background
    syncSingleSpotLive(destId, false);
  } catch(err) {
    console.error("Failed to load destination details:", err);
  }
};

async function refreshDestinationConsensus(destId) {
  const consensus = await GroundPulse.fetchConsensus(destId);
  if (!consensus) return;

  document.getElementById("consensusVotesCount").innerText = consensus.total_votes;
  document.getElementById("consensusRecommendPct").innerText = `${consensus.recommend_percentage}% Recommend`;
  document.getElementById("consensusCrowd").innerText = consensus.crowd_consensus;
  document.getElementById("consensusSafety").innerText = consensus.safety_consensus;
  document.getElementById("consensusWeather").innerText = consensus.weather_consensus;

  // Render recent reviews list
  const reviewsContainer = document.getElementById("detailPulseFeedList");
  document.getElementById("detailPulseReviewsCount").innerText = consensus.recent_pulse_feed.length;

  if (consensus.recent_pulse_feed.length === 0) {
    reviewsContainer.innerHTML = `
      <div style="font-size: 0.8rem; color: #64748b; padding: 12px; text-align: center;">
        No on-site reviews yet. Be the first explorer to cast a Ground Pulse vote!
      </div>
    `;
  } else {
    reviewsContainer.innerHTML = consensus.recent_pulse_feed.map(vote => `
      <div class="pulse-review-item">
        <div class="pulse-review-header">
          <div>
            <span class="pulse-reviewer-name">${vote.user_name}</span>
            <span class="user-rank-badge" style="font-size:0.65rem; margin-left: 4px;">[${vote.user_badge}]</span>
          </div>
          <span class="pulse-verified-tag">
            <i class="fa-solid fa-circle-check"></i> ${vote.is_onsite_verified ? 'On-Site Verified' : 'Field Report'}
          </span>
        </div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px;">
          <span style="font-size: 0.68rem; background: rgba(56,189,248,0.15); color: #38bdf8; padding: 2px 6px; border-radius: 4px;">
            Crowd: ${vote.crowd_rush}
          </span>
          <span style="font-size: 0.68rem; background: rgba(16,185,129,0.15); color: #34d399; padding: 2px 6px; border-radius: 4px;">
            ${vote.visit_recommendation}
          </span>
          <span style="font-size: 0.68rem; background: rgba(245,158,11,0.15); color: #fbbf24; padding: 2px 6px; border-radius: 4px;">
            Vibe: ${vote.safety_vibe}
          </span>
          <span style="font-size: 0.68rem; background: rgba(148,163,184,0.15); color: #cbd5e1; padding: 2px 6px; border-radius: 4px;">
            Weather: ${vote.ground_weather}
          </span>
        </div>
        ${vote.user_comment ? `<p class="pulse-review-text">"${vote.user_comment}"</p>` : ''}
      </div>
    `).join("");
  }
}

function populateDestinationDetails(dest) {
  const listView = document.getElementById("destinationsListView");
  const detailView = document.getElementById("destinationDetailView");

  listView.style.display = "none";
  detailView.style.display = "block";

  const tierInfo = getTierDetails(dest.risk_tier);

  document.getElementById("detailDestName").innerText = dest.name;
  document.getElementById("detailLocationSub").innerHTML = `<i class="fa-solid fa-location-dot"></i> ${dest.state}, ${dest.region} • Category: ${dest.category}`;
  document.getElementById("detailHeroImage").src = dest.image_url;

  const riskBadge = document.getElementById("detailRiskBadge");
  riskBadge.className = `tier-pill ${tierInfo.cssClass}`;
  riskBadge.innerText = dest.risk_tier;

  // Real-Time Hazard Alert Box (e.g. Landslide, High Tide, Flash Flood, Blizzard)
  const hazardBox = document.getElementById("detailHazardAlertBox");
  if (hazardBox) {
    if (dest.nearby_incidents && dest.nearby_incidents.length > 0) {
      const inc = dest.nearby_incidents[0];
      hazardBox.style.display = "flex";
      document.getElementById("detailHazardTitle").innerText = inc.title;
      document.getElementById("detailHazardBadge").innerText = `${inc.severity.toUpperCase()} HAZARD`;
      document.getElementById("detailHazardBadge").className = `incident-badge ${inc.severity.toLowerCase()}`;
      document.getElementById("detailHazardDesc").innerText = `${inc.description} (Category: ${inc.incident_type} • Status: ${inc.status.toUpperCase()} • Reported: ${inc.reported_time || 'Recent'})`;
    } else {
      hazardBox.style.display = "none";
    }
  }

  // Live Operations & Timings Matrix
  const liveStatusPill = document.getElementById("detailLiveStatusPill");
  const liveStatusText = document.getElementById("detailLiveStatusText");
  if (liveStatusPill && liveStatusText) {
    if (dest.is_currently_open) {
      liveStatusPill.className = "live-status-pill open";
      liveStatusText.innerText = dest.open_status_text || "OPEN NOW";
    } else {
      liveStatusPill.className = "live-status-pill closed";
      liveStatusText.innerText = dest.open_status_text || "CLOSED";
    }
  }

  if (document.getElementById("detailOperatingHours")) {
    document.getElementById("detailOperatingHours").innerText = `${formatTime12h(dest.opening_time)} - ${formatTime12h(dest.closing_time)}`;
  }
  if (document.getElementById("detailWeeklyOff")) {
    document.getElementById("detailWeeklyOff").innerText = dest.weekly_off_day ? `${dest.weekly_off_day}s` : "None (Open Daily)";
  }
  if (document.getElementById("detailPeakRush")) {
    document.getElementById("detailPeakRush").innerText = dest.peak_rush_hours || "10:30 AM - 03:30 PM";
  }
  if (document.getElementById("detailDomesticFee")) {
    document.getElementById("detailDomesticFee").innerText = dest.entry_fee_domestic || "Free / Nominal";
  }
  if (document.getElementById("detailForeignFee")) {
    document.getElementById("detailForeignFee").innerText = dest.entry_fee_foreign || "Free / Nominal";
  }
  const ticketLink = document.getElementById("detailTicketLink");
  if (ticketLink) {
    if (dest.booking_portal_url) {
      ticketLink.href = dest.booking_portal_url;
      ticketLink.style.display = "inline-flex";
    } else {
      ticketLink.href = "https://asi.payumoney.com/";
      ticketLink.style.display = "inline-flex";
    }
  }

  // Proximity Badge
  const proxBadge = document.getElementById("consensusProximityBadge");
  const dist = GeolocationEngine.calculateDistanceKm(dest.lat, dest.lng);
  const inRange = dist <= 25.0;
  if (inRange) {
    proxBadge.className = 'proximity-badge in-range';
    proxBadge.innerHTML = `<span class="pulse-dot"></span> On-Site Verified (${dist} km away)`;
  } else {
    proxBadge.className = 'proximity-badge out-range';
    proxBadge.innerHTML = `📍 ${dist} km away (Use simulator for testing)`;
  }

  // Setup Vote Buttons
  const openPulseHandler = () => GroundPulse.openVoteModal(dest);
  const btnDetailVote = document.getElementById("btnOpenPulseVoteFromDetail");
  const btnReviewVote = document.getElementById("btnCastPulseInReviews");
  
  if (btnDetailVote) {
    btnDetailVote.onclick = openPulseHandler;
  }
  if (btnReviewVote) {
    btnReviewVote.onclick = openPulseHandler;
  }

  // Score Gauge
  const scoreNum = document.getElementById("detailScoreNumber");
  scoreNum.innerText = dest.overall_safety_score;
  scoreNum.style.color = tierInfo.color;

  document.getElementById("detailVerdictTitle").innerText = tierInfo.verdictTitle;
  document.getElementById("detailVerdictText").innerText = dest.description || tierInfo.verdictText;
  document.getElementById("detailBestTime").innerText = dest.best_visit_time || "All Season";

  // Metrics Bars
  const setBar = (valId, barId, val, invert = false) => {
    const num = Math.round(val || 0);
    document.getElementById(valId).innerText = `${num}%`;
    const bar = document.getElementById(barId);
    bar.style.width = `${num}%`;
    const isBad = invert ? num < 50 : num > 40;
    bar.className = `progress-bar-fill ${isBad ? 'caution' : 'safe'}`;
  };

  setBar("valCrime", "barCrime", dest.crime_index);
  setBar("valScam", "barScam", dest.scam_index);
  setBar("valWeather", "barWeather", dest.weather_risk);
  setBar("valNight", "barNight", dest.night_safety, true);
  setBar("valCrowd", "barCrowd", dest.crowd_density);

  // Advisories
  const advContainer = document.getElementById("detailAdvisoriesList");
  if (dest.advisories && dest.advisories.length > 0) {
    advContainer.innerHTML = dest.advisories.map(a => `
      <div class="advisory-item ${a.alert_level === 'Warning' ? 'warning' : ''}">
        <div class="advisory-header">
          <span><i class="fa-solid fa-triangle-exclamation"></i> ${a.title}</span>
          <span style="font-size:10px; opacity:0.8;">Issued by: ${a.issued_by}</span>
        </div>
        <p>${a.summary}</p>
      </div>
    `).join("");
  } else {
    advContainer.innerHTML = '<div style="font-size:11px; color:#64748b;">No active advisories for this destination.</div>';
  }

  // Google News Live RSS Feed
  const newsContainer = document.getElementById("detailGoogleNewsList");
  if (newsContainer) {
    if (dest.live_news && dest.live_news.length > 0) {
      newsContainer.innerHTML = dest.live_news.map(n => {
        const isWarn = n.severity === "warning";
        return `
          <div class="google-news-item ${isWarn ? 'warning-news' : ''}">
            <div class="news-top-row">
              <span class="news-tag ${n.severity}">${n.tag || 'News Update'}</span>
              <span class="news-source"><i class="fa-brands fa-google"></i> ${n.source} • ${n.published}</span>
            </div>
            <a href="${n.link}" target="_blank" rel="noopener noreferrer" class="news-headline-link">
              ${n.title} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:10px;"></i>
            </a>
            <p class="news-snippet">${n.summary}</p>
          </div>
        `;
      }).join("");
    } else {
      newsContainer.innerHTML = '<div style="font-size:11px; color:#64748b; padding:6px 0;">Real-time Google news updates synchronized with local state authorities.</div>';
    }
  }

  // Emergency Facilities (Police & Hospitals)
  const emgContainer = document.getElementById("detailEmergencyList");
  if (dest.emergency_contacts && dest.emergency_contacts.length > 0) {
    emgContainer.innerHTML = dest.emergency_contacts.map(e => {
      const typeStr = (e.facility_type || '').toLowerCase();
      const isPolice = typeStr.includes("police");
      const icon = isPolice ? "fa-shield-halved" : "fa-notes-medical";
      const badgeCls = isPolice ? "police-badge" : "hospital-badge";
      const safeName = (e.facility_name || '').replace(/'/g, "\\'");
      return `
        <div class="facility-card">
          <div class="facility-card-top">
            <span class="facility-type-tag ${badgeCls}">
              <i class="fa-solid ${icon}"></i> ${e.facility_type}
            </span>
            <span class="facility-247">24/7 OPEN</span>
          </div>
          <strong class="facility-title">${e.facility_name}</strong>
          <span class="facility-address"><i class="fa-solid fa-location-dot"></i> ${e.address || 'Central Sector'}</span>
          <div class="facility-actions-row">
            <a href="tel:${e.phone}" class="btn-call-facility"><i class="fa-solid fa-phone"></i> ${e.phone}</a>
            <button class="btn-locate-facility" onclick="window.focusEmergencyFacility(${e.lat || dest.lat}, ${e.lng || dest.lng}, '${safeName}')" title="Locate and zoom on map">
              <i class="fa-solid fa-map-pin"></i> Locate on Map
            </button>
          </div>
        </div>
      `;
    }).join("");
  } else {
    emgContainer.innerHTML = '<div style="font-size:11px; color:#64748b;">Universal Emergency: Call 112.</div>';
  }

  // Safety Tips & Scam Warnings
  const tipsContainer = document.getElementById("detailTipsList");
  if (dest.tips && dest.tips.length > 0) {
    tipsContainer.innerHTML = dest.tips.map(t => `
      <li><i class="fa-solid fa-shield-check"></i> <span>${t.tip_text}</span></li>
    `).join("");
  } else {
    tipsContainer.innerHTML = '<li><i class="fa-solid fa-shield-check"></i> Keep emergency contacts handy and stay vigilant against unsolicited touts.</li>';
  }
}

// Single Spot Real-Time Live Sync
async function syncSingleSpotLive(destId, showToastNotification = true) {
  try {
    const res = await fetch(`/api/destinations/${destId}/sync-live`, { method: "POST" });
    const data = await res.json();
    if (data.success && data.live_weather) {
      const w = data.live_weather;
      document.getElementById("liveTempDisplay").innerText = `${w.temperature_c}°C`;
      document.getElementById("liveConditionDisplay").innerText = w.condition;
      document.getElementById("liveWindDisplay").innerText = `${w.wind_kmh} km/h`;
      document.getElementById("livePrecipDisplay").innerText = `${w.precipitation_mm} mm`;

      const iconEl = document.getElementById("weatherDynamicIcon");
      if (w.condition.includes("Thunderstorm")) iconEl.className = "fa-solid fa-cloud-bolt weather-dynamic-icon";
      else if (w.condition.includes("Rain") || w.condition.includes("Drizzle")) iconEl.className = "fa-solid fa-cloud-showers-heavy weather-dynamic-icon";
      else if (w.condition.includes("Snow")) iconEl.className = "fa-solid fa-snowflake weather-dynamic-icon";
      else if (w.condition.includes("Clear")) iconEl.className = "fa-solid fa-sun weather-dynamic-icon";
      else iconEl.className = "fa-solid fa-cloud-sun weather-dynamic-icon";

      const tierInfo = getTierDetails(data.risk_tier);
      const scoreNum = document.getElementById("detailScoreNumber");
      scoreNum.innerText = data.overall_safety_score;
      scoreNum.style.color = tierInfo.color;

      const riskBadge = document.getElementById("detailRiskBadge");
      riskBadge.className = `tier-pill ${tierInfo.cssClass}`;
      riskBadge.innerText = data.risk_tier;

      const barWeather = document.getElementById("barWeather");
      const valWeather = document.getElementById("valWeather");
      valWeather.innerText = `${Math.round(w.weather_risk_index)}%`;
      barWeather.style.width = `${Math.round(w.weather_risk_index)}%`;
      barWeather.className = `progress-bar-fill ${w.weather_risk_index > 40 ? 'caution' : 'safe'}`;

      if (showToastNotification) {
        showLiveToast(`⚡ Live telemetry updated for ${data.name}: ${w.temperature_c}°C, ${w.condition}. Safety Score: ${data.overall_safety_score}/100.`);
      }
    }
  } catch(err) {
    console.error("Live sync failed:", err);
  }
}

function setupLiveSyncControls() {
  document.getElementById("syncAllLiveBtn")?.addEventListener("click", async () => {
    showLiveToast("⚡ Contacting Open-Meteo satellites: Synchronizing real-time Bharat weather...");
    try {
      const res = await fetch("/api/destinations/sync-all-live", { method: "POST" });
      const data = await res.json();
      showLiveToast(`✓ ${data.message}`);
      await fetchAndRenderDestinations();
      await loadOverviewKPIs();
    } catch(err) {
      showLiveToast("Error syncing live data: " + err.message);
    }
  });

  document.getElementById("syncCurrentSpotLiveBtn")?.addEventListener("click", () => {
    if (currentSelectedDestination) {
      syncSingleSpotLive(currentSelectedDestination.id, true);
    }
  });
}

// Back to list view button
document.getElementById("backToListBtn")?.addEventListener("click", () => {
  document.getElementById("destinationDetailView").style.display = "none";
  document.getElementById("destinationsListView").style.display = "block";
});

// Setup Filter & Search Event Listeners
function setupFilterEvents() {
  // Region filter chips
  const regionChips = document.querySelectorAll("[data-filter='region']");
  regionChips.forEach(chip => {
    chip.addEventListener("click", () => {
      regionChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      activeFilters.region = chip.dataset.value;
      fetchAndRenderDestinations();
    });
  });

  // Risk Tier filter chips
  const riskChips = document.querySelectorAll("[data-filter='risk_tier']");
  riskChips.forEach(chip => {
    chip.addEventListener("click", () => {
      riskChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      activeFilters.risk_tier = chip.dataset.value;
      fetchAndRenderDestinations();
    });
  });

  const categorySelect = document.getElementById("categoryFilterSelect");
  categorySelect?.addEventListener("change", (e) => {
    activeFilters.category = e.target.value;
    fetchAndRenderDestinations();
  });
}

function setupSearchEvents() {
  const searchInput = document.getElementById("destinationSearchInput");
  const clearBtn = document.getElementById("clearSearchBtn");

  let debounceTimer;
  searchInput?.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    clearBtn.style.display = val ? "block" : "none";

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      activeFilters.search = val;
      fetchAndRenderDestinations();
    }, 200);
  });

  clearBtn?.addEventListener("click", () => {
    searchInput.value = "";
    clearBtn.style.display = "none";
    activeFilters.search = "";
    fetchAndRenderDestinations();
  });
}

window.App = {
  refreshDestinationConsensus
};
