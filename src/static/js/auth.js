import { apiFetch } from './api.js';

const overlay = document.getElementById('authModalOverlay');
const closeBtn = document.getElementById('closeAuthModal');
const loginBtn = document.getElementById('navLoginBtn');
const accountBtn = document.getElementById('navAccountBtn');
const loginView = document.getElementById('loginView');
const regView = document.getElementById('registerView');
const loginForm = document.getElementById('loginForm');
const regForm = document.getElementById('registerForm');
const loginError = document.getElementById('loginError');
const regError = document.getElementById('registerError');

function authParams() {
  return new URLSearchParams(window.location.search);
}

function authIntent() {
  return authParams().get('auth') || '';
}

function resetToken() {
  return authParams().get('token') || '';
}

function modalCard() {
  if (!overlay) return null;
  return overlay.querySelector('.modal-card') || overlay.firstElementChild;
}

function messageText(data, fallback) {
  if (!data) return fallback;
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => item && (item.msg || item.message))
      .filter(Boolean)
      .join(' ');
  }
  if (typeof data.message === 'string') return data.message;
  return fallback;
}

function setMessage(element, message, ok = false) {
  if (!element) return;
  element.textContent = message;
  element.classList.remove('hidden');
  element.classList.toggle('auth-success-msg', ok);
  element.classList.toggle('auth-error-msg', !ok);
}

function clearMessage(element) {
  if (!element) return;
  element.textContent = '';
  element.classList.add('hidden');
  element.classList.remove('auth-success-msg');
  element.classList.remove('auth-error-msg');
}

function createAuxiliaryViews() {
  if (!overlay || !loginView || !regView) return;
  const card = modalCard();
  if (!card) return;

  if (loginForm && !document.getElementById('showForgotPasswordView')) {
    const forgotLink = document.createElement('div');
    forgotLink.className = 'auth-footer auth-secondary-action';
    forgotLink.innerHTML = '<a href="#" id="showForgotPasswordView">Forgot password?</a>';
    loginForm.insertAdjacentElement('afterend', forgotLink);
  }

  if (!document.getElementById('forgotPasswordView')) {
    const forgotView = document.createElement('div');
    forgotView.id = 'forgotPasswordView';
    forgotView.className = 'auth-view hidden';
    forgotView.innerHTML = `
      <h2 class="auth-title">Reset Password</h2>
      <p class="auth-sub">Enter your account email and we will send a reset link.</p>
      <form id="forgotPasswordForm" class="auth-form">
        <div class="form-field">
          <label for="forgotEmail">Email Address</label>
          <input type="email" id="forgotEmail" required autocomplete="email" />
        </div>
        <button type="submit" class="btn-cta auth-submit">
          <span class="btn-text">Send Reset Link</span>
        </button>
        <div id="forgotPasswordStatus" class="auth-error-msg hidden"></div>
      </form>
      <div class="auth-footer">
        <p><a href="#" id="showLoginFromForgot">Back to sign in</a></p>
      </div>
    `;
    card.appendChild(forgotView);
  }

  if (!document.getElementById('resetPasswordView')) {
    const resetView = document.createElement('div');
    resetView.id = 'resetPasswordView';
    resetView.className = 'auth-view hidden';
    resetView.innerHTML = `
      <h2 class="auth-title">Choose New Password</h2>
      <p class="auth-sub">Enter a new password for your Traditional Astrology account.</p>
      <form id="resetPasswordForm" class="auth-form">
        <div class="form-field">
          <label for="resetPassword">New Password</label>
          <input type="password" id="resetPassword" required minlength="8" autocomplete="new-password" />
        </div>
        <div class="form-field">
          <label for="resetPasswordConfirm">Confirm Password</label>
          <input type="password" id="resetPasswordConfirm" required minlength="8" autocomplete="new-password" />
        </div>
        <button type="submit" class="btn-cta auth-submit">
          <span class="btn-text">Update Password</span>
        </button>
        <div id="resetPasswordStatus" class="auth-error-msg hidden"></div>
      </form>
      <div class="auth-footer">
        <p><a href="#" id="showLoginFromReset">Back to sign in</a></p>
      </div>
    `;
    card.appendChild(resetView);
  }
}

function showView(view = 'login') {
  const viewMap = {
    login: 'loginView',
    register: 'registerView',
    forgot: 'forgotPasswordView',
    reset: 'resetPasswordView',
  };

  Object.values(viewMap).forEach((id) => {
    const element = document.getElementById(id);
    if (element) element.classList.add('hidden');
  });

  const target = document.getElementById(viewMap[view] || 'loginView');
  if (target) target.classList.remove('hidden');
}

function openAuthModal(view = 'login') {
  createAuxiliaryViews();
  if (!overlay || !loginView || !regView) {
    window.location.href = '/account.html?auth=login';
    return;
  }

  overlay.classList.remove('hidden');
  showView(view);
}

function closeAuthModal() {
  if (overlay) {
    overlay.classList.add('hidden');
  }
}

function redirectAfterAuth() {
  const intent = authIntent();
  if (['required', 'expired', 'login', 'register', 'reset'].includes(intent)) {
    window.location.href = '/dashboard.html';
  }
}

const ACCOUNT_PAGE_PATH = '/account.html';

function isAccountEntryLink(link) {
  if (!link) return false;
  const label = (link.getAttribute('aria-label') || '').trim().toLowerCase();
  const text = (link.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
  return link.id === 'navAccountBtn' || label === 'my account' || text === 'my account';
}

function normalizeAccountLinks() {
  document.querySelectorAll('#navAccountBtn, a[aria-label="My Account"]').forEach((link) => {
    if (!isAccountEntryLink(link)) return;
    link.classList.remove('hidden');
    if (link.getAttribute('href') !== ACCOUNT_PAGE_PATH) {
      link.setAttribute('href', ACCOUNT_PAGE_PATH);
    }
    if (link.id === 'navAccountBtn') {
      if (link.textContent !== 'My Account') link.textContent = 'My Account';
    }
  });
}

function updateNavState() {
  normalizeAccountLinks();
  if (loginBtn) {
    loginBtn.classList.add('hidden');
  }
}

async function handleAuth(url, email, password, errorElement, submitBtn) {
  submitBtn.disabled = true;
  clearMessage(errorElement);

  try {
    const response = await apiFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(messageText(data, 'Authentication failed'));
    }

    if (data.token) {
      localStorage.setItem('access_token', data.token);
      localStorage.setItem('user_info', JSON.stringify(data.user));
      updateNavState();
      closeAuthModal();
      if (typeof window.CAEL_AUTH_SUCCESS_CALLBACK === 'function') {
        window.CAEL_AUTH_SUCCESS_CALLBACK(data);
      } else {
        redirectAfterAuth();
      }
    } else if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      updateNavState();
      closeAuthModal();
      if (typeof window.CAEL_AUTH_SUCCESS_CALLBACK === 'function') {
        window.CAEL_AUTH_SUCCESS_CALLBACK(data);
      } else {
        redirectAfterAuth();
      }
    }
  } catch (err) {
    setMessage(errorElement, err.message || 'Authentication failed');
  } finally {
    submitBtn.disabled = false;
  }
}

async function handleForgotPassword(form) {
  const submitBtn = form.querySelector('.auth-submit');
  const statusEl = document.getElementById('forgotPasswordStatus');
  const email = document.getElementById('forgotEmail').value;

  submitBtn.disabled = true;
  clearMessage(statusEl);

  try {
    const response = await apiFetch('/api/v1/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(messageText(data, 'Could not send reset email.'));
    }
    setMessage(statusEl, data.message || 'If an account exists, a reset link has been sent.', true);
  } catch (err) {
    setMessage(statusEl, err.message || 'Could not send reset email.');
  } finally {
    submitBtn.disabled = false;
  }
}

async function handleResetPassword(form) {
  const submitBtn = form.querySelector('.auth-submit');
  const statusEl = document.getElementById('resetPasswordStatus');
  const password = document.getElementById('resetPassword').value;
  const confirm = document.getElementById('resetPasswordConfirm').value;
  const token = resetToken();

  submitBtn.disabled = true;
  clearMessage(statusEl);

  try {
    if (!token) {
      throw new Error('Reset token is missing. Request a new password reset link.');
    }
    if (password !== confirm) {
      throw new Error('Passwords do not match.');
    }

    const response = await apiFetch('/api/v1/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: password })
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(messageText(data, 'Could not reset password.'));
    }

    setMessage(statusEl, data.message || 'Password reset successfully. You can sign in now.', true);
    window.history.replaceState({}, document.title, '/account.html?auth=login');
    showView('login');
    setMessage(loginError, 'Password reset successfully. Sign in with your new password.', true);
  } catch (err) {
    setMessage(statusEl, err.message || 'Could not reset password.');
  } finally {
    submitBtn.disabled = false;
  }
}

createAuxiliaryViews();
updateNavState();

const initialIntent = authIntent();
if (initialIntent === 'required' || initialIntent === 'expired' || initialIntent === 'login') {
  openAuthModal('login');
} else if (initialIntent === 'register') {
  openAuthModal('register');
} else if (initialIntent === 'forgot') {
  openAuthModal('forgot');
} else if (initialIntent === 'reset') {
  openAuthModal('reset');
}

if (loginBtn) {
  loginBtn.addEventListener('click', (e) => {
    e.preventDefault();
    openAuthModal('login');
  });
}

if (closeBtn) {
  closeBtn.addEventListener('click', () => {
    closeAuthModal();
  });
}

document.addEventListener('click', (e) => {
  const link = e.target instanceof Element ? e.target.closest('a') : null;
  if (!isAccountEntryLink(link)) return;
  if (link.getAttribute('href') !== ACCOUNT_PAGE_PATH) {
    link.setAttribute('href', ACCOUNT_PAGE_PATH);
  }
}, true);

document.addEventListener('click', (e) => {
  const link = e.target instanceof Element ? e.target.closest('a') : null;
  if (!link) return;

  if (link.id === 'showRegisterView') {
    e.preventDefault();
    openAuthModal('register');
  } else if (link.id === 'showLoginView' || link.id === 'showLoginFromForgot' || link.id === 'showLoginFromReset') {
    e.preventDefault();
    openAuthModal('login');
  } else if (link.id === 'showForgotPasswordView') {
    e.preventDefault();
    openAuthModal('forgot');
  } else if (link.id === 'accountLoginAction') {
    e.preventDefault();
    openAuthModal('login');
  } else if (link.id === 'accountRegisterAction') {
    e.preventDefault();
    openAuthModal('register');
  }
});

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

const forgotPasswordForm = document.getElementById('forgotPasswordForm');
if (forgotPasswordForm) {
  forgotPasswordForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleForgotPassword(forgotPasswordForm);
  });
}

const resetPasswordForm = document.getElementById('resetPasswordForm');
if (resetPasswordForm) {
  resetPasswordForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleResetPassword(resetPasswordForm);
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
