/**
 * SafeTour Bharat - User Authentication & Session Service
 */

const AuthService = {
  TOKEN_KEY: 'safetour_bharat_token',
  USER_KEY: 'safetour_bharat_user',

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  getUser() {
    try {
      const data = localStorage.getItem(this.USER_KEY);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  getAuthHeaders() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  },

  setSession(token, user) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    this.renderHeaderUser();
    window.dispatchEvent(new CustomEvent('authChanged', { detail: { user } }));
  },

  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.renderHeaderUser();
    window.dispatchEvent(new CustomEvent('authChanged', { detail: { user: null } }));
  },

  async login(email, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Login failed.');
    }

    this.setSession(data.access_token, data.user);
    return data.user;
  },

  async register(fullName, email, password, homeCity = 'India') {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name: fullName,
        email: email,
        password: password,
        home_city: homeCity
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Registration failed.');
    }

    this.setSession(data.access_token, data.user);
    return data.user;
  },

  async refreshProfile() {
    if (!this.isLoggedIn()) return null;
    try {
      const res = await fetch('/api/auth/me', {
        headers: this.getAuthHeaders()
      });
      if (res.ok) {
        const user = await res.json();
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
        this.renderHeaderUser();
        return user;
      }
    } catch (e) {
      console.warn('Could not refresh profile:', e);
    }
    return null;
  },

  renderHeaderUser() {
    const container = document.getElementById('headerUserCapsuleContainer');
    if (!container) return;

    const user = this.getUser();
    if (user) {
      const initials = (user.full_name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
      container.innerHTML = `
        <div class="user-auth-capsule" id="btnUserMenu" title="Click to view profile / logout">
          <div class="user-avatar-badge">${initials}</div>
          <div class="user-meta-info">
            <span class="user-display-name">${user.full_name}</span>
            <span class="user-rank-badge">${user.reputation_badge || 'Explorer'}</span>
          </div>
          <span class="user-xp-chip">⚡ ${user.reputation_xp || 100} XP</span>
        </div>
      `;

      document.getElementById('btnUserMenu')?.addEventListener('click', () => {
        this.showUserProfileModal(user);
      });
    } else {
      container.innerHTML = `
        <button class="btn btn-primary" id="btnOpenAuthModal" style="padding: 7px 16px; font-size: 0.82rem;">
          <i class="fa-solid fa-user-shield"></i> Sign In / Register
        </button>
      `;

      document.getElementById('btnOpenAuthModal')?.addEventListener('click', () => {
        this.openAuthModal();
      });
    }
  },

  openAuthModal(defaultTab = 'login') {
    const modal = document.getElementById('authModal');
    if (!modal) return;
    modal.classList.add('active');
    this.switchAuthTab(defaultTab);
  },

  closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.remove('active');
  },

  switchAuthTab(tab) {
    const loginForm = document.getElementById('loginFormContainer');
    const registerForm = document.getElementById('registerFormContainer');
    const tabLogin = document.getElementById('tabBtnLogin');
    const tabRegister = document.getElementById('tabBtnRegister');

    if (tab === 'login') {
      loginForm?.classList.remove('hidden');
      registerForm?.classList.add('hidden');
      tabLogin?.classList.add('active');
      tabRegister?.classList.remove('active');
    } else {
      loginForm?.classList.add('hidden');
      registerForm?.classList.remove('hidden');
      tabLogin?.classList.remove('active');
      tabRegister?.classList.add('active');
    }
  },

  showUserProfileModal(user) {
    const modal = document.getElementById('profileModal');
    if (!modal) return;
    document.getElementById('profileUserName').textContent = user.full_name;
    document.getElementById('profileUserEmail').textContent = user.email;
    document.getElementById('profileUserBadge').textContent = user.reputation_badge || 'Verified Explorer';
    document.getElementById('profileUserXP').textContent = `${user.reputation_xp || 100} XP`;
    document.getElementById('profileUserCity').textContent = user.home_city || 'India';
    modal.classList.add('active');
  }
};

window.AuthService = AuthService;
