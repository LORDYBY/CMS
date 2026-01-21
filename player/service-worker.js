// const CACHE_NAME = "player-cache-v1";
// const STATIC_ASSETS = [
//     "/player/",
//     "/player/index.html",
//     "/player/player.js",
//     "/player/boot.js",
//     "/player/styles.css",
// ];

// // -------------------------------------------------------------
// // INSTALL
// // -------------------------------------------------------------
// self.addEventListener("install", (event) => {
//     event.waitUntil(
//         caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
//     );
//     self.skipWaiting();
// });

// // -------------------------------------------------------------
// // ACTIVATE
// // -------------------------------------------------------------
// self.addEventListener("activate", (event) => {
//     event.waitUntil(
//         caches.keys().then(keys =>
//             Promise.all(keys.map(k => k !== CACHE_NAME && caches.delete(k)))
//         )
//     );
//     self.clients.claim();
// });

// // -------------------------------------------------------------
// // FETCH (SAFE, NO DOUBLE-READ)
// // -------------------------------------------------------------
// self.addEventListener("fetch", (event) => {
//     const { request } = event;

//     // Only cache GET requests
//     if (request.method !== "GET") return;

//     event.respondWith(
//         fetch(request)
//             .then((networkResponse) => {
//                 // Clone ONCE, before any read
//                 const responseClone = networkResponse.clone();

//                 caches.open(CACHE_NAME).then((cache) => {
//                     cache.put(request, responseClone);
//                 });

//                 return networkResponse;
//             })
//             .catch(() => caches.match(request))
//     );
// });

// =============================================================

self.addEventListener("fetch", (event) => {
    const request = event.request;

    // Only handle GET
    if (request.method !== "GET") return;

    // ❌ NEVER cache videos or range requests
    if (
        request.destination === "video" ||
        request.headers.get("range")
    ) {
        return;
    }

    event.respondWith(
        caches.match(request).then((cached) => {
            if (cached) return cached;

            return fetch(request).then((response) => {
                // Only cache successful full responses
                if (
                    response.ok &&
                    response.status === 200
                ) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache =>
                        cache.put(request, clone)
                    );
                }
                return response;
            });
        })
    );
});
// =============================================================