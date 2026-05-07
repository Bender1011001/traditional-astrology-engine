import { apiFetch } from './api.js';

const overlay = document.getElementById('authModalOverlay');
const closeBtn = document.getElementById('closeAuthModal');
  const loginBtn = document.getElementById('navLoginBtn');
  const accountBtn = document.getElementById('navAccountBtn');
  const loginView = document.getElementById('loginView');
  const regView = document.getElementById('registerView');
  const showRegLink = document.getElementById('showRegisterView');
  const showLoginLink = document.getElementById('showLoginView');

  const loginForm = document.getElementById('loginForm');
  const regForm = document.getElementById('registerForm');
  const loginError = document.getElementById('loginError');
  const regError = document.getElementById('registerError');

  // Check auth state
  function updateNavState() {
    const token = localStorage.getItem('access_token');
    if (token && loginBtn && accountBtn) {
      loginBtn.classList.add('hidden');
      accountBtn.classList.remove('hidden');
      accountBtn.href = '/dashboard.html';
    } else if (loginBtn && accountBtn) {
      loginBtn.classList.remove('hidden');
      accountBtn.classList.add('hidden');
    }
  }

  updateNavState();

  if (loginBtn) {
    loginBtn.addEventListener('click', (e) => {
      e.preventDefault();
      overlay.classList.remove('hidden');
      loginView.classList.remove('hidden');
      regView.classList.add('hidden');
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      overlay.classList.add('hidden');
    });
  }

  if (showRegLink) {
    showRegLink.addEventListener('click', (e) => {
      e.preventDefault();
      loginView.classList.add('hidden');
      regView.classList.remove('hidden');
    });
  }

  if (showLoginLink) {
    showLoginLink.addEventListener('click', (e) => {
      e.preventDefault();
      regView.classList.add('hidden');
      loginView.classList.remove('hidden');
    });
  }

  async function handleAuth(url, email, password, errorElement, submitBtn) {
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    
    submitBtn.disabled = true;
    errorElement.classList.add('hidden');
    errorElement.textContent = '';
    
    try {
      const response = await apiFetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      const data = await response.json();
      
      
      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }
      
      if (data.token) {
        localStorage.setItem('access_token', data.token);
        localStorage.setItem('user_info', JSON.stringify(data.user));
        updateNavState();
        overlay.classList.add('hidden');
        // Show success logic or redirect
        if (typeof window.CAEL_AUTH_SUCCESS_CALLBACK === 'function') {
           window.CAEL_AUTH_SUCCESS_CALLBACK(data);
        }
      } else if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        updateNavState();
        overlay.classList.add('hidden');
      }
    } catch (err) {
      errorElement.textContent = err.message;
      errorElement.classList.remove('hidden');
    } finally {
      submitBtn.disabled = false;
    }
  }

  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('loginEmail').value;
      const pwd = document.getElementById('loginPassword').value;
      const submitBtn = loginForm.querySelector('.auth-submit');
      handleAuth('/api/v1/auth/login', email, pwd, loginError, submitBtn);
    });
  }

  if (regForm) {
    regForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('regEmail').value;
      const pwd = document.getElementById('regPassword').value;
      const submitBtn = regForm.querySelector('.auth-submit');
      handleAuth('/api/v1/auth/register', email, pwd, regError, submitBtn);
    });
  }

  export function updateAuthUI() {
    updateNavState();
  }

  export function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    updateNavState();
    window.location.href = '/';
  }


