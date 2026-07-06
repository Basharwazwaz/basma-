const CACHE_NAME = "basma-v1";
const OFFLINE_URL = "/offline.html";

const PRECACHE_URLS = ["/", "/offline.html", "/manifest.json", "/logo-icon.png"];

// ─── Install: cache core assets ───────────────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting()),
  );
});

// ─── Activate: purge old caches ───────────────────────────────────────────────
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))),
      )
      .then(() => self.clients.claim()),
  );
});

// ─── Fetch: cache-first for static assets, network-first for API / HTML ──────
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and cross-origin requests
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  // For navigation requests: network-first, fallback to offline page
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((res) => {
          // Clone and cache the fresh navigation response
          const clone = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(request, clone));
          return res;
        })
        .catch(() =>
          caches.match(OFFLINE_URL).then(
            (cached) =>
              cached ||
              new Response("<h1>لا يوجد اتصال بالإنترنت</h1>", {
                headers: { "content-type": "text/html; charset=utf-8" },
              }),
          ),
        ),
    );
    return;
  }

  // For static assets (.js, .css, images, fonts): cache-first
  if (url.pathname.match(/\.(js|css|png|jpg|jpeg|svg|webp|woff2?|ttf)$/)) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((res) => {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(request, clone));
            return res;
          }),
      ),
    );
  }
});
