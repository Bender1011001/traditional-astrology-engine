/**
 * Service Worker — Traditional Astrology PWA
 *
 * Strategy:
 *   - App shell (HTML, CSS, JS, fonts, icons) → Cache-First
 *   - API calls → Network-First with offline fallback
 *   - Images → Cache-First with network fallback
 *
 * The SW caches the core app shell on install so the site loads instantly
 * on subsequent visits, even offline.
 */

const CACHE_NAME = "astro-v29-instant-pdf";
const RUNTIME_CACHE = "astro-runtime-v27-support-tips";

// Core app shell — cached on install.
// IMPORTANT: Do NOT include query-string cache busters here.
// Instead, bump CACHE_NAME when deploying new assets.
const APP_SHELL = [
  "/",
  "/index.html",
  "/account.html",
  "/about.html",
  "/faq.html",
  "/geomancy.html",
  "/style.css",
  "/config.js",
  "/consent.js",
  "/js/config.js",
  "/js/reading-app.js",
  "/js/astrocartography-map.js",
  "/js/chart-graphics.js",
  "/js/geomancy-app.js",
  "/js/auth.js",
  "/js/api.js",
  "/manifest.json",
  "/favicon.ico",
  "/apple-touch-icon.png",
  "/icons/icon-192x192.png",
  "/icons/icon-512x512.png",
];

// ─── Install: cache app shell ───────────────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        console.log("[SW] Caching app shell");
        return cache.addAll(APP_SHELL);
      })
      .then(() => self.skipWaiting())
  );
});

// ─── Activate: clean old caches ─────────────────────────────────────────────
self.addEventListener("activate", (event) => {
  const currentCaches = [CACHE_NAME, RUNTIME_CACHE];
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) =>
        Promise.all(
          cacheNames
            .filter((name) => !currentCaches.includes(name))
            .map((name) => {
              console.log("[SW] Deleting old cache:", name);
              return caches.delete(name);
            })
        )
      )
      .then(() => self.clients.claim())
  );
});

// ─── Fetch: routing strategy ────────────────────────────────────────────────
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests (POST to API, etc.)
  if (event.request.method !== "GET") return;

  // Skip cross-origin requests (analytics, fonts CDN, Stripe, etc.)
  if (url.origin !== self.location.origin) return;

  // API calls → Network-First
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // HTML documents → Network-First so returning visitors receive launch fixes.
  if (event.request.mode === "navigate" || event.request.destination === "document") {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Everything else (CSS, JS, images) → Cache-First
  event.respondWith(cacheFirst(event.request));
});

// ─── Cache-First strategy ───────────────────────────────────────────────────
async function cacheFirst(request) {
  // Try exact match first
  let cached = await caches.match(request);
  if (cached) return cached;

  // Try without query string for non-code assets only.
  // JavaScript and CSS query strings are deployment version contracts;
  // stripping them can resurrect stale navigation/auth code from old caches.
  const url = new URL(request.url);
  const isVersionedCodeAsset =
    request.destination === "script" ||
    request.destination === "style" ||
    /\.(?:js|css)$/i.test(url.pathname);
  if (url.search && !isVersionedCodeAsset) {
    const strippedUrl = url.origin + url.pathname;
    cached = await caches.match(strippedUrl);
    if (cached) return cached;
  }

  try {
    const networkResp = await fetch(request);
    // Cache successful responses for future use
    if (networkResp.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResp.clone());
    }
    return networkResp;
  } catch (err) {
    // If both cache and network fail, return a basic offline page
    if (request.destination === "document") {
      return new Response(
        `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Offline — Traditional Astrology</title>
<style>
  body { font-family: 'Inter', sans-serif; background: #0a0a1a; color: #e0ddd5;
         display: flex; align-items: center; justify-content: center; min-height: 100vh;
         margin: 0; text-align: center; }
  .container { max-width: 400px; padding: 2rem; }
  h1 { color: #c9a84c; font-family: 'Cormorant Garamond', serif; }
  p { opacity: 0.8; line-height: 1.6; }
  button { background: #c9a84c; color: #0a0a1a; border: none; padding: 12px 24px;
           border-radius: 8px; cursor: pointer; font-weight: 600; margin-top: 1rem; }
</style></head>
<body><div class="container">
  <h1>☽ You're Offline</h1>
  <p>The stars await your return. Please check your connection and try again.</p>
  <button onclick="location.reload()">Retry</button>
</div></body></html>`,
        { headers: { "Content-Type": "text/html" } }
      );
    }
    return new Response("", { status: 408 });
  }
}

// ─── Network-First strategy (for API) ───────────────────────────────────────
async function networkFirst(request) {
  try {
    const networkResp = await fetch(request);
    if (networkResp.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResp.clone());
    }
    return networkResp;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(JSON.stringify({ error: "You are offline." }), {
      status: 503,
      headers: { "Content-Type": "application/json" },
    });
  }
}
