// Service Worker — IT·База (PWA офлайн-доступ)
// Кэширует главные страницы + 50 свежих статей для чтения без интернета
const CACHE = "itbase-v1";
const ASSETS = [
    "/,
    "/about.html,
    "/contacts.html,
    "/support.html,
    "/sitemap.html,
    "/archive.html,
    "/top.html,
    "/glossary.html,
    "/search.html,
    "/roadmaps.html,
    "/cheatsheets.html,
    "/style.css,
    "/app.js,
    "/data/articles.js,
    "/data/index.js,
    "/favicon.svg,
    "/favicon.ico,
    "/manifest.json,
    "/rss.xml,
    "/sitemap.xml,
    "/articles/kak-napisat-rezyume-programmista.html,
    "/articles/tailwind-css-vs-bootstrap.html,
    "/articles/websocket-vs-sse-vs-polling.html,
    "/articles/postgresql-vs-mysql.html,
    "/articles/claude-ai-obzor.html,
    "/articles/nextjs-15-chto-novogo.html,
    "/articles/rust-vs-go-sravnenie.html,
    "/articles/kubernetes-dlya-novichka.html,
    "/articles/github-copilot-obzor.html,
    "/articles/chatgpt-kak-polzovatsya.html,
    "/articles/paginaciya-i-versirovanie-api.html,
    "/articles/chto-takoe-nginx.html,
    "/articles/bash-skripty-dlya-novichka.html,
    "/articles/obrabotka-isklyucheniy-v-python.html,
    "/articles/dizayn-patterns-singleton-factory-observer.html,
    "/articles/cookie-localstorage-sessionstorage.html,
    "/articles/tranzakcii-i-acid.html,
    "/articles/python-s-nulya.html,
    "/articles/dekoratory-v-python.html,
    "/articles/docker-compose-dlya-proekta.html,
    "/articles/chto-takoe-cors.html,
    "/articles/heshirovanie-paroley.html,
    "/articles/xss-csrf-sql-inekcii.html,
    "/articles/kak-rabotaet-websocket.html,
    "/articles/chto-takoe-orm.html,
    "/articles/mnogopotochnost-v-python-gil.html,
    "/articles/zachem-nuzhen-typescript.html,
    "/articles/asinhronnost-v-python.html,
    "/articles/indeksy-v-bazah-dannyh.html,
    "/articles/git-vetki-i-sliyanie.html,
    "/articles/sql-zaprosy-s-nulya.html,
    "/articles/osnovy-linux-dlya-razrabotchika.html,
    "/articles/monolit-i-mikroservisy.html,
    "/articles/http-metody-i-status-kody.html,
    "/articles/chto-takoe-jwt-avtorizaciya.html,
    "/articles/chto-takoe-keshirovanie.html,
    "/articles/kak-rabotaet-kompilyator-i-interpretator.html,
    "/articles/algoritmy-i-struktury-dannyh.html,
    "/articles/chto-takoe-rest-i-graphql.html,
    "/articles/chto-takoe-vpn.html,
    "/articles/oop-prostymi-slovami.html,
    "/articles/kak-rabotaet-dns.html,
    "/articles/kak-sozdat-telegram-bota.html,
    "/articles/chto-takoe-devops-ci-cd-deploy.html,
    "/articles/scrum-i-agile-prostymi-slovami.html,
    "/articles/kak-vybrat-pervyy-yazyk-programmirovaniya.html,
    "/articles/regulyarnye-vyrazheniya-na-praktike.html,
    "/articles/kak-rabotaet-brauzer.html,
    "/articles/modulnye-testy-zachem-nuzhny.html,
    "/articles/chto-takoe-neyroset-posloyam.html
];

// Install: кэшируем основные ресурсы
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS).catch(() => {}))
  );
  self.skipWaiting();
});

// Activate: чистим старый кэш
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

// Fetch: cache-first для статичных ресурсов, network-first для статей
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  // Только GET
  if (event.request.method !== "GET") return;
  // Пропускаем внешние запросы (Prism, GA, Метрика)
  if (url.origin !== location.origin) return;

  // Стратегия: stale-while-revalidate
  event.respondWith(
    caches.match(event.request).then(cached => {
      const fetchPromise = fetch(event.request).then(response => {
        // Кэшируем свежий ответ
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});
