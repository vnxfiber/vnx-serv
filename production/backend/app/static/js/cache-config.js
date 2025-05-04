// Cache configuration
const CACHE_NAME = 'vnx-admin-cache-v1';
const CACHE_ASSETS = [
    '/static/js/main.js',
    '/static/js/chart.js',
    '/static/css/main.css',
    '/static/css/bootstrap.min.css',
    '/static/js/bootstrap.bundle.min.js',
    '/static/js/fontawesome.min.js',
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