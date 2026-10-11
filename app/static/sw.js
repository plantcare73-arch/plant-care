const CACHE_NAME = 'plantcare-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

self.addEventListener('fetch', (event) => {
  // Stale-while-revalidate for static assets, network-first for pages
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});

self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  const options = {
    body: data.body || 'You have a new notification.',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png'
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'Plant Care', options)
  );
});
