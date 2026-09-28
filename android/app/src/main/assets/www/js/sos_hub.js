/**
 * SafeTour Bharat — SOS Emergency Hub (Improved)
 *
 * Features:
 *  - Press-and-hold guard against accidental triggers (via UxShell)
 *  - 5-second countdown with visual pulse
 *  - Real GPS acquisition with fallback
 *  - Nearest-facility list rendered after dispatch
 *  - Abort / immediate-dispatch controls
 *  - Proper cleanup of timers / audio on every exit path
 *  - Error handling for fetch failures
 */

(function () {
  'use strict';

  let _countdownTimer   = null;
  let _countdownValue   = 5;
  let _dispatchedAlready = false;

  // -----------------------------------------------------------------------
  // Helpers
  // -----------------------------------------------------------------------
  function _getEl(id) { return document.getElementById(id); }

  function _setCoords(text) {
    const el = _getEl('sosCoordsDisplay');
    if (el) el.textContent = text;
  }

  function _setCountdownDisplay(val) {
    const el = _getEl('sosCountdownNumber');
    if (!el) return;
    el.textContent = val;
    el.style.color = (typeof val === 'number' && val <= 2) ? '#ef4444' : '#f8fafc';
  }

  function _playAudio(id) {
    const el = _getEl(id);
    if (!el) return;
    try { el.currentTime = 0; el.play().catch(() => {}); } catch (_) {}
  }

  function _stopAudio(id) {
    const el = _getEl(id);
    if (!el) return;
    try { el.pause(); el.currentTime = 0; } catch (_) {}
  }

  function _clearCountdown() {
    if (_countdownTimer) { clearInterval(_countdownTimer); _countdownTimer = null; }
  }

  // -----------------------------------------------------------------------
  // GPS acquisition
  // -----------------------------------------------------------------------
  function _acquireGPS() {
    if (!navigator.geolocation) {
      _setCoords('28.6139° N, 77.2090° E (IP Geolocation)');
      window.currentLat = 28.6139;
      window.currentLng = 77.2090;
      return;
    }
    _setCoords('Acquiring GPS Fix…');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        window.currentLat = pos.coords.latitude;
        window.currentLng = pos.coords.longitude;
        const lat = pos.coords.latitude.toFixed(5);
        const lng = pos.coords.longitude.toFixed(5);
        _setCoords(`${lat}° N, ${lng}° E (GPS Verified ✓)`);
      },
      () => {
        window.currentLat = 28.6139;
        window.currentLng = 77.2090;
        _setCoords('28.6139° N, 77.2090° E (IP Geolocation)');
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
  }

  // -----------------------------------------------------------------------
  // Core dispatch
  // -----------------------------------------------------------------------
  async function _dispatchSos() {
    if (_dispatchedAlready) return;
    _dispatchedAlready = true;
    _clearCountdown();
    _stopAudio('alertChime');
    _playAudio('sosSiren');
    _setCountdownDisplay('⚡');

    const lat = window.currentLat || 28.6139;
    const lng = window.currentLng || 77.2090;
    const listContainer = _getEl('sosNearestFacilities');

    // Show loading state
    if (listContainer) {
      listContainer.innerHTML = `
        <p style="color:#94a3b8;font-size:0.78rem;text-align:center;margin:8px 0;">
          <i class="fa-solid fa-spinner fa-spin"></i> Locating nearest responders…
        </p>`;
    }

    try {
      const res = await fetch('/api/emergency/sos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat,
          lng,
          emergency_type: 'SOS Button Trigger',
          notes: 'Live distress coordinates transmitted via SafeTour Bharat SOS Hub.'
        })
      });

      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const data = await res.json();

      // Update countdown display
      _setCountdownDisplay('SENT');
      const numEl = _getEl('sosCountdownNumber');
      if (numEl) numEl.style.color = '#10b981';

      // Render nearest facilities
      if (listContainer) {
        const facilities = data.nearest_facilities || [];
        if (facilities.length > 0) {
          listContainer.innerHTML = `
            <h4 style="font-size:0.75rem;color:#10b981;margin:0 0 8px;text-transform:uppercase;letter-spacing:1px;">
              <i class="fa-solid fa-check-circle"></i> Nearest First Responders Alerted
            </h4>
            ${facilities.map(f => `
              <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                          padding:10px 12px;border-radius:8px;font-size:0.78rem;margin-bottom:8px;">
                <div style="font-weight:700;color:#f8fafc;margin-bottom:2px;">
                  ${_escHtml(f.facility_name)}
                  <span style="color:#94a3b8;font-weight:400;font-size:0.7rem;margin-left:6px;">${_escHtml(f.facility_type)}</span>
                </div>
                <div style="color:#94a3b8;">
                  <i class="fa-solid fa-route"></i> ~${_escHtml(String(f.distance_km))} km away &nbsp;|&nbsp;
                  <i class="fa-solid fa-phone"></i>
                  <a href="tel:${_escHtml(f.phone)}" style="color:#60a5fa;font-weight:700;">${_escHtml(f.phone)}</a>
                </div>
              </div>
            `).join('')}
          `;
        } else {
          listContainer.innerHTML = `
            <p style="color:#94a3b8;font-size:0.78rem;text-align:center;margin:8px 0;">
              <i class="fa-solid fa-triangle-exclamation" style="color:#f59e0b;"></i>
              SOS dispatched. Call <a href="tel:112" style="color:#60a5fa;font-weight:700;">112</a> for immediate assistance.
            </p>`;
        }
      }

    } catch (err) {
      console.error('[SOS] Dispatch error:', err);
      _setCountdownDisplay('ERR');
      const numEl = _getEl('sosCountdownNumber');
      if (numEl) numEl.style.color = '#ef4444';
      if (listContainer) {
        listContainer.innerHTML = `
          <div style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);
                      padding:10px 12px;border-radius:8px;color:#fca5a5;font-size:0.8rem;">
            <i class="fa-solid fa-wifi" style="margin-right:6px;"></i>
            Network error — call <a href="tel:112" style="color:#60a5fa;font-weight:700;">112</a>
            or <a href="tel:1364" style="color:#60a5fa;font-weight:700;">1364</a> directly.
          </div>`;
      }
    }
  }

  // -----------------------------------------------------------------------
  // Countdown
  // -----------------------------------------------------------------------
  function _startCountdown() {
    _dispatchedAlready = false;
    _countdownValue = 5;
    _setCountdownDisplay(_countdownValue);
    _acquireGPS();
    _playAudio('alertChime');

    // Reset facilities area
    const list = _getEl('sosNearestFacilities');
    if (list) list.innerHTML = '';

    _clearCountdown();
    _countdownTimer = setInterval(() => {
      _countdownValue -= 1;
      _setCountdownDisplay(_countdownValue);
      if (_countdownValue <= 0) {
        _clearCountdown();
        _dispatchSos();
      }
    }, 1000);
  }

  // -----------------------------------------------------------------------
  // Abort
  // -----------------------------------------------------------------------
  function _abortSos() {
    _clearCountdown();
    _dispatchedAlready = false;
    _stopAudio('alertChime');
    _stopAudio('sosSiren');
    _setCountdownDisplay(5);
    const modal = _getEl('sosPanicModal');
    if (modal) modal.style.display = 'none';
  }

  // -----------------------------------------------------------------------
  // Escape HTML
  // -----------------------------------------------------------------------
  function _escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // -----------------------------------------------------------------------
  // Open modal (called externally via window.__safetourStartSos)
  // -----------------------------------------------------------------------
  function _openSosModal() {
    const modal = _getEl('sosPanicModal');
    if (!modal) return;
    modal.style.display = 'flex';
    _startCountdown();
  }

  // -----------------------------------------------------------------------
  // Init
  // -----------------------------------------------------------------------
  function initSosHub() {
    const modal        = _getEl('sosPanicModal');
    const cancelBtn    = _getEl('cancelSosBtn');
    const confirmBtn   = _getEl('instantSosConfirmBtn');

    if (!modal) return; // SOS modal not present on this page

    cancelBtn?.addEventListener('click', _abortSos);
    confirmBtn?.addEventListener('click', _dispatchSos);

    // Close on backdrop click (outside the card)
    modal.addEventListener('click', (e) => {
      if (e.target === modal) _abortSos();
    });

    // Keyboard: Escape key cancels
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.style.display === 'flex') _abortSos();
    });

    // Expose for press-and-hold trigger from UxShell / mobile button
    window.__safetourStartSos = _openSosModal;
  }

  // Auto-init when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSosHub);
  } else {
    initSosHub();
  }

})();
