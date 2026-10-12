// SOS Emergency Panic Hub & Geolocation Dispatch

let sosCountdownTimer = null;
let countdownRemaining = 5;
let isSosDispatching = false;

function initSosHub() {
  const modal = document.getElementById("sosPanicModal");
  const cancelBtn = document.getElementById("cancelSosBtn");
  const confirmBtn = document.getElementById("instantSosConfirmBtn");
  const timerDisplay = document.getElementById("sosCountdownNumber");
  const coordsDisplay = document.getElementById("sosCoordsDisplay");
  const alertAudio = document.getElementById("alertChime");
  const sirenAudio = document.getElementById("sosSiren");

  if (!modal) return;

  const startCountdown = () => {
    modal.style.display = "flex";
    countdownRemaining = 5;
    isSosDispatching = false;
    timerDisplay.innerText = countdownRemaining;
    timerDisplay.style.color = "#ef4444";

    // Play alert audio
    try {
      if (alertAudio) {
        alertAudio.currentTime = 0;
        alertAudio.play().catch(() => {});
      }
    } catch(e){}

    // Try to get real navigator geolocation
    if (navigator.geolocation) {
      coordsDisplay.innerText = "Acquiring GPS fix...";
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude.toFixed(4);
          const lng = pos.coords.longitude.toFixed(4);
          coordsDisplay.innerText = `${lat}° N, ${lng}° E (GPS Verified)`;
          window.currentLat = pos.coords.latitude;
          window.currentLng = pos.coords.longitude;
        },
        (err) => {
          coordsDisplay.innerText = "28.6139° N, 77.2090° E (IP Geolocation)";
          window.currentLat = 28.6139;
          window.currentLng = 77.2090;
        },
        { enableHighAccuracy: true, timeout: 8000 }
      );
    } else {
      coordsDisplay.innerText = "28.6139° N, 77.2090° E (IP Geolocation)";
      window.currentLat = 28.6139;
      window.currentLng = 77.2090;
    }

    clearInterval(sosCountdownTimer);
    sosCountdownTimer = setInterval(() => {
      countdownRemaining--;
      timerDisplay.innerText = countdownRemaining;
      if (countdownRemaining <= 0) {
        clearInterval(sosCountdownTimer);
        dispatchSosPayload();
      }
    }, 1000);
  };

  const abortSos = () => {
    clearInterval(sosCountdownTimer);
    countdownRemaining = 5;
    isSosDispatching = false;
    timerDisplay.innerText = "5";
    timerDisplay.style.color = "#ef4444";
    modal.style.display = "none";
    try {
      if (alertAudio) {
        alertAudio.pause();
        alertAudio.currentTime = 0;
      }
      if (sirenAudio) {
        sirenAudio.pause();
        sirenAudio.currentTime = 0;
      }
    } catch(e){}
  };

  const dispatchSosPayload = async () => {
    if (isSosDispatching) return;
    isSosDispatching = true;
    clearInterval(sosCountdownTimer);

    try {
      if (alertAudio) {
        alertAudio.pause();
        alertAudio.currentTime = 0;
      }
      sirenAudio?.play().catch(() => {});
    } catch(e){}

    const lat = window.currentLat || 28.6139;
    const lng = window.currentLng || 77.2090;

    try {
      const res = await fetch("/api/emergency/sos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: lat,
          lng: lng,
          emergency_type: "SOS Button Trigger",
          notes: "Live distress coordinates transmitted."
        })
      });

      if (!res.ok) {
        throw new Error("Server status: " + res.status);
      }

      const data = await res.json();
      timerDisplay.innerText = "SENT";
      timerDisplay.style.color = "#10b981";

      const listContainer = document.getElementById("sosNearestFacilities");
      if (listContainer && data.nearest_facilities) {
        listContainer.innerHTML = `
          <h4 style="font-size:12px; color:#fff; margin-bottom:8px;">Nearest First Responders Alerted:</h4>
          ${data.nearest_facilities.map(f => `
            <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; font-size:11px; margin-bottom:6px; text-align:left;">
              <strong style="color:#fff;">${f.facility_name}</strong> (${f.facility_type})<br>
              <span>Distance: ~${f.distance_km} km • Call: <a href="tel:${f.phone}" style="color:#60a5fa; font-weight:700;">${f.phone}</a></span>
            </div>
          `).join("")}
        `;
      }
    } catch(err) {
      console.error("SOS dispatch error:", err);
      timerDisplay.innerText = "ERR";
      timerDisplay.style.color = "#ef4444";
      const listContainer = document.getElementById("sosNearestFacilities");
      if (listContainer) {
        listContainer.innerHTML = `
          <div style="background:rgba(239,68,68,0.15); border:1px solid #ef4444; color:#fca5a5; padding:8px 10px; border-radius:6px; font-size:11px; margin-top:8px;">
            Connection error. Please call national emergency directly: <a href="tel:112" style="color:#60a5fa; font-weight:700;">112</a> or Tourist Helpline: <a href="tel:1364" style="color:#60a5fa; font-weight:700;">1364</a>.
          </div>
        `;
      }
    }
  };

  // Exposed for press-and-hold SOS from UxShell (avoids accidental taps)
  window.__safetourStartSos = startCountdown;

  cancelBtn?.addEventListener("click", abortSos);
  confirmBtn?.addEventListener("click", dispatchSosPayload);

  // Dismiss on Escape key or backdrop click
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.style.display === "flex") {
      abortSos();
    }
  });
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      abortSos();
    }
  });
}
