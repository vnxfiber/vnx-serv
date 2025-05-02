// Cache configuration
const CACHE_NAME = 'vnx-admin-cache-v1';
const CACHE_ASSETS = [
    '/static/css/bootstrap.min.css',
    '/static/css/all.min.css',
    '/static/js/chart.js',
    '/static/js/main.js',
    // Add other assets to cache
];

// Install service worker and cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(CACHE_ASSETS);
            })
    );
});

// Serve cached content when offline
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
    );
}); 