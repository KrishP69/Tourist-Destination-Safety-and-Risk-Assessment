/**
 * Smart Ticket Booking UI — predicted occupancy per slot + overbooking-safe book API.
 */
const SmartBooking = {
  destId: null,
  date: null,

  todayISO() {
    const d = new Date();
    return d.toISOString().slice(0, 10);
  },

  levelClass(level) {
    return level || "UNKNOWN";
  },

  async initForDestination(destId) {
    this.destId = destId;
    const dateInput = document.getElementById("bookingSlotDate");
    if (dateInput && !dateInput.value) dateInput.value = this.todayISO();
    this.date = dateInput ? dateInput.value : this.todayISO();
    await this.loadSlots();
  },

  async loadSlots() {
    if (!this.destId) return;
    const dateInput = document.getElementById("bookingSlotDate");
    this.date = dateInput?.value || this.todayISO();
    const list = document.getElementById("slotListContainer");
    const err = document.getElementById("bookingErrorBox");
    const conf = document.getElementById("bookingConfirmBox");
    if (err) err.classList.remove("visible");
    if (conf) conf.classList.remove("visible");
    if (list) list.innerHTML = `<div style="color:#94a3b8;font-size:0.8rem;padding:8px;">Loading slots…</div>`;

    try {
      const res = await fetch(`/api/tickets/${this.destId}/slots?date=${this.date}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to load slots");
      this.renderSlots(data.slots || []);
    } catch (e) {
      if (list) list.innerHTML = `<div style="color:#f87171;font-size:0.8rem;">${e.message}</div>`;
    }
  },

  renderSlots(slots) {
    const list = document.getElementById("slotListContainer");
    if (!list) return;
    if (!slots.length) {
      list.innerHTML = `<div style="color:#94a3b8;font-size:0.8rem;">No slots for this date.</div>`;
      return;
    }
    list.innerHTML = slots
      .map((s) => {
        const full = s.available <= 0 || s.status === "full";
        const pred =
          s.predicted_crowd != null
            ? `Predicted crowd: ~${s.predicted_crowd} · Occupancy: ${s.predicted_occupancy}%`
            : "Predicted crowd: unavailable";
        return `
        <div class="slot-row ${full ? "full" : ""}">
          <div>
            <div class="slot-time">${s.start_time} – ${s.end_time}</div>
            <div class="slot-meta">
              Available: ${s.available} / ${s.capacity}<br>
              ${pred}<br>
              <span class="crowd-level-pill ${this.levelClass(s.crowd_level)}" style="margin-top:4px;">
                ${CrowdDashboard.levelEmoji(s.crowd_level)} ${s.crowd_level || "UNKNOWN"}
              </span>
              <span style="margin-left:6px;color:#64748b;">Conf: ${s.confidence_label || "Low"}</span>
            </div>
          </div>
          <button class="slot-book-btn" ${full ? "disabled" : ""}
            onclick="SmartBooking.bookSlot(${s.id})">
            ${full ? "Full" : "Book"}
          </button>
        </div>`;
      })
      .join("");
  },

  async findLessCrowded() {
    if (!this.destId) return;
    const dateInput = document.getElementById("bookingSlotDate");
    this.date = dateInput?.value || this.todayISO();
    const list = document.getElementById("slotListContainer");
    if (list) list.innerHTML = `<div style="color:#94a3b8;font-size:0.8rem;">Finding less-crowded times…</div>`;
    try {
      const res = await fetch(
        `/api/tickets/${this.destId}/recommend?date=${this.date}&limit=5`
      );
      const data = await res.json();
      const recs = data.recommendations || [];
      if (!recs.length) {
        list.innerHTML = `<div style="color:#94a3b8;font-size:0.8rem;">No lower-crowd alternatives with availability.</div>`;
        return;
      }
      // Map recommendations into slot-like objects
      this.renderSlots(
        recs.map((r) => ({
          id: r.slot_id,
          start_time: r.start_time,
          end_time: r.end_time,
          available: r.available,
          capacity: r.slot_capacity,
          predicted_crowd: r.predicted_crowd,
          predicted_occupancy: r.predicted_occupancy,
          crowd_level: r.crowd_level,
          confidence_label: r.confidence_label,
          status: r.available > 0 ? "open" : "full",
        }))
      );
      if (typeof window.showLiveToast === "function") {
        window.showLiveToast("Showing lower-crowd recommended slots");
      }
    } catch (e) {
      if (list) list.innerHTML = `<div style="color:#f87171;font-size:0.8rem;">${e.message}</div>`;
    }
  },

  async bookSlot(slotId) {
    const peopleInput = document.getElementById("bookingPeopleCount");
    const people = Math.max(1, parseInt(peopleInput?.value || "1", 10));
    const err = document.getElementById("bookingErrorBox");
    const conf = document.getElementById("bookingConfirmBox");
    if (err) {
      err.classList.remove("visible");
      err.innerHTML = "";
    }
    if (conf) conf.classList.remove("visible");

    const anon =
      (window.LocationPresence && LocationPresence.getAnonymousId()) ||
      localStorage.getItem("safetour_anon_id");

    const headers = { "Content-Type": "application/json" };
    if (window.AuthService && AuthService.getToken()) {
      headers["Authorization"] = `Bearer ${AuthService.getToken()}`;
    }

    try {
      const res = await fetch("/api/tickets/book", {
        method: "POST",
        headers,
        body: JSON.stringify({
          destination_id: this.destId,
          slot_id: slotId,
          number_of_people: people,
          anonymous_user_id: anon,
        }),
      });
      const data = await res.json();
      if (res.status === 409) {
        const detail = data.detail || {};
        const alts = (detail.alternatives || [])
          .slice(0, 3)
          .map(
            (a) =>
              `• ${a.start_time}–${a.end_time}: predicted ~${a.predicted_crowd} (${a.crowd_level})`
          )
          .join("<br>");
        if (err) {
          err.innerHTML = `<strong>${detail.message || "This slot is currently full."}</strong><br>${alts || ""}`;
          err.classList.add("visible");
        }
        return;
      }
      if (!res.ok) {
        throw new Error(typeof data.detail === "string" ? data.detail : "Booking failed");
      }
      if (conf) {
        conf.innerHTML = `
          Booking confirmed.<br>
          Reference: <strong>${data.booking_reference}</strong><br>
          ${data.slot_date} · ${data.start_time}–${data.end_time} · ${data.number_of_people} visitor(s)
        `;
        conf.classList.add("visible");
      }
      this.showConfirmModal(data);
      await this.loadSlots();
      if (CrowdDashboard.currentDestId) CrowdDashboard.loadForDestination(CrowdDashboard.currentDestId);
      if (window.BestTime) BestTime.load(this.destId);
    } catch (e) {
      if (err) {
        err.textContent = e.message;
        err.classList.add("visible");
      }
    }
  },

  showConfirmModal(data) {
    const modal = document.getElementById("bookingConfirmModal");
    const details = document.getElementById("bookingConfirmDetails");
    const cal = document.getElementById("bookingCalendarLink");
    if (!modal || !details) return;
    const destName =
      data.destination_name || window.currentSelectedDestination?.name || "Destination";
    details.innerHTML = `
      <div class="row"><span>Destination</span><b>${destName}</b></div>
      <div class="row"><span>Date</span><b>${data.slot_date}</b></div>
      <div class="row"><span>Time</span><b>${data.start_time} – ${data.end_time}</b></div>
      <div class="row"><span>Visitors</span><b>${data.number_of_people}</b></div>
      <div class="row"><span>Booking ID</span><b>${data.booking_reference}</b></div>
      <div class="row"><span>Status</span><b>Confirmed</b></div>
    `;
    if (cal) {
      const title = encodeURIComponent(`SafeTour visit: ${destName}`);
      const dates = `${(data.slot_date || "").replace(/-/g, "")}T${(data.start_time || "09:00").replace(":", "")}00`;
      cal.href = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dates}/${dates}`;
    }
    modal.classList.add("open");
  },
};

window.SmartBooking = SmartBooking;
