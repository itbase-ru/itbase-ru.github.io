#!/usr/bin/env python3
"""
Ежедневный генератор статей для IT·База.
Запускается GitHub Action (.github/workflows/daily-article.yml) каждый день в 12:00 MSK.

Логика:
1. Читаем articles.js — получаем существующие slug-и
2. Имеем список тем 2026 года → выбираем тему, которой нет
3. Через GitHub Models API (gpt-4o-mini или Llama 3.3 70B) генерируем статью ~1500 слов
4. Парсим ответ → slug, title, excerpt, content (HTML), tags, FAQ
5. Создаём SVG-обложку 1200×630
6. Добавляем статью в articles.js
"""
import json
import os
import re
import sys
import datetime as dt
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES_FILE = ROOT / "data" / "articles.js"
IMG_DIR = ROOT / "img"

# Текущая дата по Москве
TZ_MSK = dt.timezone(dt.timedelta(hours=3))
TODAY = dt.datetime.now(TZ_MSK).date().isoformat()

# ────────────────────────────────────────────────────────────────────
# Список тем 2026 года — пополняемый пул
# ────────────────────────────────────────────────────────────────────
TOPICS = [
    # AI / LLM
    "RAG-системы для production: архитектура и подводные камни",
    "AI-агенты в 2026 году: фреймворки LangGraph, AutoGen, CrewAI",
    "Function calling в LLM: практическое руководство с примерами",
    "Локальные LLM: llama.cpp, Ollama и vLLM — сравнение",
    "Fine-tuning vs RAG vs prompt-engineering: что выбрать",
    "MCP (Model Context Protocol) — стандарт Anthropic для LLM-инструментов",
    "Векторные базы: pgvector, Qdrant, Weaviate, Chroma — обзор",
    "Prompt-инъекции и jailbreak: как защищать LLM-приложения",

    # Frontend / Web
    "React Server Components в 2026: практический разбор",
    "Signals в Angular и Vue: реактивность нового поколения",
    "Astro 5 — контентные сайты на максимум",
    "SolidJS Start — фреймворк для тех, кто устал от React",
    "Qwik и resumability: как работает фреймворк без гидратации",
    "Web Components в 2026 году: стоит ли использовать",
    "CSS Container Queries: полный гайд",
    "View Transitions API: нативные анимации страниц",
    "Tailwind CSS v4 — что нового и как мигрировать",
    "TanStack Query v5: управление серверным состоянием",

    # Backend / Архитектура
    "Bun 1.2 — JavaScript runtime быстрее Node.js",
    "Deno 2 — стоит ли переходить с Node",
    "Hono — минималистичный веб-фреймворк для edge",
    "tRPC v11: end-to-end типобезопасность без кодогенерации",
    "GraphQL-Yoga 5: современный GraphQL-сервер",
    "gRPC-Web: связываем браузер с микросервисами",
    "Event-driven архитектура: NATS, Kafka, RabbitMQ — когда что",
    "CQRS и Event Sourcing: разбор с примером на Python",
    "Temporal Workflow — durable execution для распределённых систем",

    # DevOps / Cloud
    "Terraform 1.10: что нового и лучшие практики",
    "OpenTofu — open-source форк Terraform: стоит ли переходить",
    "ArgoCD vs Flux: GitOps для Kubernetes",
    "Kubernetes Operators: пишем свой оператор на Python",
    "Knative — serverless на Kubernetes",
    "Observability в 2026: OpenTelemetry, Grafana, Tempo, Loki",
    "ContainerD vs CRI-O: runtime для K8s",
    "DevContainers: одинаковое окружение для всей команды",

    # Базы данных
    "DuckDB — аналитическая БД прямо в процессе",
    "ClickHouse для логов: опыт и踩坑и",
    "PostgreSQL 17: что нового (logical replication, partitioning)",
    "MongoDB 8 — изменения под капотом",
    "Redis 8 — vector search и JSON-индексы",
    "SurrealDB — мульти-модельная БД нового поколения",

    # Языки программирования
    "Rust для backend: tokio, axum, sqlx — практический разбор",
    "Go 1.24 — generics зрелые, range-over-func, новые std пакеты",
    "Python 3.13 — free-threaded build, JIT, что нового",
    "TypeScript 5.7 — pattern matching, type predicates",
    "Kotlin 2.1 — K2 compiler, multiplatform",

    # Security / Performance
    "WebAuthn и passkeys: конец паролям",
    "SameSite cookies и CSP в 2026: современные best practices",
    "Core Web Vitals: как пройти в эпоху INP",
    "HTTP/3 и QUIC: почему это важно",

    # Инструменты
    "VS Code в 2026: расширения, которые экономят часы",
    "Neovim как IDE: LSP, treesitter, lazy.nvim",
    "Zed — редактор от создателей Atom",
    "Turborepo 2: монорепо на максимум",
    "Nx 19: монорепо для enterprise",
    "Biome — единый инструмент вместо ESLint+Prettier",

    # Mobile / Desktop
    "React Native 0.77 — New Architecture по умолчанию",
    "Expo SDK 52 — EAS Build, Updates",
    "Tauri 2 — десктоп-приложения на Rust",
    "Flutter 3.27 — Impeller, Material 3",

    # Data / ML engineering
    "DuckDB + dbt: аналитика без хранилища",
    "Polars vs Pandas: benchmark на реальных данных",
    "Airflow 3 — что нового в orchestrator",
    "Dagster — альтернатива Airflow",

    # Карьера / soft skills
    "System Design Interview: разбор типовых задач 2026",
    "Как оценить свою зарплату программисту в 2026",
    "Senior vs Middle: реальные отличия",
    "Code review: как давать фидбек без токсичности",
]


def log(msg: str):
    print(f"[generate_article] {msg}", flush=True)


def read_existing_slugs() -> set[str]:
    """Получить все slug из articles.js"""
    text = ARTICLES_FILE.read_text(encoding="utf-8")
    return set(re.findall(r'slug:\s*"([^"]+)"', text))


def pick_topic(existing: set[str]) -> str:
    """Выбрать первую тему, slug которой не существует"""
    for topic in TOPICS:
        slug = slugify(topic)
        if slug not in existing:
            return topic
    raise RuntimeError("Все темы из пула исчерпаны — нужно добавить новые в TOPICS")


def slugify(text: str) -> str:
    """Транслитерация ru→en и slug-ify"""
    ru_map = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z',
        'и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r',
        'с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh',
        'щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'
    }
    out = []
    for ch in text.lower():
        if ch in ru_map:
            out.append(ru_map[ch])
        elif ch.isalnum():
            out.append(ch)
        elif ch in ' -_':
            out.append('-')
    slug = re.sub(r'-+', '-', ''.join(out)).strip('-')
    # Ограничение длины — slug не больше 60 символов
    if len(slug) > 60:
        slug = slug[:60].rsplit('-', 1)[0]
    return slug


# ────────────────────────────────────────────────────────────────────
# GitHub Models API
# ────────────────────────────────────────────────────────────────────
GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 6000) -> str:
    """Вызвать GitHub Models API. Токен берём из GH_TOKEN env."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN не задан в окружении")

    body = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "response_format": {"type": "text"},
    }

    req = urllib.request.Request(
        GITHUB_MODELS_ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub Models API HTTP {e.code}: {body[:500]}") from e


def generate_article_content(topic: str) -> dict:
    """Сгенерировать статью через LLM. Возвращает dict со всеми полями."""
    system = (
        "Ты — технический писатель для русскоязычного IT-блога IT·База. "
        "Пишешь статьи уровня senior-разработчика: с примерами кода, конкретикой, "
        "без воды. Стиль — дружелюбный, но профессиональный. "
        "Все примеры кода — на подходящем для темы языке (Python/JS/Go/Rust/SQL/YAML). "
        "Структура: H1, введение 2-3 абзаца, 4-6 секций H2 с 2-4 абзацами и примерами кода, "
        "секция FAQ с 3-5 вопросами H3, заключение. "
        "Цель: ~1500 слов. НЕ используй Markdown — только HTML-теги (<p>, <h2>, <h3>, "
        "<pre><code>, <ul><li>, <table>, <blockquote>). "
        "Возвращай ТОЛЬКО JSON с полями: title, excerpt, tags (массив 3-5), "
        "content (HTML-строка), faqs (массив объектов {question, answer})."
    )

    user = (
        f"Напиши статью на тему: «{topic}».\n\n"
        f"Дата публикации: {TODAY}.\n"
        f"Аудитория: русскоязычные разработчики уровней middle/senior.\n\n"
        f"Требования к контенту:\n"
        f"- Заголовок (title) — короткий и цепляющий, без кликбейта\n"
        f"- Excerpt — 1-2 предложения для превью и SEO description\n"
        f"- Content — HTML, ~1500 слов, с примерами кода в <pre><code>...</code></pre>\n"
        f"- FAQ — 3-5 вопросов в формате H3 (внутри content) И отдельный массив faqs\n"
        f"- Все технические термины — поясняй при первом упоминании\n\n"
        f"Верни JSON в формате:\n"
        f'{{"title": "...", "excerpt": "...", "tags": ["...", "..."], '
        f'"content": "<p>...</p>", "faqs": [{{"question": "...", "answer": "..."}}]}}\n\n'
        f"Без markdown, без ```json блоков, без пояснений — только валидный JSON."
    )

    raw = call_llm(system, user, max_tokens=8000)

    # Извлекаем JSON (LLM может обернуть в ```json ... ```)
    m = re.search(r'\{[\s\S]*\}', raw)
    if not m:
        raise RuntimeError("LLM не вернул JSON-объект")
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Невалидный JSON от LLM: {e}\nСырой ответ:\n{raw[:1000]}")

    # Валидация
    for field in ("title", "excerpt", "tags", "content"):
        if field not in data:
            raise RuntimeError(f"В ответе LLM нет поля {field}")

    return data


# ────────────────────────────────────────────────────────────────────
# SVG-обложка
# ────────────────────────────────────────────────────────────────────
ACCENT_COLORS = [
    ("#58a6ff", "#0d1117"),  # синий/тёмный
    ("#f778ba", "#1a1320"),  # розовый/тёмный
    ("#7ee787", "#0f1a14"),  # зелёный/тёмный
    ("#ffa657", "#1a1108"),  # оранжевый/тёмный
    ("#d2a8ff", "#15101f"),  # фиолетовый/тёмный
    ("#79c0ff", "#0a1420"),  # голубой/тёмный
]


def make_cover_svg(slug: str, title: str) -> Path:
    """Создать SVG-обложку 1200×630 в img/{slug}.svg"""
    # Хеш от slug → выбор цвета
    h = sum(ord(c) for c in slug)
    accent, bg = ACCENT_COLORS[h % len(ACCENT_COLORS)]

    # Обрезаем title для обложки (max 60 символов на строку, 2 строки)
    short_title = title[:80]

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg}"/>
      <stop offset="100%" stop-color="{bg}" stop-opacity="0.85"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.6"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect x="0" y="0" width="1200" height="8" fill="url(#accent)"/>
  <circle cx="1080" cy="120" r="80" fill="{accent}" opacity="0.15"/>
  <circle cx="1140" cy="80" r="40" fill="{accent}" opacity="0.1"/>
  <text x="80" y="540" font-family="-apple-system, Segoe UI, Roboto, sans-serif" font-size="28" font-weight="600" fill="{accent}">IT·База</text>
  <text x="80" y="580" font-family="-apple-system, Segoe UI, Roboto, sans-serif" font-size="18" fill="#8b949e">itbase-ru.github.io</text>
  <text x="80" y="180" font-family="-apple-system, Segoe UI, Roboto, sans-serif" font-size="46" font-weight="700" fill="#e6edf3">
    <tspan x="80" dy="0">{_escape_svg(short_title[:50])}</tspan>
    <tspan x="80" dy="60">{_escape_svg(short_title[50:100]) if len(short_title) > 50 else ''}</tspan>
  </text>
  <rect x="80" y="100" width="60" height="6" fill="{accent}"/>
</svg>'''
    path = IMG_DIR / f"{slug}.svg"
    path.write_text(svg, encoding="utf-8")
    return path


def _escape_svg(s: str) -> str:
    """Экранировать спецсимволы XML"""
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;'))


# ────────────────────────────────────────────────────────────────────
# Сборка и вставка в articles.js
# ────────────────────────────────────────────────────────────────────
def estimate_read_time(html: str) -> int:
    """Грубая оценка: 200 слов/мин"""
    text = re.sub(r'<[^>]+>', ' ', html)
    words = len(text.split())
    return max(3, round(words / 200))


def append_article(article: dict):
    """Вставить статью перед закрывающей ];"""
    text = ARTICLES_FILE.read_text(encoding="utf-8")

    new_entry = '''  {
    slug: "%(slug)s",
    title: "%(title)s",
    excerpt: "%(excerpt)s",
    cover: "img/%(slug)s.svg",
    tags: [%(tags)s],
    date: "%(date)s",
    readTime: %(readTime)d,
    content: %(content)s
  },''' % {
        'slug': article['slug'],
        'title': _escape_js(article['title']),
        'excerpt': _escape_js(article['excerpt']),
        'tags': ', '.join(f'"{_escape_js(t)}"' for t in article['tags']),
        'date': article['date'],
        'readTime': article['readTime'],
        'content': _js_string(article['content']),
    }

    # Вставляем перед закрывающей ]
    # Ищем закрывающую скобку: последняя ]; в файле
    idx = text.rfind('\n];')
    if idx == -1:
        idx = text.rfind('];')
    if idx == -1:
        raise RuntimeError("Не нашёл закрывающую ]; в articles.js")

    new_text = text[:idx] + new_entry + '\n' + text[idx:]
    ARTICLES_FILE.write_text(new_text, encoding="utf-8")
    log(f"Статья добавлена в articles.js: {article['slug']}")


def _escape_js(s: str) -> str:
    """Экранировать строку для JS-литерала в двойных кавычках"""
    return (s.replace('\\', '\\\\')
             .replace('"', '\\"')
             .replace('\n', '\\n')
             .replace('\r', '')
             .replace('\t', '\\t'))


def _js_string(s: str) -> str:
    """Создать JS-строковый литерал для content (HTML может содержать что угодно)"""
    return '"' + _escape_js(s) + '"'


# ────────────────────────────────────────────────────────────────────
# Главный поток
# ────────────────────────────────────────────────────────────────────
def main():
    log(f"Сегодня: {TODAY}")

    existing = read_existing_slugs()
    log(f"Существующих статей: {len(existing)}")

    topic = pick_topic(existing)
    slug = slugify(topic)
    log(f"Выбрана тема: {topic}")
    log(f"Slug: {slug}")

    log("Генерация через GitHub Models API...")
    data = generate_article_content(topic)
    log(f"Получен ответ: title='{data['title'][:50]}...', "
        f"content={len(data['content'])} символов")

    # Создаём обложку
    cover = make_cover_svg(slug, data['title'])
    log(f"Обложка: {cover}")

    # Собираем финальный объект статьи
    article = {
        'slug': slug,
        'title': data['title'],
        'excerpt': data['excerpt'],
        'tags': data['tags'][:5],
        'date': TODAY,
        'readTime': estimate_read_time(data['content']),
        'content': data['content'],
    }

    append_article(article)

    # Записываем slug в output для GitHub Action
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], 'a') as f:
            f.write(f"slug={slug}\n")
            f.write(f"title={data['title']}\n")

    log(f"✅ Готово: {slug} ({TODAY})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
