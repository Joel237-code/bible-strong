const SHELL='logos-shell-v1';
self.addEventListener('install',e=>e.waitUntil(caches.open(SHELL).then(c=>c.addAll(['./','./index.html','./style.css','./app.js','./manifest.webmanifest','./icon-192.png','./icon-512.png'])).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;e.respondWith((async()=>{const cached=await caches.match(e.request);if(cached)return cached;try{return await fetch(e.request)}catch(err){if(e.request.mode==='navigate')return await caches.match('./index.html');return Response.error()}})())});
