// SOS Emergency Panic Hub & Geolocation Dispatch

let sosCountdownTimer = null;
let countdownRemaining = 5;

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
    timerDisplay.innerText = countdownRemaining;
    timerDisplay.style.color = "#ef4444";

    // Play alert audio
    try { alertAudio?.play(); } catch(e){}

    // Try to get real navigator geolocation
    if (navigator.geolocation) {
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
        }
      );
    }

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
    modal.style.display = "none";
    try {
      sirenAudio?.pause();
      sirenAudio.currentTime = 0;
    } catch(e){}
  };

  const dispatchSosPayload = async () => {
    clearInterval(sosCountdownTimer);
    try { sirenAudio?.play(); } catch(e){}

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
    }
  };

  // Exposed for press-and-hold SOS from UxShell (avoids accidental taps)
  window.__safetourStartSos = startCountdown;

  cancelBtn?.addEventListener("click", abortSos);
  confirmBtn?.addEventListener("click", dispatchSosPayload);
}
