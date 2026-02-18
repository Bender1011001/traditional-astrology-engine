import { apiUrl, apiFetch } from './api.js';
import { initTheme, setupThemeToggle } from './theme.js';

function setStatus(el, msg, isError = false) {
  if (!el) return;
  el.textContent = msg || '';
  el.style.color = isError ? 'var(--danger)' : '';
}

async function submitLead(payload) {
  const resp = await apiFetch('/api/v1/lead', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  let data = null;
  try {
    data = await resp.json();
  } catch (e) {
    // Non-fatal: we'll surface a generic error below.
  }

  if (!resp.ok) {
    const detail = data && data.detail ? String(data.detail) : 'Lead capture failed';
    throw new Error(detail);
  }
  return data;
}

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupThemeToggle();

  const form = document.getElementById('sellerWaitlistForm');
  const statusEl = document.getElementById('leadStatus');
  const submitBtn = document.getElementById('leadSubmitBtn');

  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    setStatus(statusEl, '');

    const email = (document.getElementById('leadEmail')?.value || '').trim();
    const segment = (document.getElementById('leadSegment')?.value || '').trim();
    const platform = (document.getElementById('leadPlatform')?.value || '').trim();
    const volume = (document.getElementById('leadVolume')?.value || '').trim();
    const pain = (document.getElementById('leadPain')?.value || '').trim();

    if (!email) {
      setStatus(statusEl, 'Email is required.', true);
      return;
    }

    const payload = {
      email,
      segment,
      platform,
      volume,
      pain,
      url: window.location.href,
      ua: navigator.userAgent,
    };

    try {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'SENDING...';
      }

      await submitLead(payload);
      setStatus(statusEl, 'Received. We will email you when seller-first features ship.');
      form.reset();
    } catch (err) {
      setStatus(statusEl, `Error: ${err.message}`, true);
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'JOIN THE LIST';
      }
    }
  });
});

