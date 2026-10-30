/* Файл создаётся автоматически скриптом build.py — не редактируй. */
const ARTICLES = [
 {
  "slug": "kak-napisat-rezyume-programmista",
  "title": "Как написать резюме программисту: шаблон + примеры 2026",
  "excerpt": "Практический гайд по резюме разработчика в 2026: структура, саммари, описание опыта с метриками, навыки, дизайн, ATS-формат и типичные ошибки.",
  "cover": "img/resume-cover.svg",
  "tags": [
   "Карьера",
   "Разработка"
  ],
  "date": "2026-10-29",
  "readTime": 12,
  "url": "articles/kak-napisat-rezyume-programmista.html"
 },
 {
  "slug": "tailwind-css-vs-bootstrap",
  "title": "Tailwind CSS vs Bootstrap: что лучше в 2026",
  "excerpt": "Сравнение Tailwind и Bootstrap простыми словами: философия, размер бандла, кривая обучения, экосистема. Поможем выбрать фреймворк под проект.",
  "cover": "img/tailwind-cover.svg",
  "tags": [
   "Веб",
   "CSS"
  ],
  "date": "2026-10-28",
  "readTime": 11,
  "url": "articles/tailwind-css-vs-bootstrap.html"
 },
 {
  "slug": "websocket-vs-sse-vs-polling",
  "title": "WebSocket vs Server-Sent Events vs Long Polling: что когда использовать",
  "excerpt": "Сравнение трёх технологий real-time в вебе: long polling, SSE и WebSocket. Разбираем, что выбрать для чата, уведомлений, ленты и игр. С примерами кода.",
  "cover": "img/ws-sse-cover.svg",
  "tags": [
   "Веб",
   "Сети",
   "Разработка"
  ],
  "date": "2026-10-27",
  "readTime": 10,
  "url": "articles/websocket-vs-sse-vs-polling.html"
 },
 {
  "slug": "postgresql-vs-mysql",
  "title": "PostgreSQL vs MySQL: что выбрать в 2026",
  "excerpt": "Сравнение PostgreSQL и MySQL простыми словами: философия, производительность, JSON, индексы и расширения. Поможем выбрать БД под твой проект.",
  "cover": "img/pg-mysql-cover.svg",
  "tags": [
   "Базы данных",
   "SQL"
  ],
  "date": "2026-10-26",
  "readTime": 14,
  "url": "articles/postgresql-vs-mysql.html"
 },
 {
  "slug": "claude-ai-obzor",
  "title": "Claude AI от Anthropic: обзор, сравнение с ChatGPT, как пользоваться",
  "excerpt": "Обзор Claude AI в 2026 году: где он сильнее ChatGPT, тарифы, работа с длинными документами и кодом. Практический гайд без маркетингового шума.",
  "cover": "img/claude-cover.svg",
  "tags": [
   "ИИ",
   "Инструменты"
  ],
  "date": "2026-10-25",
  "readTime": 11,
  "url": "articles/claude-ai-obzor.html"
 },
 {
  "slug": "nextjs-15-chto-novogo",
  "title": "Next.js 15: что нового, App Router, Server Components",
  "excerpt": "Обзор Next.js 15 простыми словами: чем App Router отличается от Pages, как работают Server Components, зачем Turbopack и где лежат грабли при миграции.",
  "cover": "img/nextjs-cover.svg",
  "tags": [
   "Веб",
   "JavaScript"
  ],
  "date": "2026-10-24",
  "readTime": 13,
  "url": "articles/nextjs-15-chto-novogo.html"
 },
 {
  "slug": "rust-vs-go-sravnenie",
  "title": "Rust vs Go: какой язык учить в 2026",
  "excerpt": "Сравнение Rust и Go простыми словами: философия, управление памятью, параллелизм, где использовать каждый язык. Поможем выбрать под твою задачу и карьеру.",
  "cover": "img/rust-go-cover.svg",
  "tags": [
   "Разработка",
   "Карьера"
  ],
  "date": "2026-10-23",
  "readTime": 12,
  "url": "articles/rust-vs-go-sravnenie.html"
 },
 {
  "slug": "kubernetes-dlya-novichka",
  "title": "Kubernetes для новичка: поды, деплойменты, сервисы за 15 минут",
  "excerpt": "Объяснение Kubernetes простыми словами: что такое поды, деплойменты и сервисы, зачем они нужны и как написать первый манифест. Без воды и без заумных терминов.",
  "cover": "img/kubernetes-cover.svg",
  "tags": [
   "DevOps",
   "Инструменты"
  ],
  "date": "2026-10-22",
  "readTime": 15,
  "url": "articles/kubernetes-dlya-novichka.html"
 },
 {
  "slug": "github-copilot-obzor",
  "title": "GitHub Copilot: обзор, цена, сравнение с альтернативами",
  "excerpt": "Что умеет GitHub Copilot в 2026 году, сколько стоит и стоит ли переключаться на Cursor, Codeium и Tabnine. Реальные сценарии, где ИИ-ассистент помогает и мешает.",
  "cover": "img/copilot-cover.svg",
  "tags": [
   "ИИ",
   "Инструменты",
   "Разработка"
  ],
  "date": "2026-10-21",
  "readTime": 10,
  "url": "articles/github-copilot-obzor.html"
 },
 {
  "slug": "chatgpt-kak-polzovatsya",
  "title": "ChatGPT: как пользоваться, промпты, лайфхаки",
  "excerpt": "Практический гайд по ChatGPT в 2026 году: тарифы, промпт-инжиниринг простыми словами, лайфхаки и ловушки, в которые попадают новички.",
  "cover": "img/chatgpt-cover.svg",
  "tags": [
   "ИИ",
   "Инструменты"
  ],
  "date": "2026-10-20",
  "readTime": 12,
  "url": "articles/chatgpt-kak-polzovatsya.html"
 },
 {
  "slug": "paginaciya-i-versirovanie-api",
  "title": "Пагинация и версионирование API — как не сломать клиентов",
  "excerpt": "Как отдавать тысячи записей постранично и что делать, когда API меняется. Разбираем offset/limit, cursor-пагинацию и версионирование.",
  "cover": "img/api-versioning.svg",
  "tags": [
   "API",
   "Веб",
   "Разработка"
  ],
  "date": "2026-04-27",
  "readTime": 11,
  "url": "articles/paginaciya-i-versirovanie-api.html"
 },
 {
  "slug": "chto-takoe-nginx",
  "title": "Что такое Nginx и зачем он нужен на сервере",
  "excerpt": "Почему почти все сайты работают через Nginx. Разбираем: веб-сервер, reverse proxy, балансировка нагрузки, статика и конфиги.",
  "cover": "img/nginx.svg",
  "tags": [
   "DevOps",
   "Веб",
   "Инструменты"
  ],
  "date": "2026-04-26",
  "readTime": 10,
  "url": "articles/chto-takoe-nginx.html"
 },
 {
  "slug": "bash-skripty-dlya-novichka",
  "title": "Bash-скрипты для новичка — автоматизация на Linux",
  "excerpt": "Как написать первый скрипт, который автоматизирует рутину: переменные, условия, циклы, функции, аргументы командной строки.",
  "cover": "img/bash.svg",
  "tags": [
   "Инструменты",
   "DevOps",
   "Разработка"
  ],
  "date": "2026-04-25",
  "readTime": 11,
  "url": "articles/bash-skripty-dlya-novichka.html"
 },
 {
  "slug": "obrabotka-isklyucheniy-v-python",
  "title": "Обработка исключений в Python — try, except, finally",
  "excerpt": "Как ловить ошибки и не давать программе падать. Разбираем try/except, собственные исключения и контекстные менеджеры с примерами.",
  "cover": "img/python-errors.svg",
  "tags": [
   "Python",
   "Разработка",
   "Теория"
  ],
  "date": "2026-04-24",
  "readTime": 11,
  "url": "articles/obrabotka-isklyucheniy-v-python.html"
 },
 {
  "slug": "dizayn-patterns-singleton-factory-observer",
  "title": "Дизайн-паттерны — Singleton, Factory, Observer",
  "excerpt": "Три самых частых паттерна проектирования. Разбираем на примерах: зачем нужны, как устроены и где применяются в реальном коде.",
  "cover": "img/patterns.svg",
  "tags": [
   "Разработка",
   "Архитектура",
   "Теория"
  ],
  "date": "2026-04-23",
  "readTime": 11,
  "url": "articles/dizayn-patterns-singleton-factory-observer.html"
 },
 {
  "slug": "cookie-localstorage-sessionstorage",
  "title": "Cookie, localStorage и sessionStorage — что выбрать",
  "excerpt": "Три способа хранить данные в браузере. Разбираем разницу, лимиты, безопасность и когда что использовать — на конкретных примерах.",
  "cover": "img/storage.svg",
  "tags": [
   "Веб",
   "JavaScript",
   "Безопасность"
  ],
  "date": "2026-04-22",
  "readTime": 10,
  "url": "articles/cookie-localstorage-sessionstorage.html"
 },
 {
  "slug": "tranzakcii-i-acid",
  "title": "Транзакции в базах данных — ACID простыми словами",
  "excerpt": "Почему при переводе денег нельзя потерять ни копейки. Разбираем транзакции и четыре их свойства: атомарность, согласованность, изоляцию, надёжность.",
  "cover": "img/tranzakcii.svg",
  "tags": [
   "Базы данных",
   "SQL",
   "Теория"
  ],
  "date": "2026-04-21",
  "readTime": 11,
  "url": "articles/tranzakcii-i-acid.html"
 },
 {
  "slug": "python-s-nulya",
  "title": "Python с нуля — базовый синтаксис за 15 минут",
  "excerpt": "Переменные, типы, условия, циклы, функции и списки. Минимальный набор, с которого начинается любой Python-проект.",
  "cover": "img/python.svg",
  "tags": [
   "Python",
   "Разработка",
   "Теория"
  ],
  "date": "2026-04-20",
  "readTime": 12,
  "url": "articles/python-s-nulya.html"
 },
 {
  "slug": "dekoratory-v-python",
  "title": "Декораторы в Python — что это и зачем нужны",
  "excerpt": "Функции, которые оборачивают другие функции. Разбираем декораторы с нуля: синтаксис, как работают, где применяются на практике.",
  "cover": "img/decorators.svg",
  "tags": [
   "Python",
   "Разработка",
   "Теория"
  ],
  "date": "2026-04-19",
  "readTime": 11,
  "url": "articles/dekoratory-v-python.html"
 },
 {
  "slug": "docker-compose-dlya-proekta",
  "title": "Docker Compose — несколько контейнеров одной командой",
  "excerpt": "Когда одного Dockerfile мало: как описать приложение, базу и кэш в одном файле и запускать всё одной командой docker compose up.",
  "cover": "img/compose.svg",
  "tags": [
   "DevOps",
   "Инструменты",
   "Разработка"
  ],
  "date": "2026-04-18",
  "readTime": 10,
  "url": "articles/docker-compose-dlya-proekta.html"
 },
 {
  "slug": "chto-takoe-cors",
  "title": "Что такое CORS и почему браузер блокирует запросы",
  "excerpt": "Почему fetch с одного сайта на другой падает с ошибкой, что такое Same-Origin Policy и как правильно настроить CORS на сервере.",
  "cover": "img/cors.svg",
  "tags": [
   "Веб",
   "Безопасность",
   "API"
  ],
  "date": "2026-04-17",
  "readTime": 10,
  "url": "articles/chto-takoe-cors.html"
 },
 {
  "slug": "heshirovanie-paroley",
  "title": "Как правильно хранить пароли — хеширование и соль",
  "excerpt": "Почему нельзя хранить пароли в открытом виде, чем MD5 хуже bcrypt и что такое соль. Разбираем на примерах кода.",
  "cover": "img/passwords.svg",
  "tags": [
   "Безопасность",
   "Разработка",
   "Теория"
  ],
  "date": "2026-04-16",
  "readTime": 10,
  "url": "articles/heshirovanie-paroley.html"
 },
 {
  "slug": "xss-csrf-sql-inekcii",
  "title": "XSS, CSRF, SQL-инъекции — три главные атаки на веб",
  "excerpt": "Разбираем три самых частых уязвимости в веб-приложениях: как работают, чем опасны и как защититься. С примерами атак и защиты.",
  "cover": "img/security.svg",
  "tags": [
   "Безопасность",
   "Веб",
   "Разработка"
  ],
  "date": "2026-04-15",
  "readTime": 12,
  "url": "articles/xss-csrf-sql-inekcii.html"
 },
 {
  "slug": "kak-rabotaet-websocket",
  "title": "Как работает WebSocket — real-time связь между браузером и сервером",
  "excerpt": "Почему обычный HTTP плохо подходит для чатов, игр и бирж. Разбираем WebSocket: handshake, кадры, когда нужен и какие есть альтернативы.",
  "cover": "img/websocket.svg",
  "tags": [
   "Веб",
   "Сети",
   "Разработка"
  ],
  "date": "2026-04-14",
  "readTime": 10,
  "url": "articles/kak-rabotaet-websocket.html"
 },
 {
  "slug": "chto-takoe-orm",
  "title": "Что такое ORM — работа с базой через объекты",
  "excerpt": "Зачем писать SQL, если можно работать с базой как с обычными объектами. Разбираем ORM: как работает, плюсы и минусы, примеры на SQLAlchemy.",
  "cover": "img/orm.svg",
  "tags": [
   "Базы данных",
   "Разработка",
   "Python"
  ],
  "date": "2026-04-13",
  "readTime": 10,
  "url": "articles/chto-takoe-orm.html"
 },
 {
  "slug": "mnogopotochnost-v-python-gil",
  "title": "Многопоточность в Python — GIL и потоки",
  "excerpt": "Почему потоки в Python не ускоряют вычисления, что такое GIL и когда всё-таки стоит использовать threading, multiprocessing или asyncio.",
  "cover": "img/threading.svg",
  "tags": [
   "Python",
   "Разработка",
   "Теория"
  ],
  "date": "2026-04-12",
  "readTime": 11,
  "url": "articles/mnogopotochnost-v-python-gil.html"
 },
 {
  "slug": "zachem-nuzhen-typescript",
  "title": "Зачем нужен TypeScript, если есть JavaScript",
  "excerpt": "Типы, интерфейсы, компиляция — разбираем, что даёт TypeScript, кому он нужен и почему крупные проекты уходят на него.",
  "cover": "img/typescript.svg",
  "tags": [
   "TypeScript",
   "JavaScript",
   "Разработка"
  ],
  "date": "2026-04-11",
  "readTime": 10,
  "url": "articles/zachem-nuzhen-typescript.html"
 },
 {
  "slug": "asinhronnost-v-python",
  "title": "Асинхронность в Python — asyncio простыми словами",
  "excerpt": "async, await, event loop, задачи и корутины. Разбираем, зачем нужна асинхронность в Python, где она помогает и где только мешает.",
  "cover": "img/asyncio.svg",
  "tags": [
   "Python",
   "Разработка",
   "Теория"
  ],
  "date": "2026-04-10",
  "readTime": 11,
  "url": "articles/asinhronnost-v-python.html"
 },
 {
  "slug": "indeksy-v-bazah-dannyh",
  "title": "Индексы в базах данных — зачем и как работают",
  "excerpt": "Почему один и тот же SQL-запрос может выполняться 10 мс или 10 секунд. Разбираем индексы: B-tree, составные, покрывающие и когда они вредят.",
  "cover": "img/indeksy.svg",
  "tags": [
   "Базы данных",
   "SQL",
   "Разработка"
  ],
  "date": "2026-04-09",
  "readTime": 11,
  "url": "articles/indeksy-v-bazah-dannyh.html"
 },
 {
  "slug": "git-vetki-i-sliyanie",
  "title": "Git ветки и слияния — branch, merge, rebase",
  "excerpt": "Как работать с ветками в Git: создавать, переключаться, сливать, разрешать конфликты. Разбираем merge и rebase — когда что использовать.",
  "cover": "img/git-vetki.svg",
  "tags": [
   "Git",
   "Инструменты",
   "Разработка"
  ],
  "date": "2026-04-08",
  "readTime": 11,
  "url": "articles/git-vetki-i-sliyanie.html"
 },
 {
  "slug": "sql-zaprosy-s-nulya",
  "title": "SQL-запросы с нуля — SELECT, WHERE, JOIN",
  "excerpt": "Разбираем SQL на практике: как выбрать данные, отфильтровать, отсортировать, соединить таблицы. С примерами на реальных задачах интернет-магазина.",
  "cover": "img/sql.svg",
  "tags": [
   "Базы данных",
   "SQL",
   "Разработка"
  ],
  "date": "2026-04-07",
  "readTime": 12,
  "url": "articles/sql-zaprosy-s-nulya.html"
 },
 {
  "slug": "osnovy-linux-dlya-razrabotchika",
  "title": "Основы Linux для разработчика — базовые команды",
  "excerpt": "Что нужно знать про Linux, чтобы работать на сервере. Разбираем навигацию по файлам, права доступа, процессы, SSH и полезные команды с примерами.",
  "cover": "img/linux.svg",
  "tags": [
   "Инструменты",
   "DevOps",
   "Теория"
  ],
  "date": "2026-04-06",
  "readTime": 11,
  "url": "articles/osnovy-linux-dlya-razrabotchika.html"
 },
 {
  "slug": "monolit-i-mikroservisy",
  "title": "Монолит и микросервисы — когда что выбирать",
  "excerpt": "Разбираем без хайпа: что такое монолит, микросервисы, зачем они нужны, какие проблемы решают и какие создают. Спойлер: микросервисы — не всегда лучше.",
  "cover": "img/mikroservisy.svg",
  "tags": [
   "Разработка",
   "Архитектура",
   "DevOps"
  ],
  "date": "2026-04-05",
  "readTime": 11,
  "url": "articles/monolit-i-mikroservisy.html"
 },
 {
  "slug": "http-metody-i-status-kody",
  "title": "HTTP-методы и статус-коды — шпаргалка с примерами",
  "excerpt": "GET, POST, PUT, PATCH, DELETE и что значат все эти 200, 301, 404, 500. Разбираем HTTP по-человечески, с примерами запросов и ответов.",
  "cover": "img/http.svg",
  "tags": [
   "Веб",
   "API",
   "Теория"
  ],
  "date": "2026-04-04",
  "readTime": 10,
  "url": "articles/http-metody-i-status-kody.html"
 },
 {
  "slug": "chto-takoe-jwt-avtorizaciya",
  "title": "Что такое JWT и как работает авторизация",
  "excerpt": "JWT — это токен, который заменяет куки-сессии. Разбираем структуру, подпись, срок жизни и типичные ошибки при работе с токенами.",
  "cover": "img/jwt.svg",
  "tags": [
   "Веб",
   "Безопасность",
   "API"
  ],
  "date": "2026-04-03",
  "readTime": 10,
  "url": "articles/chto-takoe-jwt-avtorizaciya.html"
 },
 {
  "slug": "chto-takoe-keshirovanie",
  "title": "Что такое кэширование и зачем оно нужно",
  "excerpt": "Кэш — одна из главных идей в IT. Разбираем, какие бывают уровни кэша, что такое TTL, инвалидация, и почему кэш может всё сломать.",
  "cover": "img/cache.svg",
  "tags": [
   "Разработка",
   "Веб",
   "DevOps"
  ],
  "date": "2026-04-02",
  "readTime": 10,
  "url": "articles/chto-takoe-keshirovanie.html"
 },
 {
  "slug": "kak-rabotaet-kompilyator-i-interpretator",
  "title": "Как работает компилятор и интерпретатор",
  "excerpt": "Почему Python медленнее C, а JavaScript работает в браузере, хотя он интерпретируемый. Разбираем компиляцию, интерпретацию и JIT.",
  "cover": "img/kompilyator.svg",
  "tags": [
   "Разработка",
   "Теория",
   "Инструменты"
  ],
  "date": "2026-04-01",
  "readTime": 10,
  "url": "articles/kak-rabotaet-kompilyator-i-interpretator.html"
 },
 {
  "slug": "algoritmy-i-struktury-dannyh",
  "title": "Алгоритмы и структуры данных — с чего начать",
  "excerpt": "Зачем программисту знать про массивы, списки, деревья и хеш-таблицы. Разбираем базовые структуры и алгоритмы на понятных примерах.",
  "cover": "img/algoritmy.svg",
  "tags": [
   "Разработка",
   "Теория",
   "Карьера"
  ],
  "date": "2026-03-31",
  "readTime": 11,
  "url": "articles/algoritmy-i-struktury-dannyh.html"
 },
 {
  "slug": "chto-takoe-rest-i-graphql",
  "title": "REST и GraphQL — в чём разница",
  "excerpt": "Два главных подхода к построению API. Разбираем на примерах: когда REST удобнее, а когда GraphQL решает проблемы, которые REST создаёт.",
  "cover": "img/rest-graphql.svg",
  "tags": [
   "Веб",
   "API",
   "Теория"
  ],
  "date": "2026-03-30",
  "readTime": 10,
  "url": "articles/chto-takoe-rest-i-graphql.html"
 },
 {
  "slug": "chto-takoe-vpn",
  "title": "Что такое VPN и как он работает",
  "excerpt": "VPN — это не только «обход блокировок». Разбираем, как устроен туннель, что видит провайдер, какие бывают протоколы и где VPN не поможет.",
  "cover": "img/vpn.svg",
  "tags": [
   "Безопасность",
   "Сети",
   "Теория"
  ],
  "date": "2026-03-29",
  "readTime": 9,
  "url": "articles/chto-takoe-vpn.html"
 },
 {
  "slug": "oop-prostymi-slovami",
  "title": "ООП простыми словами — классы, объекты, наследование",
  "excerpt": "Инкапсуляция, наследование, полиморфизм и абстракция — четыре слова, которые пугают новичков. Разбираем на понятных примерах без умных терминов.",
  "cover": "img/oop.svg",
  "tags": [
   "Разработка",
   "Теория"
  ],
  "date": "2026-03-28",
  "readTime": 10,
  "url": "articles/oop-prostymi-slovami.html"
 },
 {
  "slug": "kak-rabotaet-dns",
  "title": "Как работает DNS — простыми словами",
  "excerpt": "Что происходит за секунду между вводом адреса в браузере и загрузкой сайта. Разбираем DNS: корневые серверы, зоны, кэш и типы записей.",
  "cover": "img/dns.svg",
  "tags": [
   "Веб",
   "Сети",
   "Теория"
  ],
  "date": "2026-03-27",
  "readTime": 9,
  "url": "articles/kak-rabotaet-dns.html"
 },
 {
  "slug": "kak-sozdat-telegram-bota",
  "title": "Как создать Telegram-бота с кодом",
  "excerpt": "Пошагово: от BotFather и токена до рабочего бота на Python с командами, кнопками и запуском на сервере.",
  "cover": "img/kak-sozdat-telegram-bota.svg",
  "tags": [
   "Разработка",
   "Python",
   "Инструменты"
  ],
  "date": "2026-03-26",
  "readTime": 12,
  "url": "articles/kak-sozdat-telegram-bota.html"
 },
 {
  "slug": "chto-takoe-devops-ci-cd-deploy",
  "title": "Что такое DevOps — CI/CD и деплой простыми словами",
  "excerpt": "Разбираем по-человечески: что такое DevOps, зачем нужны CI и CD, как выглядит pipeline и какие бывают способы деплоя.",
  "cover": "img/chto-takoe-devops-ci-cd-deploy.svg",
  "tags": [
   "DevOps",
   "Теория",
   "Инструменты"
  ],
  "date": "2026-03-25",
  "readTime": 10,
  "url": "articles/chto-takoe-devops-ci-cd-deploy.html"
 },
 {
  "slug": "scrum-i-agile-prostymi-slovami",
  "title": "Scrum и Agile простыми словами",
  "excerpt": "Agile, Scrum, спринт, стендап, Kanban — разбираем, что за этими словами стоит на самом деле, без корпоративного тумана и коучей.",
  "cover": "img/scrum-i-agile-prostymi-slovami.svg",
  "tags": [
   "Разработка",
   "Теория"
  ],
  "date": "2026-03-24",
  "readTime": 8,
  "url": "articles/scrum-i-agile-prostymi-slovami.html"
 },
 {
  "slug": "kak-vybrat-pervyy-yazyk-programmirovaniya",
  "title": "Как выбрать первый язык программирования",
  "excerpt": "Python, JavaScript, Java или Go? Разбираем без холиваров: как выбрать первый язык под свою цель, что важно и что вообще не имеет значения.",
  "cover": "img/kak-vybrat-pervyy-yazyk-programmirovaniya.svg",
  "tags": [
   "Карьера",
   "Теория",
   "Разработка"
  ],
  "date": "2026-03-23",
  "readTime": 9,
  "url": "articles/kak-vybrat-pervyy-yazyk-programmirovaniya.html"
 },
 {
  "slug": "regulyarnye-vyrazheniya-na-praktike",
  "title": "Регулярные выражения: практический разбор с примерами",
  "excerpt": "Что это такое, зачем они нужны, как читать «страшные» строки вроде ^\\d{3}-\\d{2}$ и применять в реальных задачах.",
  "cover": "img/regex-cover.svg",
  "tags": [
   "Разработка",
   "Инструменты"
  ],
  "date": "2026-03-21",
  "readTime": 12,
  "url": "articles/regulyarnye-vyrazheniya-na-praktike.html"
 },
 {
  "slug": "kak-rabotaet-brauzer",
  "title": "Как работает браузер: DOM, парсинг и рендеринг",
  "excerpt": "Что происходит между нажатием Enter и появлением страницы. Разбираю путь: HTML → DOM → CSSOM → рендер-дерево → пиксели.",
  "cover": "img/browser-cover.svg",
  "tags": [
   "Веб",
   "Теория"
  ],
  "date": "2026-03-19",
  "readTime": 11,
  "url": "articles/kak-rabotaet-brauzer.html"
 },
 {
  "slug": "modulnye-testy-zachem-nuzhny",
  "title": "Модульные тесты: зачем они нужны и как их писать",
  "excerpt": "Почему программисты пишут код, который проверяет код. Разбираю на примерах: что такое юнит-тесты, зачем они нужны и как начать без боли.",
  "cover": "img/tests-cover.svg",
  "tags": [
   "Разработка",
   "Тестирование"
  ],
  "date": "2026-03-17",
  "readTime": 10,
  "url": "articles/modulnye-testy-zachem-nuzhny.html"
 },
 {
  "slug": "chto-takoe-neyroset-posloyam",
  "title": "Что такое нейросеть: разбор по слоям без формул",
  "excerpt": "Как устроен искусственный нейрон, зачем нужны слои, веса и функции активации. Разбираю архитектуру на пальцах и показываю мини-сеть на Python.",
  "cover": "img/neural-cover.svg",
  "tags": [
   "ИИ",
   "Теория"
  ],
  "date": "2026-03-15",
  "readTime": 12,
  "url": "articles/chto-takoe-neyroset-posloyam.html"
 },
 {
  "slug": "api-klyuch-kak-ne-слить",
  "title": "API-ключ: что это и как не слить его в GitHub",
  "excerpt": "Что такое токены, чем они опасны и почему одна строка в публичном репозитории может стоить тысячи долларов. Правила, которые спасают.",
  "cover": "img/apikey-cover.svg",
  "tags": [
   "Безопасность",
   "Разработка"
  ],
  "date": "2026-03-13",
  "readTime": 9,
  "url": "articles/api-klyuch-kak-ne-slit.html"
 },
 {
  "slug": "asinhronnost-v-javascript",
  "title": "Асинхронность в JavaScript: промисы и async/await",
  "excerpt": "Почему JavaScript не может просто подождать, что такое промисы, как работает async/await и почему fetch — асинхронный.",
  "cover": "img/async-cover.svg",
  "tags": [
   "JavaScript",
   "Веб"
  ],
  "date": "2026-03-11",
  "readTime": 11,
  "url": "articles/asinhronnost-v-javascript.html"
 },
 {
  "slug": "javascript-massivy-i-obekty",
  "title": "Массивы и объекты в JavaScript: полный разбор с примерами",
  "excerpt": "Как хранить списки и структурированные данные, какие методы массивов нужны в реальной работе и чем объект отличается от массива.",
  "cover": "img/arrays-cover.svg",
  "tags": [
   "JavaScript",
   "Веб"
  ],
  "date": "2026-03-09",
  "readTime": 12,
  "url": "articles/javascript-massivy-i-obekty.html"
 },
 {
  "slug": "kak-pisat-chistyy-kod",
  "title": "Как писать чистый код: 8 принципов, которые отличают новичка",
  "excerpt": "Разбор на примерах: почему код пишут для людей, а не для машин, что такое DRY, KISS, YAGNI и как одна маленькая привычка экономит часы.",
  "cover": "img/cleancode-cover.svg",
  "tags": [
   "Разработка",
   "Теория"
  ],
  "date": "2026-03-07",
  "readTime": 11,
  "url": "articles/kak-pisat-chistyy-kod.html"
 },
 {
  "slug": "chto-takoe-oblako",
  "title": "Что такое облако: IaaS, PaaS, SaaS и почему это удобно",
  "excerpt": "Разбираю на пальцах: чем облако отличается от обычного хостинга, что такое AWS S3 и Lambda, и когда выгоднее арендовать, а не покупать.",
  "cover": "img/cloud-cover.svg",
  "tags": [
   "Cloud",
   "DevOps"
  ],
  "date": "2026-03-05",
  "readTime": 9,
  "url": "articles/chto-takoe-oblako.html"
 },
 {
  "slug": "kak-rabotaet-poisk-v-google",
  "title": "Как работает поиск в Google: краулеры, индекс и ранжирование",
  "excerpt": "Что происходит за миллисекунды между нажатием Enter и списком результатов: как роботы обходят сайты, как строится индекс и почему одни страницы выше других.",
  "cover": "img/google-cover.svg",
  "tags": [
   "SEO",
   "Веб"
  ],
  "date": "2026-03-03",
  "readTime": 10,
  "url": "articles/kak-rabotaet-poisk-v-google.html"
 },
 {
  "slug": "docker-za-10-minut",
  "title": "Docker за 10 минут: зачем нужны контейнеры",
  "excerpt": "Проблема «у меня работает, а у тебя нет» и как Docker её решает. Образ, контейнер, Dockerfile — на пальцах.",
  "cover": "img/docker-cover.svg",
  "tags": [
   "Инструменты",
   "DevOps"
  ],
  "date": "2026-03-01",
  "readTime": 9,
  "url": "articles/docker-za-10-minut.html"
 },
 {
  "slug": "kak-rabotaet-https",
  "title": "Как работает HTTPS: шифрование простыми словами",
  "excerpt": "Почему сайты без HTTPS уже вне закона, что такое TLS, сертификат и почему замок в адресной строке — это не просто иконка.",
  "cover": "img/https-cover.svg",
  "tags": [
   "Безопасность",
   "Веб"
  ],
  "date": "2026-02-28",
  "readTime": 8,
  "url": "articles/kak-rabotaet-https.html"
 },
 {
  "slug": "sql-vs-nosql",
  "title": "SQL vs NoSQL: какую базу данных выбрать",
  "excerpt": "Разница между реляционными и нереляционными базами, где какие применяются и как не прогадать с выбором под свой проект.",
  "cover": "img/db-cover.svg",
  "tags": [
   "Базы данных",
   "Теория"
  ],
  "date": "2026-02-26",
  "readTime": 9,
  "url": "articles/sql-vs-nosql.html"
 },
 {
  "slug": "javascript-peremennye-i-tipy",
  "title": "JavaScript: переменные и типы данных простыми словами",
  "excerpt": "Чем отличается let от const, какие в JS бывают типы данных, зачем нужны строки, числа и объекты — с примерами и разбором ошибок.",
  "cover": "img/js-cover.svg",
  "tags": [
   "Веб",
   "JavaScript"
  ],
  "date": "2026-02-24",
  "readTime": 10,
  "url": "articles/javascript-peremennye-i-tipy.html"
 },
 {
  "slug": "css-flexbox-vs-grid",
  "title": "CSS: Flexbox против Grid — когда что использовать",
  "excerpt": "Два инструмента для раскладки элементов. Объясняю разницу, показываю примеры и говорю прямо: бери это, а не то.",
  "cover": "img/css-cover.svg",
  "tags": [
   "Веб",
   "CSS"
  ],
  "date": "2026-02-22",
  "readTime": 8,
  "url": "articles/css-flexbox-vs-grid.html"
 },
 {
  "slug": "html-s-nulya",
  "title": "HTML с нуля: как устроена любая веб-страница",
  "excerpt": "Что такое HTML, зачем нужны теги, что означает семантическая разметка и как собрать первую страницу с нуля.",
  "cover": "img/html-cover.svg",
  "tags": [
   "Веб",
   "HTML"
  ],
  "date": "2026-02-20",
  "readTime": 9,
  "url": "articles/html-s-nulya.html"
 },
 {
  "slug": "terminal-dlya-novichka",
  "title": "Терминал для новичка: 20 команд, которые нужны каждый день",
  "excerpt": "Почему программисты работают в чёрном окне с текстом и какие команды нужно знать, чтобы не бояться командной строки.",
  "cover": "img/terminal-cover.svg",
  "tags": [
   "Инструменты",
   "Теория"
  ],
  "date": "2026-02-18",
  "readTime": 9,
  "url": "articles/terminal-dlya-novichka.html"
 },
 {
  "slug": "chto-takoe-api",
  "title": "Что такое API за 5 минут: понятное объяснение с примерами",
  "excerpt": "API — это способ одной программы попросить что-то у другой. Разбираю на примере официанта в кафе и показываю рабочие примеры запросов.",
  "cover": "img/api-cover.svg",
  "tags": [
   "Веб",
   "Теория"
  ],
  "date": "2026-02-16",
  "readTime": 7,
  "url": "articles/chto-takoe-api.html"
 },
 {
  "slug": "kak-uchitsya-programmirovaniyu-s-nulya",
  "title": "Как учиться программированию с нуля в 2026 году",
  "excerpt": "Пошаговый план: с чего начать, сколько времени нужно, какие ошибки совершают почти все и как не бросить на полпути.",
  "cover": "img/learn-cover.svg",
  "tags": [
   "Карьера",
   "Теория"
  ],
  "date": "2026-02-14",
  "readTime": 10,
  "url": "articles/kak-uchitsya-programmirovaniyu-s-nulya.html"
 },
 {
  "slug": "chto-takoe-iskusstvennyy-intellekt",
  "title": "Что такое искусственный интеллект: разбор с нуля",
  "excerpt": "Объясняю простыми словами, чем ИИ отличается от обычной программы, какие бывают типы ИИ и как он реально работает — без магии и заумных терминов.",
  "cover": "img/ai-cover.svg",
  "tags": [
   "ИИ",
   "Теория"
  ],
  "date": "2026-02-10",
  "readTime": 8,
  "url": "articles/chto-takoe-iskusstvennyy-intellekt.html"
 },
 {
  "slug": "git-dlya-novichkov",
  "title": "Git для новичков: 10 команд, которых хватит в 90% случаев",
  "excerpt": "Что такое система контроля версий, зачем она нужна и какой минимум команд нужно выучить, чтобы не бояться сломать проект.",
  "cover": "img/git-cover.svg",
  "tags": [
   "Git",
   "Инструменты"
  ],
  "date": "2026-02-05",
  "readTime": 6,
  "url": "articles/git-dlya-novichkov.html"
 }
];
