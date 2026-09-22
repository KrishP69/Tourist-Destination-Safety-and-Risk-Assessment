/**
 * Navigation shell: More menu, mobile drawer, Live status, My Tickets, SOS hold, admin visibility.
 */
const LiveStatus = {
  lastOkAt: Date.now(),
  demo: false,
  timer: null,

  init() {
    document.getElementById("liveStatusChip")?.addEventListener("click", () => this.open());
    document.getElementById("mobileBtnLive")?.addEventListener("click", () => {
      this.open();
      UxShell.closeMobile();
    });
    document.getElementById("btnLiveSyncFromModal")?.addEventListener("click", () => {
      document.getElementById("syncAllLiveBtn")?.click();
    });
    this.tick();
    this.timer = setInterval(() => this.tick(), 5000);
    this.ping();
  },

  async ping() {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      if (res.ok) {
        this.lastOkAt = Date.now();
        this.demo = !!data.demo_mode;
      }
    } catch (_) {}
    this.renderChip();
  },

  tick() {
    this.renderChip();
  },

  renderChip() {
    const chip = document.getElementById("liveStatusChip");
    const sub = document.getElementById("liveStatusSub");
    if (!chip || !sub) return;
    const ageSec = Math.round((Date.now() - this.lastOkAt) / 1000);
    chip.classList.remove("delayed", "demo");
    if (this.demo) {
      chip.classList.add("demo");
      chip.querySelector("span").textContent = "● DEMO MODE";
      sub.textContent = "Simulated labeled data";
      return;
    }
    if (ageSec > 90) {
      chip.classList.add("delayed");
      chip.querySelector("span").textContent = "● DATA DELAYED";
      sub.textContent = `Last updated ${ageSec < 120 ? ageSec + " sec" : Math.round(ageSec / 60) + " min"} ago`;
    } else {
      chip.querySelector("span").textContent = "● LIVE";
      sub.textContent = `Updated ${ageSec} sec ago`;
    }
  },

  markFresh() {
    this.lastOkAt = Date.now();
    this.renderChip();
  },

  open() {
    const modal = document.getElementById("liveDataModal");
    const updated = document.getElementById("liveDataUpdated");
    if (updated) {
      const ageSec = Math.round((Date.now() - this.lastOkAt) / 1000);
      updated.textContent = this.demo
        ? "DEMO MODE — data is labeled simulation, not live measurements"
        : `Last updated ${ageSec} sec ago`;
    }
    modal?.classList.add("open");
  },

  close() {
    document.getElementById("liveDataModal")?.classList.remove("open");
  },
};

const MyTickets = {
  tab: "upcoming",
  cache: { upcoming: [], completed: [], cancelled: [] },

  init() {
    document.getElementById("btnMyTickets")?.addEventListener("click", () => this.open());
    document.getElementById("mobileBtnTickets")?.addEventListener("click", () => {
      this.open();
      UxShell.closeMobile();
    });
    document.querySelectorAll("#myTicketsModal .ticket-tabs button").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("#myTicketsModal .ticket-tabs button").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        this.tab = btn.dataset.tab;
        this.render();
      });
    });
  },

  async open() {
    document.getElementById("myTicketsModal")?.classList.add("open");
    await this.load();
  },

  close() {
    document.getElementById("myTicketsModal")?.classList.remove("open");
  },

  async load() {
    const anon =
      (window.LocationPresence && LocationPresence.getAnonymousId()) ||
      localStorage.getItem("safetour_anon_id") ||
      "";
    const headers = {};
    if (window.AuthService && AuthService.getToken()) {
      headers.Authorization = `Bearer ${AuthService.getToken()}`;
    }
    try {
      const res = await fetch(`/api/tickets/my-bookings?anonymous_user_id=${encodeURIComponent(anon)}`, {
        headers,
      });
      const data = await res.json();
      this.cache = {
        upcoming: data.upcoming || [],
        completed: data.completed || [],
        cancelled: data.cancelled || [],
      };
      this.render();
    } catch (e) {
      const list = document.getElementById("myTicketsList");
      if (list) list.innerHTML = `<div style="color:#f87171;">${e.message}</div>`;
    }
  },

  render() {
    const list = document.getElementById("myTicketsList");
    if (!list) return;
    const rows = this.cache[this.tab] || [];
    if (!rows.length) {
      list.innerHTML = `<div style="font-size:0.8rem;color:#94a3b8;padding:8px 0;">No ${this.tab} bookings.</div>`;
      return;
    }
    list.innerHTML = rows
      .map(
        (b) => `
      <div class="ticket-item">
        <strong>${b.destination_name || "Destination"}</strong>
        ${b.slot_date} · ${b.start_time}–${b.end_time}<br>
        Visitors: ${b.number_of_people} · ID: ${b.booking_reference}<br>
        Status: ${b.booking_status}
      </div>`
      )
      .join("");
  },
};

const UxShell = {
  init() {
    LiveStatus.init();
    MyTickets.init();
    this.bindMoreMenu();
    this.bindMobile();
    this.bindSosHold();
    this.syncAdminVisibility();
    this.bindLocationLabel();
    window.addEventListener("authChanged", () => this.syncAdminVisibility());

    document.getElementById("btnFindBestTime")?.addEventListener("click", () => BestTime.openModal());
    document.getElementById("mobileBtnReport")?.addEventListener("click", () => {
      document.getElementById("openReportModalBtn")?.click();
      this.closeMobile();
    });
    document.getElementById("mobileBtnLocation")?.addEventListener("click", () => {
      document.getElementById("btnAcquireCurrentGPS")?.click();
      this.closeMobile();
    });
  },

  bindMoreMenu() {
    const btn = document.getElementById("btnNavMore");
    const menu = document.getElementById("navMoreMenu");
    btn?.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = menu?.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", () => menu?.classList.remove("open"));
  },

  bindMobile() {
    document.getElementById("btnMobileMenu")?.addEventListener("click", () => this.openMobile());
    document.getElementById("btnCloseMobileMenu")?.addEventListener("click", () => this.closeMobile());
    document.getElementById("mobileDrawer")?.addEventListener("click", (e) => {
      if (e.target.id === "mobileDrawer") this.closeMobile();
    });
  },

  openMobile() {
    const d = document.getElementById("mobileDrawer");
    d?.classList.add("open");
    d?.setAttribute("aria-hidden", "false");
  },

  closeMobile() {
    const d = document.getElementById("mobileDrawer");
    d?.classList.remove("open");
    d?.setAttribute("aria-hidden", "true");
  },

  bindSosHold() {
    const bind = (el) => {
      if (!el) return;
      let timer = null;
      const start = (e) => {
        e.preventDefault();
        el.classList.add("holding");
        timer = setTimeout(() => {
          el.classList.remove("holding");
          if (typeof window.__safetourStartSos === "function") window.__safetourStartSos();
        }, 700);
      };
      const cancel = () => {
        el.classList.remove("holding");
        if (timer) clearTimeout(timer);
      };
      el.addEventListener("mousedown", start);
      el.addEventListener("touchstart", start, { passive: false });
      el.addEventListener("mouseup", cancel);
      el.addEventListener("mouseleave", cancel);
      el.addEventListener("touchend", cancel);
      el.addEventListener("click", (e) => e.preventDefault());
    };
    bind(document.getElementById("triggerSosBtn"));
    bind(document.getElementById("mobileBtnSos"));
  },

  syncAdminVisibility() {
    const user = window.AuthService?.getUser?.() || null;
    const show = user && user.role === "admin";
    const a = document.getElementById("navAdminLink");
    const m = document.getElementById("mobileAdminLink");
    if (a) a.style.display = show ? "flex" : "none";
    if (m) m.style.display = show ? "flex" : "none";
  },

  bindLocationLabel() {
    const label = document.getElementById("myLocationLabel");
    const btn = document.getElementById("btnAcquireCurrentGPS");
    if (!btn || !label) return;
    const update = () => {
      const consent = localStorage.getItem("safetour_location_consent");
      const st = window.LocationPresence?.status;
      if (st === "active" || st === "granted" || consent === "1") {
        label.textContent = "Location Active";
      } else if (st === "denied") {
        label.textContent = "Enable Location";
      } else if (st === "unavailable") {
        label.textContent = "Location Unavailable";
      } else {
        label.textContent = "Enable Location";
      }
    };
    update();
    setInterval(update, 3000);
    btn.addEventListener("click", () => {
      // Prefer crowd presence consent flow when available
      if (window.LocationPresence) {
        LocationPresence.enable();
      }
      setTimeout(update, 500);
    });
  },
};

window.LiveStatus = LiveStatus;
window.MyTickets = MyTickets;
window.UxShell = UxShell;

document.addEventListener("DOMContentLoaded", () => {
  UxShell.init();
});
