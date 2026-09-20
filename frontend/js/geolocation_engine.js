/**
 * SafeTour Bharat - Geolocation & Demo Simulator Engine
 * Calculates Haversine distance, geofencing perimeters (25km threshold), and hybrid GPS / IP positions.
 */

const GeolocationEngine = {
  currentPosition: {
    lat: 28.6139, // Default: New Delhi, India
    lng: 77.2090,
    isSimulated: true,
    locationName: 'Delhi Central (Default)'
  },

  SIMULATED_PRESETS: {
    'delhi': { name: 'New Delhi (Rashtrapati Bhavan)', lat: 28.6143, lng: 77.1994 },
    'mumbai': { name: 'Mumbai (Gateway of India & Colaba)', lat: 18.9220, lng: 72.8347 },
    'bengaluru': { name: 'Bengaluru (MG Road / Cubbon Park)', lat: 12.9716, lng: 77.5946 },
    'kolkata': { name: 'Kolkata (Victoria Memorial)', lat: 22.5448, lng: 88.3426 },
    'chennai': { name: 'Chennai (Marina Beach)', lat: 13.0499, lng: 80.2824 },
    'lakshadweep': { name: 'Lakshadweep (Agatti Island Lagoon)', lat: 10.8530, lng: 72.1949 },
    'taj_mahal': { name: 'Taj Mahal East Gate, Agra', lat: 27.1751, lng: 78.0421 },
    'goa_baga': { name: 'Baga Beach, North Goa', lat: 15.5553, lng: 73.7517 },
    'manali': { name: 'Mall Road, Manali, HP', lat: 32.2396, lng: 77.1887 },
    'varanasi': { name: 'Dashashwamedh Ghat, Varanasi', lat: 25.3109, lng: 83.0107 },
    'leh': { name: 'Leh Main Bazaar, Ladakh', lat: 34.1526, lng: 77.5771 },
    'munnar': { name: 'Munnar Tea Valley, Kerala', lat: 10.0889, lng: 77.0595 },
    'hampi': { name: 'Virupaksha Complex, Hampi', lat: 15.3350, lng: 76.4600 },
    'shillong': { name: 'Police Bazar, Shillong', lat: 25.5788, lng: 91.8933 }
  },

  init() {
    this.setupSimulatorDropdown();
    this.setupMyLocationButton();
    // Silently attempt live network/GPS location without disruptive alerts
    this.acquireLiveLocation(false);
  },

  setupSimulatorDropdown() {
    const select = document.getElementById('locationSimulatorSelect');
    if (!select) return;

    select.addEventListener('change', (e) => {
      const val = e.target.value;
      if (val === 'device_gps') {
        this.acquireLiveLocation(true);
      } else if (this.SIMULATED_PRESETS[val]) {
        const p = this.SIMULATED_PRESETS[val];
        this.currentPosition = {
          lat: p.lat,
          lng: p.lng,
          isSimulated: true,
          locationName: p.name
        };
        this.notifyLocationChange();
        if (typeof window.showLiveToast === 'function') {
          window.showLiveToast(`📍 Position set to ${p.name}`);
        }
      }
    });
  },

  setupMyLocationButton() {
    const btn = document.getElementById('btnAcquireCurrentGPS');
    if (btn) {
      btn.addEventListener('click', () => {
        this.acquireLiveLocation(true);
      });
    }
  },

  /**
   * Acquire live location with seamless graceful fallback:
   * 1. Try Browser HTML5 Geolocation (low-latency, enableHighAccuracy: false)
   * 2. If blocked / timeout on desktop, fallback to Network IP Geolocation
   * 3. Never throw blocking alerts
   */
  async acquireLiveLocation(notifyUser = true) {
    if (notifyUser && typeof window.showLiveToast === 'function') {
      window.showLiveToast('🛰️ Scanning for device GPS & network telemetry...');
    }

    const tryBrowserGps = () => {
      return new Promise((resolve, reject) => {
        if (!('geolocation' in navigator)) {
          reject(new Error('Geolocation not supported'));
          return;
        }
        navigator.geolocation.getCurrentPosition(
          (pos) => resolve(pos),
          (err) => reject(err),
          { timeout: 4000, enableHighAccuracy: false, maximumAge: 300000 }
        );
      });
    };

    try {
      const pos = await tryBrowserGps();
      this.currentPosition = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        isSimulated: false,
        locationName: 'Active Device GPS'
      };
      this.notifyLocationChange();
      this.updateSelectDropdownValue('device_gps');
      if (notifyUser && typeof window.showLiveToast === 'function') {
        window.showLiveToast(`📍 Device GPS Locked: (${this.currentPosition.lat.toFixed(3)}, ${this.currentPosition.lng.toFixed(3)})`);
      }
      return;
    } catch (gpsErr) {
      console.log('Browser GPS unavailable or timed out, activating Network IP telemetry...', gpsErr.message);
    }

    // Fallback: Query backend Network IP Geolocation
    try {
      const res = await fetch('/api/destinations/network/ip-location');
      const data = await res.json();
      if (data && data.lat && data.lng) {
        this.currentPosition = {
          lat: data.lat,
          lng: data.lng,
          isSimulated: false,
          locationName: `${data.city}, ${data.region} (${data.source})`
        };
        this.notifyLocationChange();
        this.updateSelectDropdownValue('device_gps');
        if (notifyUser && typeof window.showLiveToast === 'function') {
          window.showLiveToast(`📍 Location acquired via Network: ${data.city}, ${data.region} (${data.lat.toFixed(2)}, ${data.lng.toFixed(2)})`);
        }
        return;
      }
    } catch (ipErr) {
      console.warn('Network IP location lookup failed:', ipErr);
    }

    // Secondary fallback: External free IP API
    try {
      const res = await fetch('http://ip-api.com/json/');
      const data = await res.json();
      if (data && data.lat && data.lon) {
        this.currentPosition = {
          lat: data.lat,
          lng: data.lon,
          isSimulated: false,
          locationName: `${data.city}, ${data.regionName} (IP Geolocation)`
        };
        this.notifyLocationChange();
        this.updateSelectDropdownValue('device_gps');
        if (notifyUser && typeof window.showLiveToast === 'function') {
          window.showLiveToast(`📍 Location acquired: ${data.city} (${data.lat.toFixed(2)}, ${data.lon.toFixed(2)})`);
        }
        return;
      }
    } catch (extErr) {
      console.warn('Direct IP geolocation failed:', extErr);
    }

    // Graceful silent fallback to default
    if (notifyUser && typeof window.showLiveToast === 'function') {
      window.showLiveToast('📍 Position set to New Delhi Central (Simulated Hub)');
    }
  },

  updateSelectDropdownValue(val) {
    const select = document.getElementById('locationSimulatorSelect');
    if (select) {
      const optionExists = Array.from(select.options).some(o => o.value === val);
      if (optionExists) select.value = val;
    }
  },

  setSimulatedPreset(key) {
    if (this.SIMULATED_PRESETS[key]) {
      const p = this.SIMULATED_PRESETS[key];
      this.currentPosition = {
        lat: p.lat,
        lng: p.lng,
        isSimulated: true,
        locationName: p.name
      };
      this.notifyLocationChange();
      this.updateSelectDropdownValue(key);
    }
  },

  notifyLocationChange() {
    window.dispatchEvent(new CustomEvent('locationUpdated', {
      detail: { ...this.currentPosition }
    }));
  },

  calculateDistanceKm(targetLat, targetLng) {
    const R = 6371.0;
    const dlat = (targetLat - this.currentPosition.lat) * (Math.PI / 180.0);
    const dlon = (targetLng - this.currentPosition.lng) * (Math.PI / 180.0);
    const a =
      Math.sin(dlat / 2.0) * Math.sin(dlat / 2.0) +
      Math.cos(this.currentPosition.lat * (Math.PI / 180.0)) *
      Math.cos(targetLat * (Math.PI / 180.0)) *
      Math.sin(dlon / 2.0) * Math.sin(dlon / 2.0);
    const c = 2.0 * Math.atan2(Math.sqrt(a), Math.sqrt(1.0 - a));
    return Math.round(R * c * 10) / 10;
  },

  isWithinGeofence(targetLat, targetLng, thresholdKm = 25.0) {
    return this.calculateDistanceKm(targetLat, targetLng) <= thresholdKm;
  }
};

window.GeolocationEngine = GeolocationEngine;
