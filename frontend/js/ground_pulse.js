/**
 * SafeTour Bharat - Ground Pulse MCQ Voting & Consensus Engine
 */

const GroundPulse = {
  activeDestination: null,

  openVoteModal(dest) {
    if (!AuthService.isLoggedIn()) {
      alert('Please sign in or register to submit on-site Ground Pulse votes and earn Reputation XP.');
      AuthService.openAuthModal('login');
      return;
    }

    this.activeDestination = dest;
    const modal = document.getElementById('groundPulseModal');
    if (!modal) return;

    // Set Destination Header Info
    document.getElementById('pulseModalDestName').textContent = dest.name;
    document.getElementById('pulseModalDestState').textContent = `${dest.state}, ${dest.region}`;

    const dist = GeolocationEngine.calculateDistanceKm(dest.lat, dest.lng);
    const inRange = dist <= 25.0;

    const geofenceBadge = document.getElementById('pulseModalGeofenceBadge');
    if (geofenceBadge) {
      if (inRange) {
        geofenceBadge.className = 'proximity-badge in-range';
        geofenceBadge.innerHTML = `<span class="pulse-dot"></span> On-Site Verified (${dist} km away)`;
      } else {
        geofenceBadge.className = 'proximity-badge out-range';
        geofenceBadge.innerHTML = `⚠️ ${dist} km away (Exceeds 25km limit)`;
      }
    }

    // Reset Form Options
    document.getElementById('groundPulseForm').reset();
    document.getElementById('pulseSubmitError').classList.add('hidden');
    document.getElementById('pulseSubmitSuccess').classList.add('hidden');

    modal.classList.add('active');
  },

  closeVoteModal() {
    const modal = document.getElementById('groundPulseModal');
    if (modal) modal.classList.remove('active');
  },

  async submitVote(e) {
    e.preventDefault();
    if (!this.activeDestination) return;

    const form = e.target;
    const formData = new FormData(form);

    const crowd_rush = formData.get('crowd_rush');
    const visit_recommendation = formData.get('visit_recommendation');
    const safety_vibe = formData.get('safety_vibe');
    const ground_weather = formData.get('ground_weather');
    const clean_sanitation = formData.get('clean_sanitation') || 'Good';
    const user_comment = formData.get('user_comment') || '';

    if (!crowd_rush || !visit_recommendation || !safety_vibe || !ground_weather) {
      this.showError('Please answer all required MCQ questions before submitting.');
      return;
    }

    const pos = GeolocationEngine.currentPosition;
    const isSimulated = pos.isSimulated;

    const payload = {
      destination_id: this.activeDestination.id,
      user_lat: pos.lat,
      user_lon: pos.lng,
      crowd_rush: crowd_rush,
      visit_recommendation: visit_recommendation,
      safety_vibe: safety_vibe,
      ground_weather: ground_weather,
      clean_sanitation: clean_sanitation,
      user_comment: user_comment,
      is_simulated_override: isSimulated
    };

    const submitBtn = document.getElementById('btnSubmitPulse');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Submitting Field Intel...`;
    }

    try {
      const res = await fetch('/api/pulse/vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders()
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to submit vote.');
      }

      // Show Success State
      const successBox = document.getElementById('pulseSubmitSuccess');
      successBox.classList.remove('hidden');
      successBox.innerHTML = `
        <i class="fa-solid fa-circle-check" style="color: #34d399; font-size: 1.2rem;"></i>
        <div>
          <strong>Field Pulse Registered!</strong>
          <p style="margin: 2px 0 0; font-size: 0.8rem; color: #a7f3d0;">
            +${data.awarded_xp} XP awarded! Total: ${data.new_reputation_xp} XP (${data.new_badge}).
          </p>
        </div>
      `;

      // Refresh User profile in header
      await AuthService.refreshProfile();

      // Refresh Consensus stats in destination card / modal
      if (window.App && typeof window.App.refreshDestinationConsensus === 'function') {
        window.App.refreshDestinationConsensus(this.activeDestination.id);
      }

      setTimeout(() => {
        this.closeVoteModal();
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `Cast Verified Ground Pulse Vote`;
        }
      }, 2000);

    } catch (err) {
      this.showError(err.message);
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `Cast Verified Ground Pulse Vote`;
      }
    }
  },

  showError(msg) {
    const errorBox = document.getElementById('pulseSubmitError');
    if (errorBox) {
      errorBox.textContent = msg;
      errorBox.classList.remove('hidden');
    }
  },

  async fetchConsensus(destId) {
    try {
      const res = await fetch(`/api/pulse/${destId}/consensus`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Could not fetch consensus:', e);
    }
    return null;
  }
};

window.GroundPulse = GroundPulse;
