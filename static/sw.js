// KasFlow service worker — offline shell
const CACHE = 'kasflow-v2';
const ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon.svg',
  './icon-192.png',
  './icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  // Only cache same-origin GET requests. Never cache Firebase or Google APIs.
  if (request.method !== 'GET') return;
  if (url.origin !== self.location.origin) return;
  event.respondWith(
    caches.match(request).then((cached) => {
      const fetched = fetch(request).then((resp) => {
        if (resp && resp.ok) {
          const clone = resp.clone();
          caches.open(CACHE).then((c) => c.put(request, clone));
        }
        return resp;
      }).catch(() => cached);
      return cached || fetched;
    })
  );
});
