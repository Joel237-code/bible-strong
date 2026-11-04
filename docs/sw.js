const SHELL='logos-shell-fr-v8', DATA='logos-data-fr-v3';
const ASSETS=['./','./index.html','./style.css','./app.js','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(SHELL).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('logos-shell-')&&k!==SHELL).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;
  e.respondWith((async()=>{
    const request=e.request,url=new URL(request.url), shell=await caches.open(SHELL);
    // Current shell always wins over old app.js saved by a full offline download.
    const app=await shell.match(request);if(app)return app;
    const current=await caches.open(DATA);const isFrench=/\/lex-fr-[GH]\d+\.json$/.test(url.pathname);
    if(isFrench){try{const response=await fetch(request);if(response.ok){await current.put(request,response.clone());return response;}}catch{}}
    const refresh=request.cache==='reload'||request.cache==='no-store'||url.pathname.endsWith('/offline-assets.json');
    if(refresh){try{const response=await fetch(request);if(response.ok)return response;}catch{}}
    const saved=await current.match(request);if(saved)return saved;
    const old=await caches.match(request);if(old)return old;
    try{const response=await fetch(request);if(response.ok&&/\/lex-fr-[GH]\d+\.json$/.test(url.pathname))await current.put(request,response.clone());return response;}
    catch{if(request.mode==='navigate')return await shell.match('./index.html');return Response.error();}
  })());
});
