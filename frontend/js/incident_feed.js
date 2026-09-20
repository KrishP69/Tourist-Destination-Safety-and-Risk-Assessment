// Crowd-Sourced Safety Incident Feed & Reporting

async function loadIncidentFeed() {
  const container = document.getElementById("liveIncidentFeed");
  if (!container) return;

  try {
    const res = await fetch("/api/incidents?status=Active");
    const incidents = await res.json();

    if (incidents.length === 0) {
      container.innerHTML = '<div style="color:#64748b; font-size:12px; padding:8px;">No active safety hazards reported recently.</div>';
      return;
    }

    container.innerHTML = incidents.map(inc => `
      <div class="incident-chip-card">
        <div class="incident-chip-header">
          <span style="color:${inc.severity === 'Critical' ? '#ef4444' : '#f59e0b'}; font-weight:700;">
            <i class="fa-solid fa-circle-exclamation"></i> ${inc.category}
          </span>
          <span>${inc.destination_name}, ${inc.destination_country}</span>
        </div>
        <h4 class="incident-chip-title">${inc.title}</h4>
        <p class="incident-chip-desc">${inc.description}</p>
        <div class="incident-chip-footer">
          <span><i class="fa-solid fa-location-dot"></i> ${inc.location_name}</span>
          <button class="btn-upvote" onclick="upvoteIncident(${inc.id}, this)">
            <i class="fa-solid fa-thumbs-up"></i> Verified (${inc.upvotes})
          </button>
        </div>
      </div>
    `).join("");

    // Render on map
    if (window.renderIncidentMapPoints) {
      window.renderIncidentMapPoints(incidents);
    }
  } catch (err) {
    console.error("Failed to load live incident feed:", err);
  }
}

async function upvoteIncident(incidentId, btnElement) {
  try {
    const res = await fetch(`/api/incidents/${incidentId}/upvote`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      btnElement.innerHTML = `<i class="fa-solid fa-thumbs-up"></i> Verified (${data.upvotes})`;
      btnElement.style.color = "#10b981";
    }
  } catch (err) {
    console.error("Failed to upvote incident:", err);
  }
}

function initIncidentModal(allDestinations) {
  const modal = document.getElementById("reportIncidentModal");
  const openBtn = document.getElementById("openReportModalBtn");
  const closeBtn = document.getElementById("closeReportModalBtn");
  const cancelBtn = document.getElementById("cancelReportBtn");
  const form = document.getElementById("incidentReportForm");
  const destSelect = document.getElementById("incidentDestination");

  if (!modal || !form) return;

  // Populate destinations
  if (destSelect && allDestinations) {
    destSelect.innerHTML = allDestinations.map(d => `<option value="${d.id}">${d.name} (${d.country})</option>`).join("");
  }

  const openModal = () => { modal.style.display = "flex"; };
  const closeModal = () => { modal.style.display = "none"; };

  openBtn?.addEventListener("click", openModal);
  closeBtn?.addEventListener("click", closeModal);
  cancelBtn?.addEventListener("click", closeModal);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const destId = parseInt(destSelect.value);
    const destObj = allDestinations.find(d => d.id === destId);

    // Approximate lat/lng from destination coords with tiny random offset
    const lat = (destObj ? destObj.lat : 0) + (Math.random() - 0.5) * 0.02;
    const lng = (destObj ? destObj.lng : 0) + (Math.random() - 0.5) * 0.02;

    const payload = {
      destination_id: destId,
      category: document.getElementById("incidentCategory").value,
      severity: document.getElementById("incidentSeverity").value,
      location_name: document.getElementById("incidentLocationName").value,
      title: document.getElementById("incidentTitle").value,
      description: document.getElementById("incidentDesc").value,
      lat: lat,
      lng: lng
    };

    try {
      const res = await fetch("/api/incidents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        alert("Incident report broadcasted successfully. Thank you for contributing to traveler safety!");
        form.reset();
        closeModal();
        loadIncidentFeed();
      }
    } catch (err) {
      alert("Failed to broadcast report: " + err.message);
    }
  });
}
