/**
 * Cookie Consent — Google Consent Mode v2
 * Reads/writes localStorage key "ta_consent" = "granted" | "denied"
 * Fires gtag consent update immediately so the Google tag knows the user's
 * choice before analytics events run.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'ta_consent';
  var BANNER_ID   = 'ta-consent-banner';
  var PREFS_ID    = 'ta-cookie-preferences';

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
    showPreferencesControl();
  }

  function decline() {
    localStorage.setItem(STORAGE_KEY, 'denied');
    applyConsent('denied');
    hideBanner();
    showPreferencesControl();
  }

  function showPreferencesControl() {
    if (document.getElementById(PREFS_ID)) return;
    var btn = document.createElement('button');
    btn.id = PREFS_ID;
    btn.type = 'button';
    btn.textContent = 'Cookie preferences';
    btn.setAttribute('aria-label', 'Change cookie preferences');
    btn.addEventListener('click', function () {
      showBanner(true);
    });
    document.body.appendChild(btn);
  }

  function showBanner(force) {
    if (document.getElementById(BANNER_ID)) return;

    var banner = document.createElement('div');
    banner.id = BANNER_ID;
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-live', 'polite');
    banner.setAttribute('aria-label', 'Cookie consent');
    banner.innerHTML = [
      '<div class="ta-consent-inner">',
        '<p class="ta-consent-text">',
          'We use Google Analytics with Consent Mode defaulted to denied. ',
          'Analytics cookies are only enabled if you accept; you can decline or change this later.',
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

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  function ensureNavBackdrop(nav) {
    var existing = document.getElementById('navBackdrop') || document.querySelector('.nav-backdrop');
    if (existing) return existing;
    var backdrop = document.createElement('div');
    backdrop.id = 'navBackdrop';
    backdrop.className = 'nav-backdrop';
    nav.insertAdjacentElement('afterend', backdrop);
    return backdrop;
  }

  function closeMobileNav() {
    document.querySelectorAll('.mobile-menu-toggle').forEach(function (toggle) {
      toggle.setAttribute('aria-expanded', 'false');
      toggle.classList.remove('active');
    });
    document.querySelectorAll('.nav-links').forEach(function (links) {
      links.classList.remove('active');
    });
    document.querySelectorAll('.nav-backdrop').forEach(function (backdrop) {
      backdrop.classList.remove('active');
    });
    document.body.classList.remove('nav-open');
    document.body.style.overflow = '';
  }

  function toggleMobileNav(toggle) {
    var nav = toggle.closest('.site-nav');
    if (!nav) return;
    var navLinks = nav.querySelector('.nav-links');
    if (!navLinks) return;
    var backdrop = ensureNavBackdrop(nav);
    var willOpen = !navLinks.classList.contains('active');

    closeMobileNav();

    if (!willOpen) return;
    toggle.setAttribute('aria-expanded', 'true');
    toggle.classList.add('active');
    navLinks.classList.add('active');
    if (backdrop) backdrop.classList.add('active');
    document.body.classList.add('nav-open');
    document.body.style.overflow = 'hidden';
  }

  function initMobileNavigation() {
    document.querySelectorAll('.site-nav .nav-links').forEach(function (navLinks, index) {
      if (!navLinks.id) navLinks.id = 'siteNavLinks' + (index + 1);
      var nav = navLinks.closest('.site-nav');
      var toggle = nav ? nav.querySelector('.mobile-menu-toggle') : null;
      if (toggle) toggle.setAttribute('aria-controls', navLinks.id);
    });

    document.addEventListener('click', function (event) {
      var toggle = event.target.closest ? event.target.closest('.mobile-menu-toggle') : null;
      if (!toggle) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      toggleMobileNav(toggle);
    }, true);

    document.addEventListener('click', function (event) {
      if (event.target.closest && event.target.closest('.nav-backdrop')) {
        closeMobileNav();
        return;
      }
      if (event.target.closest && event.target.closest('.nav-links a') && window.innerWidth <= 820) {
        closeMobileNav();
      }
    }, true);

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeMobileNav();
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 820) closeMobileNav();
    });
  }

  // ---- Init ----
  var stored = localStorage.getItem(STORAGE_KEY);

  if (stored === 'granted') {
    applyConsent('granted');          // restore prior consent immediately
    ready(showPreferencesControl);
  } else if (stored === 'denied') {
    applyConsent('denied');           // no-op (already denied by default), but explicit
    ready(showPreferencesControl);
  } else {
    // No decision yet — show banner after DOM is ready
    ready(function () { showBanner(false); });
  }

  ready(initMobileNavigation);
})();
