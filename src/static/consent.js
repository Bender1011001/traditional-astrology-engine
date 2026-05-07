/**
 * Cookie Consent — Google Consent Mode v2
 * Reads/writes localStorage key "ta_consent" = "granted" | "denied"
 * Fires gtag consent update immediately so GTM knows the user's choice before
 * any analytics tags run.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'ta_consent';
  var BANNER_ID   = 'ta-consent-banner';

  // Update all four Consent Mode v2 signals in one call
  function applyConsent(state) {
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        analytics_storage:    state,
        ad_storage:           state,
        ad_user_data:         state,
        ad_personalization:   state
      });
    }
  }

  function hideBanner() {
    var el = document.getElementById(BANNER_ID);
    if (el) {
      el.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
      el.style.transform  = 'translateY(100%)';
      el.style.opacity    = '0';
      setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 350);
    }
  }

  function accept() {
    localStorage.setItem(STORAGE_KEY, 'granted');
    applyConsent('granted');
    hideBanner();
  }

  function decline() {
    localStorage.setItem(STORAGE_KEY, 'denied');
    applyConsent('denied');
    hideBanner();
  }

  function showBanner() {
    if (document.getElementById(BANNER_ID)) return;

    var banner = document.createElement('div');
    banner.id = BANNER_ID;
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-live', 'polite');
    banner.setAttribute('aria-label', 'Cookie consent');
    banner.innerHTML = [
      '<div class="ta-consent-inner">',
        '<p class="ta-consent-text">',
          'We use analytics (Google Analytics) to understand how people find this site. ',
          'No personal data is sold. You can decline and analytics will not run.',
          ' <a href="/privacy.html" class="ta-consent-link">Privacy policy</a>.',
        '</p>',
        '<div class="ta-consent-btns">',
          '<button id="ta-consent-decline" class="ta-consent-btn ta-consent-btn--decline">Decline</button>',
          '<button id="ta-consent-accept"  class="ta-consent-btn ta-consent-btn--accept">Accept analytics</button>',
        '</div>',
      '</div>'
    ].join('');

    document.body.appendChild(banner);

    document.getElementById('ta-consent-accept').addEventListener('click',  accept);
    document.getElementById('ta-consent-decline').addEventListener('click', decline);

    // Slide in
    requestAnimationFrame(function () {
      banner.style.transition = 'transform 0.35s ease, opacity 0.35s ease';
      banner.style.transform  = 'translateY(0)';
      banner.style.opacity    = '1';
    });
  }

  // ---- Init ----
  var stored = localStorage.getItem(STORAGE_KEY);

  if (stored === 'granted') {
    applyConsent('granted');          // restore prior consent immediately
  } else if (stored === 'denied') {
    applyConsent('denied');           // no-op (already denied by default), but explicit
  } else {
    // No decision yet — show banner after DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }
})();
