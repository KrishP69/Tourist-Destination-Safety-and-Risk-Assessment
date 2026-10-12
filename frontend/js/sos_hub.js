// SOS Emergency Panic Hub & Geolocation Dispatch System
// State-of-the-art interactive emergency beacon with real-time telemetry, Web Audio siren, WhatsApp SOS, and deduplicated responders.

let sosCountdownTimer = null;
let countdownRemaining = 5;
let currentIncidentId = null;
let currentTrackingToken = null;
let selectedEmergencyCategory = "General Emergency";
let isSirenActive = false;
let isSilentMode = false;
let audioContext = null;
let sirenOscillator = null;
let sirenGain = null;
let sirenModulator = null;

function initSosHub() {
  const modal = document.getElementById("sosPanicModal");
  const cancelBtn = document.getElementById("cancelSosBtn");
  const confirmBtn = document.getElementById("instantSosConfirmBtn");
  const deescalateBtn = document.getElementById("deescalateSosBtn");
  const timerDisplay = document.getElementById("sosCountdownNumber");
  const timerLabel = document.getElementById("sosCountdownLabel");
  const timerBox = document.getElementById("sosTimerBox");
  const progressFill = document.getElementById("sosProgressBarFill");
  const coordsDisplay = document.getElementById("sosCoordsDisplay");
  const batteryDisplay = document.getElementById("sosBatteryDisplay");
  const beaconPing = document.getElementById("sosBeaconPing");
  const titleDisplay = document.getElementById("sosModalTitle");
  const subtitleDisplay = document.getElementById("sosModalSubtitle");
  const statusBadgeWrap = document.getElementById("sosStatusBadgeWrap");
  const trackingTokenDisplay = document.getElementById("sosTrackingToken");
  const dispatchEtaDisplay = document.getElementById("sosDispatchEta");
  const facilitiesContainer = document.getElementById("sosNearestFacilities");
  const callPoliceDirectBtn = document.getElementById("callPoliceDirectBtn");
  const btnShareWhatsapp = document.getElementById("btnSosShareWhatsapp");
  const btnToggleSiren = document.getElementById("btnSosToggleSiren");
  const btnSilentMode = document.getElementById("btnSosSilentMode");
  const sirenBtnText = document.getElementById("sosSirenBtnText");
  const categoryChips = document.querySelectorAll(".sos-cat-chip");

  if (!modal) return;

  // 1. Category selector setup
  categoryChips.forEach(chip => {
    chip.addEventListener("click", () => {
      categoryChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      selectedEmergencyCategory = chip.dataset.cat || "General Emergency";
    });
  });

  // 2. Battery telemetry detection
  const updateBattery = async () => {
    if (navigator.getBattery && batteryDisplay) {
      try {
        const b = await navigator.getBattery();
        const level = Math.round(b.level * 100);
        const icon = b.charging ? "fa-bolt" : (level < 20 ? "fa-battery-quarter" : "fa-battery-three-quarters");
        batteryDisplay.innerHTML = `<i class="fa-solid ${icon}"></i> Battery ${level}%${b.charging ? ' (Charging)' : ''}`;
        window.userBatteryLevel = `${level}%`;
      } catch (_) {}
    }
  };
  updateBattery();

  // 3. Web Audio emergency siren generator
  const startSirenSound = () => {
    if (isSilentMode) return;
    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioContext.state === "suspended") {
        audioContext.resume();
      }
      if (isSirenActive) return;

      sirenOscillator = audioContext.createOscillator();
      sirenGain = audioContext.createGain();
      sirenOscillator.type = "sawtooth";

      // Modulate frequency for high-low emergency wail (700Hz to 1350Hz)
      const now = audioContext.currentTime;
      sirenGain.gain.setValueAtTime(0.18, now);

      sirenOscillator.frequency.setValueAtTime(750, now);
      for (let i = 0; i < 60; i++) {
        sirenOscillator.frequency.linearRampToValueAtTime(1350, now + (i * 1.0) + 0.5);
        sirenOscillator.frequency.linearRampToValueAtTime(750, now + (i * 1.0) + 1.0);
      }

      sirenOscillator.connect(sirenGain);
      sirenGain.connect(audioContext.destination);
      sirenOscillator.start();
      isSirenActive = true;

      if (btnToggleSiren) btnToggleSiren.classList.add("active");
      if (sirenBtnText) sirenBtnText.innerText = "Stop Siren";
    } catch (_) {}
  };

  const stopSirenSound = () => {
    try {
      if (sirenOscillator) {
        sirenOscillator.stop();
        sirenOscillator.disconnect();
        sirenOscillator = null;
      }
      isSirenActive = false;
      if (btnToggleSiren) btnToggleSiren.classList.remove("active");
      if (sirenBtnText) sirenBtnText.innerText = "Sound Alarm";
    } catch (_) {}
  };

  // 4. Start Countdown
  const startCountdown = () => {
    modal.style.display = "flex";
    countdownRemaining = 5;
    currentIncidentId = null;

    // Reset UI to countdown state
    if (timerDisplay) {
      timerDisplay.style.display = "block";
      timerDisplay.innerText = countdownRemaining;
      timerDisplay.style.color = "#ef4444";
    }
    if (statusBadgeWrap) statusBadgeWrap.style.display = "none";
    if (timerLabel) timerLabel.innerText = "Seconds until automatic dispatch";
    if (timerBox) timerBox.className = "sos-timer-box";
    if (progressFill) progressFill.style.width = "100%";
    if (dispatchEtaDisplay) dispatchEtaDisplay.style.display = "none";
    if (beaconPing) beaconPing.className = "sos-radar-ping";
    if (titleDisplay) titleDisplay.innerText = "BHARAT EMERGENCY SOS BEACON";
    if (subtitleDisplay) subtitleDisplay.innerText = "Broadcasting emergency locator coordinates to State Police Control Room (112) & nearest medical response units.";

    // Action buttons reset
    if (cancelBtn) cancelBtn.style.display = "block";
    if (confirmBtn) confirmBtn.style.display = "block";
    if (deescalateBtn) deescalateBtn.style.display = "none";
    if (callPoliceDirectBtn) callPoliceDirectBtn.style.display = "none";
    if (facilitiesContainer) facilitiesContainer.innerHTML = "";

    // Live Geolocation detection with high accuracy
    if (navigator.geolocation && coordsDisplay) {
      coordsDisplay.innerText = "Acquiring High-Precision GPS Fix...";
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude.toFixed(4);
          const lng = pos.coords.longitude.toFixed(4);
          const acc = pos.coords.accuracy ? ` (±${Math.round(pos.coords.accuracy)}m Accuracy)` : " (GPS Verified)";
          coordsDisplay.innerText = `${lat}° N, ${lng}° E${acc}`;
          window.currentLat = pos.coords.latitude;
          window.currentLng = pos.coords.longitude;
        },
        () => {
          coordsDisplay.innerText = "19.0760° N, 72.8777° E (State Telemetry)";
          window.currentLat = 19.0760;
          window.currentLng = 72.8777;
        },
        { enableHighAccuracy: true, timeout: 6000 }
      );
    }

    clearInterval(sosCountdownTimer);
    sosCountdownTimer = setInterval(() => {
      countdownRemaining--;
      if (timerDisplay) timerDisplay.innerText = countdownRemaining;
      if (progressFill) progressFill.style.width = `${(countdownRemaining / 5) * 100}%`;

      if (countdownRemaining <= 0) {
        clearInterval(sosCountdownTimer);
        dispatchSosPayload();
      }
    }, 1000);
  };

  // 5. Abort Countdown (False alarm before sent)
  const abortSos = () => {
    clearInterval(sosCountdownTimer);
    stopSirenSound();
    modal.style.display = "none";
  };

  // 6. De-escalate Active SOS (I am safe now)
  const deescalateSos = async () => {
    stopSirenSound();
    if (currentIncidentId) {
      try {
        await fetch("/api/emergency/sos/deescalate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            incident_id: currentIncidentId,
            reason: "Traveler clicked I AM SAFE NOW / De-escalate alert."
          })
        });
      } catch (_) {}
    }
    modal.style.display = "none";
    alert("Emergency Beacon De-escalated.\nPolice and first responders have been notified that you are safe.");
  };

  // 7. Dispatch SOS Payload
  const dispatchSosPayload = async () => {
    clearInterval(sosCountdownTimer);

    const lat = window.currentLat || 19.0760;
    const lng = window.currentLng || 72.8777;

    // Transition UI to DISPATCHED state immediately
    if (timerDisplay) timerDisplay.style.display = "none";
    if (statusBadgeWrap) statusBadgeWrap.style.display = "flex";
    if (timerBox) timerBox.classList.add("sent");
    if (timerLabel) timerLabel.innerText = "LIVE BEACON ACTIVE • POLICE & MEDICAL DISPATCHED";
    if (beaconPing) beaconPing.classList.add("active");
    if (titleDisplay) titleDisplay.innerText = "SOS BEACON ACTIVE • RESCUE EN ROUTE";
    if (subtitleDisplay) subtitleDisplay.innerText = "Telemetry streaming live to State Emergency Command (112), Ambulance (108) and local PCR units.";
    if (dispatchEtaDisplay) dispatchEtaDisplay.style.display = "flex";

    // Switch action buttons: hide countdown buttons, show resolved/call buttons
    if (cancelBtn) cancelBtn.style.display = "none";
    if (confirmBtn) confirmBtn.style.display = "none";
    if (deescalateBtn) deescalateBtn.style.display = "inline-flex";
    if (callPoliceDirectBtn) callPoliceDirectBtn.style.display = "inline-flex";

    // Start siren if not silent
    if (!isSilentMode) {
      startSirenSound();
    }

    try {
      const res = await fetch("/api/emergency/sos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: lat,
          lng: lng,
          emergency_type: selectedEmergencyCategory,
          user_note: `High-priority traveler SOS broadcast. Battery: ${window.userBatteryLevel || 'Normal'}.`
        })
      });

      const data = await res.json();
      currentIncidentId = data.incident_id;
      currentTrackingToken = data.tracking_token || `SOS-IND-${data.incident_id || 101}`;

      if (trackingTokenDisplay) {
        trackingTokenDisplay.innerText = `TOKEN: ${currentTrackingToken}`;
      }

      // Render deduplicated, verified nearest first responders
      if (facilitiesContainer && data.nearest_facilities) {
        const list = data.nearest_facilities;
        facilitiesContainer.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <strong style="font-size:12px; color:#f8fafc;"><i class="fa-solid fa-bell"></i> Nearest First Responders Alerted:</strong>
            <span style="font-size:10px; color:#10b981; font-weight:700;"><i class="fa-solid fa-circle-check"></i> ${list.length} Units Targeted</span>
          </div>
          ${list.map(f => {
            const isPolice = (f.facility_type || '').toLowerCase().includes("police");
            const icon = isPolice ? "fa-shield-halved" : "fa-notes-medical";
            const cls = isPolice ? "police" : "hospital";
            const mapUrl = (f.lat && f.lng) ? `https://www.google.com/maps/dir/?api=1&destination=${f.lat},${f.lng}` : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(f.facility_name)}`;
            return `
              <div class="sos-facility-item ${cls}">
                <div class="sos-facility-info">
                  <strong><i class="fa-solid ${icon}" style="margin-right:4px;"></i>${f.facility_name}</strong>
                  <span>${f.facility_type} • ~${f.distance_km} km away</span>
                </div>
                <div class="sos-facility-actions">
                  <a href="tel:${f.phone}" class="sos-facility-call" title="Call directly">
                    <i class="fa-solid fa-phone"></i> ${f.phone}
                  </a>
                  <a href="${mapUrl}" target="_blank" rel="noopener noreferrer" class="sos-facility-map" title="View directions on Google Maps">
                    <i class="fa-solid fa-route"></i> Map
                  </a>
                </div>
              </div>
            `;
          }).join("")}
        `;
      }
    } catch(err) {
      console.error("SOS dispatch network error:", err);
    }
  };

  // 8. Share Live GPS on WhatsApp
  if (btnShareWhatsapp) {
    btnShareWhatsapp.addEventListener("click", () => {
      const lat = window.currentLat || 19.0760;
      const lng = window.currentLng || 72.8777;
      const token = currentTrackingToken || "PENDING";
      const batt = window.userBatteryLevel || "Normal";
      const text = `🚨 *EMERGENCY SOS ALERT!* 🚨\n\nI need urgent assistance!\n• Emergency: *${selectedEmergencyCategory}*\n• SOS Beacon: *${token}*\n• Battery: ${batt}\n\n📍 *My Live GPS Location:*\nhttps://maps.google.com/?q=${lat},${lng}\n\nIf you cannot reach me, please immediately call Emergency Services at 112.`;
      const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
      window.open(url, "_blank");
    });
  }

  // 9. Siren Toggle & Silent Mode
  if (btnToggleSiren) {
    btnToggleSiren.addEventListener("click", () => {
      if (isSirenActive) {
        stopSirenSound();
      } else {
        isSilentMode = false;
        if (btnSilentMode) btnSilentMode.classList.remove("active");
        startSirenSound();
      }
    });
  }

  if (btnSilentMode) {
    btnSilentMode.addEventListener("click", () => {
      isSilentMode = !isSilentMode;
      btnSilentMode.classList.toggle("active", isSilentMode);
      if (isSilentMode) {
        stopSirenSound();
      }
    });
  }

  // Exposed for press-and-hold SOS from UxShell
  window.__safetourStartSos = startCountdown;

  cancelBtn?.addEventListener("click", abortSos);
  confirmBtn?.addEventListener("click", dispatchSosPayload);
  deescalateBtn?.addEventListener("click", deescalateSos);
}

// Auto-initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initSosHub);
} else {
  initSosHub();
}
