#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — сборка сайта IT·База.

Что делает (запускается сам через GitHub Actions при каждом сохранении):
  1. Читает data/articles.js (твоё хранилище статей — его по-прежнему правишь ты).
  2. Для КАЖДОЙ статьи создаёт готовую страницу articles/<адрес>.html
     (заголовок, описание, canonical, Open Graph, JSON-LD, оглавление, похожие).
  3. Создаёт data/index.js — лёгкий список статей без текста (для поиска и закладок).
  4. Пересобирает sitemap.xml.
  5. Вставляет карточки статей прямо в index.html (между маркерами GRID_START/END).
  6. Дописывает canonical / Open Graph в служебные страницы (about, contacts...).
  7. Рисует картинки для превью в соцсетях img/og/*.png (если есть шрифт и Pillow).
  8. Удаляет «мёртвые» партнёрские блоки с заглушкой ССЫЛКА_НА_ПАРТНЁРКУ.

Новая статья = новый объект в data/articles.js. Больше ничего делать не нужно.
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

# ----------------------------- НАСТРОЙКИ ------------------------------------
SITE = "https://itbase-ru.github.io"   # адрес сайта БЕЗ слэша в конце
SITE_NAME = "IT·База"                  # название сайта
AUTHOR_NAME = "IT·База"                # автор в микроразметке (можно своё имя)
CONTACT_EMAIL = "kirillfomichev05@mail.ru"
FORCE_OG = False                       # True = перерисовать все OG-картинки

# ─── Монетизация и аналитика (вкл/выкл через переменные окружения в GitHub Secrets) ───
YANDEX_METRIKA_ID = os.environ.get("YANDEX_METRIKA_ID", "")  # например "12345678"
GOOGLE_ANALYTICS_ID = os.environ.get("GOOGLE_ANALYTICS_ID", "")  # например "G-XXXXXXX"
YANDEX_RSY_BLOCK_ID = os.environ.get("YANDEX_RSY_BLOCK_ID", "")  # ID блока РСЯ, напр. "R-A-123456-1"
DONATE_BOOSTY_URL  = os.environ.get("DONATE_BOOSTY_URL", "")  # пусто — кнопка не показывается
DONATE_TG_URL      = os.environ.get("DONATE_TG_URL", "https://t.me/itbase_bot")
DONATE_YOOMONEY    = os.environ.get("DONATE_YOOMONEY", "")  # напр. "https://yoomoney.ru/to/4100123456789"
TG_CHANNEL_URL     = os.environ.get("TG_CHANNEL_URL", "https://t.me/itbase")  # для кнопки в шапке/футере
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
YEAR = datetime.date.today().year

THEME_SCRIPT = """<script>
    (function(){
      try{
        var t = localStorage.getItem('itbase_theme');
        if (t) document.documentElement.setAttribute('data-theme', t);
      }catch(e){}
    })();
  </script>"""

ICONS = """<link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">"""

HEADER = """<header class="site-header">
    <div class="site-header__inner">
      <a href="/" class="logo">IT<span>·</span>База</a>
      <button class="theme-toggle" id="themeToggle" title="Сменить тему" aria-label="Сменить тему">☾</button>
    </div>
  </header>"""

FOOTER = f"""<footer class="site-footer">
  <div class="site-footer__inner">
    <span>© <span id="year">{YEAR}</span> IT·База</span>
    <a href="/about.html">О сайте</a>
    <a href="/top.html">Лучшее</a>
    <a href="/archive.html">Архив</a>
    <a href="/sitemap.html">Карта</a>
    <a href="/support.html">Поддержать ★</a>
    <a href="/privacy.html">Политика</a>
    <a href="/bookmarks.html" style="margin-left:auto;color:var(--accent)">★ Закладки</a>
  </div>
</footer>"""


# ─── Аналитика: Яндекс.Метрика и Google Analytics ─────────────────────────
def analytics_snippet():
    """Возвращает HTML-код счётчиков, если ID заданы в переменных окружения."""
    parts = []
    if YANDEX_METRIKA_ID:
        parts.append(f'''<!-- Yandex.Metrika counter -->
<script type="text/javascript">
(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
m[i].l=1*new Date();
for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }} }}
k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})
(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
ym({YANDEX_METRIKA_ID}, "init", {{
    clickmap:true,
    trackLinks:true,
    accurateTrackBounce:true,
    webvisor:true
}});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/{YANDEX_METRIKA_ID}" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->''')
    if GOOGLE_ANALYTICS_ID:
        parts.append(f'''<!-- Google Analytics (GA4) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GOOGLE_ANALYTICS_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GOOGLE_ANALYTICS_ID}', {{ 'anonymize_ip': true }});
</script>
<!-- /Google Analytics -->''')
    return "\n".join(parts)


# ─── Рекламный слот РСЯ (Рекламная Сеть Яндекса) ──────────────────────────
def ad_slot_html(block_id=YANDEX_RSY_BLOCK_ID, slot_name="inline"):
    """Возвращает HTML-код рекламного блока РСЯ, если block_id задан.
    Если block_id пустой — возвращает пустой div с классом ad-slot
    (через CSS скрыт, не мешает верстке).
    """
    if not block_id:
        return f'<div class="ad-slot ad-slot--{slot_name}" data-slot="{slot_name}"></div>'
    return f'''<div class="ad-slot ad-slot--{slot_name}" data-slot="{slot_name}">
  <!-- Яндекс.РСЯ -->
  <div id="yandex_rtb_{slot_name}"></div>
  <script>
    window.yaContextCb = window.yaContextCb || [];
    window.yaContextCb.push(()=>{{
      window.yaContext.renderTo("{block_id}", {{
        blockId: "{slot_name}",
        renderTo: "yandex_rtb_{slot_name}"
      }});
    }});
  </script>
</div>'''


# ─── Кнопка «Поддержать» для вставки в статьи ─────────────────────────────
def donate_block_html():
    """Блок поддержки проекта — Telegram/ЮMoney (Boosty отключён по умолчанию).
    Вставляется в конец статьи."""
    buttons = []
    if DONATE_BOOSTY_URL:
        buttons.append(f'<a href="{DONATE_BOOSTY_URL}" target="_blank" rel="noopener nofollow" class="donate-btn donate-boosty">☕ Boosty</a>')
    if DONATE_TG_URL:
        buttons.append(f'<a href="{DONATE_TG_URL}" target="_blank" rel="noopener nofollow" class="donate-btn donate-tg">✈️ Telegram</a>')
    if DONATE_YOOMONEY:
        buttons.append(f'<a href="{DONATE_YOOMONEY}" target="_blank" rel="noopener nofollow" class="donate-btn donate-yoo">💳 ЮMoney</a>')
    if not buttons:
        return ''
    return f'''
    <aside class="donate-block" aria-label="Поддержать проект">
      <div class="donate-block__title">Поддержи проект</div>
      <p class="donate-block__text">Сайт живёт на энтузиазме. Если статья оказалась полезной — поблагодари автора. Любая сумма идёт на хостинг, домен и новые статьи.</p>
      <div class="donate-block__buttons">
        {''.join(buttons)}
      </div>
      <p class="donate-block__hint">Также можно подписаться на <a href="{TG_CHANNEL_URL}" target="_blank" rel="noopener">Telegram-канал</a> — там анонсы новых статей.</p>
    </aside>
    '''


# ─── FAQ JSON-LD: если в статье есть H3 в формате «Вопрос?» → генерируем ───
FAQ_Q_RE = re.compile(r'<h3[^>]*>([^<\?]+(?:\?|:))</h3>', re.I)


def extract_faq_jsonld(content):
    """Извлекает вопросы (h3, оканчивающиеся на ? или :) → FAQPage schema.
    Возвращает dict или None, если вопросов меньше 3 (Яндекс требует 3+)."""
    questions = []
    for m in FAQ_Q_RE.finditer(content):
        q = strip_tags(m.group(1)).strip()
        if not q:
            continue
        # Найти ближайший <p> после вопроса как ответ
        after = content[m.end():]
        p_m = re.search(r'<p[^>]*>(.*?)</p>', after, re.S)
        if not p_m:
            continue
        answer = strip_tags(p_m.group(1)).strip()
        if len(answer) < 20:
            continue
        questions.append({"q": q, "a": answer})
    if len(questions) < 3:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["q"],
             "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in questions[:10]  # максимум 10 вопросов
        ]
    }

# ----------------------------- ВСПОМОГАТЕЛЬНОЕ -------------------------------
TR = dict(zip(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n",
     "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y",
     "", "e", "yu", "ya"]))


def esc(s):
    return html.escape(str(s), quote=True)


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def clean_slug(s):
    """Адрес только из латиницы, цифр и дефисов (кириллицу транслитерирует)."""
    s = "".join(TR.get(c, c) for c in s.lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def abs_url(path):
    if re.match(r"https?://", path):
        return path
    return SITE + "/" + path.lstrip("/")


def src(path):
    """Путь к картинке от корня сайта."""
    return path if re.match(r"(https?:)?//|/", path) else "/" + path


def ld_json(data):
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


# ----------------------------- ЧТЕНИЕ СТАТЕЙ ---------------------------------
def load_articles():
    code = (ROOT / "data" / "articles.js").read_text(encoding="utf-8")
    code += "\n;process.stdout.write(JSON.stringify(ARTICLES));\n"
    res = subprocess.run(["node", "-"], input=code, capture_output=True,
                         text=True, encoding="utf-8")
    if res.returncode != 0:
        sys.exit("Не удалось прочитать data/articles.js:\n" + res.stderr)
    return json.loads(res.stdout)


AFF_RE = re.compile(r'<div class="affiliate">.*?</a>\s*</div>', re.S)


def strip_dead_affiliates(content):
    removed = 0

    def rep(m):
        nonlocal removed
        block = m.group(0)
        href = re.search(r'href="([^"]*)"', block)
        if not href or "ССЫЛКА" in href.group(1) or href.group(1) in ("", "#"):
            removed += 1
            return ""
        return block

    return AFF_RE.sub(rep, content), removed


def wrap_tables(content):
    content = re.sub(r'<div class="table-scroll">\s*(<table\b.*?</table>)\s*</div>',
                     r"\1", content, flags=re.S)
    return re.sub(r"(<table\b.*?</table>)",
                  r'<div class="table-scroll">\1</div>', content, flags=re.S)


def add_ids(content):
    heads = []

    def rep(m):
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        idm = re.search(r'\bid="([^"]+)"', attrs)
        hid = idm.group(1) if idm else f"section-{len(heads)}"
        if not idm:
            attrs += f' id="{hid}"'
        heads.append((level, hid, strip_tags(inner)))
        return f"<h{level}{attrs}>{inner}</h{level}>"

    content = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", rep, content, flags=re.S)
    return content, heads


OLD_LINK_RE = re.compile(r'href="(?:/)?article\.html\?a=([^"#&]+)(#[^"]*)?"')


def fix_internal_links(content, valid):
    """Ссылки article.html?a=... внутри статей -> прямые адреса articles/....html"""
    missing = []

    def rep(m):
        slug = clean_slug(unquote(m.group(1)))
        if slug in valid:
            return f'href="/articles/{slug}.html{m.group(2) or ""}"'
        missing.append(m.group(1))
        return m.group(0)

    return OLD_LINK_RE.sub(rep, content), missing


def prepare(raw):
    seen, out, removed = set(), [], 0
    for a in raw:
        a = dict(a)
        a["clean"] = clean_slug(a["slug"])
        if not a["clean"] or a["clean"] in seen:
            sys.exit(f"Повторяющийся или пустой адрес статьи: {a['slug']}")
        seen.add(a["clean"])
        a["url"] = f"articles/{a['clean']}.html"
        content, n = strip_dead_affiliates(a["content"])
        removed += n
        content, missing = fix_internal_links(content, {clean_slug(x["slug"]) for x in raw})
        for m in missing:
            print(f"  ! В статье «{a['slug']}» ссылка на несуществующую статью: {m}")
        content = wrap_tables(content)
        a["content"], a["heads"] = add_ids(content)
        out.append(a)
    out.sort(key=lambda x: x["date"], reverse=True)
    return out, removed


# ----------------------------- КАРТИНКИ ДЛЯ СОЦСЕТЕЙ -------------------------
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def find_font():
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    return None


def draw_card(out_path, title, tags_line):
    """Рисует PNG 1200×630. Возвращает True, если получилось."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        font_path = find_font()
        if not font_path:
            return False
        W, H = 1200, 630
        img = Image.new("RGB", (W, H), (14, 17, 23))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 18, H], fill=(79, 140, 255))
        f_brand = ImageFont.truetype(font_path, 40)
        f_title = ImageFont.truetype(font_path, 62)
        f_small = ImageFont.truetype(font_path, 30)
        d.text((80, 64), SITE_NAME, font=f_brand, fill=(79, 140, 255))

        lines, line = [], ""
        for word in title.split():
            test = (line + " " + word).strip()
            if d.textlength(test, font=f_title) <= 1040:
                line = test
            else:
                lines.append(line)
                line = word
        lines.append(line)
        if len(lines) > 4:
            lines = lines[:4]
            lines[-1] = lines[-1].rstrip(" .,") + "…"
        y = 170
        for ln in lines:
            d.text((80, y), ln, font=f_title, fill=(240, 242, 247))
            y += 84
        if tags_line:
            d.text((80, H - 90), tags_line, font=f_small, fill=(140, 150, 170))
        d.text((W - 80 - d.textlength(SITE.replace("https://", ""), font=f_small),
                H - 90), SITE.replace("https://", ""), font=f_small,
               fill=(140, 150, 170))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, optimize=True)
        return True
    except Exception as e:  # картинки — приятный бонус, сборка не должна падать
        print("  (OG-картинка не создана:", e, ")")
        return False


def make_og_images(arts):
    made = 0
    default = ROOT / "img" / "og-default.png"
    if (FORCE_OG or not default.exists()) and draw_card(
            default, "Понятно про ИИ, код и технологии", "ИИ · Код · Инструменты"):
        made += 1
    for a in arts:
        p = ROOT / "img" / "og" / f"{a['clean']}.png"
        if FORCE_OG or not p.exists():
            if draw_card(p, a["title"], "  ·  ".join(a["tags"][:3])):
                made += 1
    return made


def og_image(a):
    p = ROOT / "img" / "og" / f"{a['clean']}.png"
    if p.exists():
        return abs_url(f"img/og/{a['clean']}.png")
    if (ROOT / "img" / "og-default.png").exists():
        return abs_url("img/og-default.png")
    return abs_url(a["cover"])


def default_og():
    if (ROOT / "img" / "og-default.png").exists():
        return abs_url("img/og-default.png")
    return abs_url("img/ai-cover.svg")


# ----------------------------- HTML-КУСКИ ------------------------------------
def card(a):
    href = "/" + a["url"]
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in a["tags"])
    return (
        '<article class="card">\n'
        f'  <a class="card__cover" href="{href}"><img src="{esc(src(a["cover"]))}" '
        f'alt="{esc(a["title"])}" loading="lazy"></a>\n'
        '  <div class="card__body">\n'
        f'    <div class="card__tags">{tags}</div>\n'
        f'    <a href="{href}"><h2 class="card__title">{esc(a["title"])}</h2></a>\n'
        f'    <p class="card__excerpt">{esc(a["excerpt"])}</p>\n'
        '    <div class="card__meta">\n'
        f'      <span>{fmt_date(a["date"])}</span><span class="dot">•</span>'
        f'<span>{a["readTime"]} мин</span>\n'
        f'      <button class="card__bm" data-slug="{esc(a["slug"])}" title="В закладки" '
        'aria-label="В закладки">★</button>\n'
        '    </div>\n  </div>\n</article>'
    )


MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
          "августа", "сентября", "октября", "ноября", "декабря"]


def fmt_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def related(a, arts):
    """Похожие статьи — сначала по общим тегам, потом добираем свежими.
    Возвращает 6 статей (раньше было 3)."""
    scored = [(len(set(x["tags"]) & set(a["tags"])), x)
              for x in arts if x["slug"] != a["slug"]]
    scored = [s for s in scored if s[0] > 0]
    # Сортировка: больший overlap сверху, при равенстве — более свежая дата
    scored.sort(key=lambda s: (-s[0], s[1]["date"]), reverse=False)
    # reverse=False значит по возрастанию, но -overlap даёт нужный порядок
    # На самом деле нужно явно: больший overlap и более поздняя дата наверху
    scored.sort(key=lambda s: (-s[0], s[1]["date"]))
    # arts уже отсортированы по дате — берём первые 6
    res = [x for _, x in scored[:6]]
    if len(res) < 6:
        used = {x["slug"] for x in res} | {a["slug"]}
        for x in arts:
            if len(res) < 6 and x["slug"] not in used:
                res.append(x)
                used.add(x["slug"])
    return res


def build_article_page(a, arts):
    canon = f"{SITE}/{a['url']}"
    img = og_image(a)
    first_tag = a["tags"][0]
    title_full = f"{a['title']} — {SITE_NAME}"

    ld = [
        {"@context": "https://schema.org", "@type": "Article",
         "headline": a["title"], "description": a["excerpt"], "image": [img],
         "datePublished": a["date"], "dateModified": a["date"], "inLanguage": "ru",
         "author": {"@type": "Organization", "name": AUTHOR_NAME, "url": SITE + "/"},
         "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE + "/",
                       "logo": {"@type": "ImageObject", "url": SITE + "/favicon.svg"}},
         "mainEntityOfPage": {"@type": "WebPage", "@id": canon},
         "articleSection": first_tag,
         "keywords": ", ".join(a["tags"])},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": first_tag,
              "item": f"{SITE}/?tag={first_tag}"},
             {"@type": "ListItem", "position": 3, "name": a["title"], "item": canon}]},
    ]
    # FAQ JSON-LD — если в статье есть 3+ вопроса под H3
    faq = extract_faq_jsonld(a["content"])
    if faq:
        ld.append(faq)

    # Склеиваем все LD в один тег
    ld_inline = "\n".join(
        f'<script type="application/ld+json">{ld_json(item)}</script>'
        for item in ld
    )

    donate_html = donate_block_html()
    ad_inline = ad_slot_html(slot_name="ad-inline")
    ad_bottom = ad_slot_html(slot_name="ad-bottom")
    analytics = analytics_snippet()

    toc = ""
    if len(a["heads"]) >= 2:
        links = "".join(
            f'<a href="#{esc(hid)}" class="lvl-{3 if lvl == "3" else 2}">{esc(text)}</a>'
            for lvl, hid, text in a["heads"])
        toc = f'<div class="toc__title">Содержание</div>{links}'

    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in a["tags"])
    rel = "\n".join(card(x) for x in related(a, arts))

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title_full)}</title>
  <meta name="description" content="{esc(a['excerpt'])}">
  <link rel="canonical" href="{canon}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:title" content="{esc(a['title'])}">
  <meta property="og:description" content="{esc(a['excerpt'])}">
  <meta property="og:image" content="{img}">
  <meta property="og:url" content="{canon}">
  <meta property="article:published_time" content="{a['date']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(a['title'])}">
  <meta name="twitter:description" content="{esc(a['excerpt'])}">
  <meta name="twitter:image" content="{img}">
  {ld_inline}
  {THEME_SCRIPT}
  {ICONS}
  <link rel="stylesheet" href="/style.css">
</head>
<body>

  <div id="progress"></div>

  {HEADER}

  <main>
    <div id="article-view" class="wrap" data-slug="{esc(a['slug'])}">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="/">Главная</a>
        <span class="sep">/</span>
        <a href="/?tag={esc(first_tag)}">{esc(first_tag)}</a>
        <span class="sep">/</span>
        <span>{esc(a['title'])}</span>
      </nav>

      <div class="article-head">
        <div class="card__tags">{tags}</div>
        <h1>{esc(a['title'])}</h1>
        <div class="article-head__meta">
          <time datetime="{a['date']}">{fmt_date(a['date'])}</time>
          <span class="dot">•</span>
          <span>{a['readTime']} мин чтения</span>
          <button class="btn-bm" id="bmBtn">★ В закладки</button>
          <div class="share">
            <span class="share__label">Поделиться:</span>
            <button class="share__btn" id="shareTg" title="Telegram">Telegram</button>
            <button class="share__btn" id="shareVk" title="ВКонтакте">VK</button>
            <button class="share__btn" id="shareCopy" title="Скопировать ссылку">Копировать</button>
          </div>
        </div>
      </div>

      <figure class="article-cover">
        <img src="{esc(src(a['cover']))}" alt="{esc(a['title'])}">
      </figure>

      {ad_inline}

      <div class="article-layout">
        <article class="article-body" id="article-body">{a['content']}</article>
        <aside class="toc" id="toc">{toc}</aside>
      </div>

      {donate_html}

      {ad_bottom}

      <section class="wrap" style="padding-bottom:70px">
        <h2 style="font-family:Georgia,serif;font-size:22px;margin:24px 0 20px">Читай дальше</h2>
        <div class="grid" id="related">
{rel}
        </div>
      </section>
    </div>
  </main>

  {FOOTER}

  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css">
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-core.min.js" data-manual></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
  <script src="/app.js"></script>
  {analytics}
</body>
</html>
"""


# ----------------------------- ЗАПИСЬ ФАЙЛОВ --------------------------------
def write_articles(arts):
    out_dir = ROOT / "articles"
    out_dir.mkdir(exist_ok=True)
    keep = set()
    for a in arts:
        p = out_dir / f"{a['clean']}.html"
        p.write_text(build_article_page(a, arts), encoding="utf-8")
        keep.add(p.name)
    for old in out_dir.glob("*.html"):
        if old.name not in keep:
            old.unlink()


def write_index_js(arts):
    items = [{"slug": a["slug"], "title": a["title"], "excerpt": a["excerpt"],
              "cover": a["cover"], "tags": a["tags"], "date": a["date"],
              "readTime": a["readTime"], "url": a["url"]} for a in arts]
    text = ("/* Файл создаётся автоматически скриптом build.py — не редактируй. */\n"
            "const ARTICLES = " + json.dumps(items, ensure_ascii=False, indent=1) + ";\n")
    (ROOT / "data" / "index.js").write_text(text, encoding="utf-8")


def write_sitemap(arts):
    newest = max(a["date"] for a in arts)
    urls = [(SITE + "/", newest, "weekly", "1.0")]
    # Служебные страницы
    static_pages = [
        ("about.html", "monthly", "0.6"),
        ("contacts.html", "monthly", "0.5"),
        ("privacy.html", "monthly", "0.3"),
        ("terms.html", "monthly", "0.3"),
        ("support.html", "monthly", "0.6"),
        ("sitemap.html", "weekly", "0.7"),
        ("archive.html", "weekly", "0.7"),
        ("top.html", "weekly", "0.8"),
    ]
    for page, freq, prio in static_pages:
        urls.append((f"{SITE}/{page}", None, freq, prio))
    # Все статьи
    for a in arts:
        urls.append((f"{SITE}/{a['url']}", a["date"], "weekly", "0.8"))
    # Теговые страницы
    by_tag = {}
    for a in arts:
        for t in a["tags"]:
            by_tag.setdefault(t, []).append(a)
    for tag in by_tag:
        urls.append((f"{SITE}/tags/{slugify_tag(tag)}.html", newest, "weekly", "0.6"))

    rows = []
    for loc, last, freq, prio in urls:
        row = f"  <url>\n    <loc>{esc(loc)}</loc>\n"
        if last:
            row += f"    <lastmod>{last}</lastmod>\n"
        if freq:
            row += f"    <changefreq>{freq}</changefreq>\n"
        if prio:
            row += f"    <priority>{prio}</priority>\n"
        rows.append(row + "  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")


def update_index_html(arts):
    p = ROOT / "index.html"
    text = p.read_text(encoding="utf-8")
    if "<!--GRID_START-->" not in text:
        print("  ! В index.html нет маркеров <!--GRID_START--> / <!--GRID_END-->")
        return
    cards = "\n".join(card(a) for a in arts)
    text = re.sub(r"(<!--GRID_START-->).*?(<!--GRID_END-->)",
                  lambda m: m.group(1) + "\n" + cards + "\n" + m.group(2),
                  text, flags=re.S)
    p.write_text(text, encoding="utf-8")


def normalize_pages():
    """Мелкие правки служебных страниц: canonical, Open Graph, noindex, email."""
    skip = {"index.html", "article.html"}
    for p in sorted(ROOT.glob("*.html")):
        if p.name in skip:
            continue
        t = p.read_text(encoding="utf-8")
        orig = t
        t = t.replace('src="data/articles.js"', 'src="data/index.js"')
        t = t.replace("ТВОЙ_EMAIL@gmail.com", CONTACT_EMAIL)
        head_end = t.find("</head>")
        head = t[:head_end]
        if p.name == "bookmarks.html" and 'name="robots"' not in head:
            t = t.replace("</head>", '  <meta name="robots" content="noindex, follow">\n</head>', 1)
        if "noindex" not in t[:t.find("</head>")] and 'rel="canonical"' not in head:
            title = re.search(r"<title>(.*?)</title>", head, re.S)
            desc = re.search(r'name="description" content="([^"]*)"', head)
            canon = f"{SITE}/{p.name}"
            block = (
                f'  <link rel="canonical" href="{canon}">\n'
                '  <meta property="og:type" content="website">\n'
                f'  <meta property="og:site_name" content="{esc(SITE_NAME)}">\n'
                '  <meta property="og:locale" content="ru_RU">\n'
                f'  <meta property="og:title" content="{title.group(1).strip() if title else ""}">\n'
                f'  <meta property="og:description" content="{desc.group(1) if desc else ""}">\n'
                f'  <meta property="og:url" content="{canon}">\n'
                f'  <meta property="og:image" content="{default_og()}">\n'
                '  <meta name="twitter:card" content="summary_large_image">\n')
            t = t.replace("</head>", block + "</head>", 1)
        if t != orig:
            p.write_text(t, encoding="utf-8")


# ----------------------------- RSS / MANIFEST / SITEMAP.HTML ----------------
def write_rss(arts):
    """RSS 2.0 — Яндекс.Вебмастер индексирует RSS быстрее, чем HTML."""
    last_build = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    items = []
    for a in arts[:25]:  # последние 25 статей
        url = f"{SITE}/{a['url']}"
        cover_url = abs_url(a["cover"])
        items.append(
            "    <item>\n"
            f"      <title>{esc(a['title'])}</title>\n"
            f"      <link>{url}</link>\n"
            f"      <guid isPermaLink=\"true\">{url}</guid>\n"
            f"      <description>{esc(a['excerpt'])}</description>\n"
            f"      <category>{esc(a['tags'][0] if a['tags'] else '')}</category>\n"
            f"      <pubDate>{datetime.datetime.strptime(a['date'], '%Y-%m-%d').strftime('%a, %d %b %Y %H:%M:%S +0300')}</pubDate>\n"
            f"      <enclosure url=\"{cover_url}\" type=\"image/svg+xml\" length=\"0\"/>\n"
            "    </item>"
        )
    xml = (
        '<?xml version="1.0" encoding=\"UTF-8\"?>\n'
        '<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n'
        '  <channel>\n'
        f'    <title>{esc(SITE_NAME)} — понятные статьи про ИИ, программирование и IT</title>\n'
        f'    <link>{SITE}/</link>\n'
        '    <description>Статьи про технологии простыми словами: ИИ, программирование, веб, базы данных, DevOps.</description>\n'
        '    <language>ru-ru</language>\n'
        f'    <lastBuildDate>{last_build}</lastBuildDate>\n'
        f'    <atom:link href=\"{SITE}/rss.xml\" rel=\"self\" type=\"application/rss+xml\"/>\n'
        '    <image>\n'
        f'      <url>{SITE}/favicon.svg</url>\n'
        f'      <title>{esc(SITE_NAME)}</title>\n'
        f'      <link>{SITE}/</link>\n'
        '    </image>\n'
        + "\n".join(items) + "\n"
        '  </channel>\n'
        '</rss>\n'
    )
    (ROOT / "rss.xml").write_text(xml, encoding="utf-8")


def write_manifest():
    """PWA-манифест для установки сайта как приложения."""
    manifest = {
        "name": f"{SITE_NAME} — статьи про программирование",
        "short_name": SITE_NAME,
        "description": "Понятные статьи про ИИ, программирование и IT простыми словами",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait-primary",
        "background_color": "#0d1117",
        "theme_color": "#0d1117",
        "lang": "ru",
        "dir": "ltr",
        "categories": ["education", "news", "books"],
        "icons": [
            {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"},
            {"src": "/favicon.ico", "sizes": "16x16 32x32 48x48", "type": "image/x-icon", "purpose": "any"},
        ],
        "shortcuts": [
            {"name": "Все статьи", "url": "/", "description": "Открыть главную страницу со всеми статьями"},
            {"name": "Карта сайта", "url": "/sitemap.html", "description": "Список всех статей по тегам"},
        ],
    }
    (ROOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_robots():
    """robots.txt со ссылками на sitemap и правилами для Яндекса."""
    host = SITE.replace("https://", "").replace("http://", "")
    txt = (
        "# robots.txt — IT·База\n"
        f"# {SITE}/\n\n"
        "User-agent: *\n"
        "Allow: /\n"
        "Allow: /articles/\n"
        "Allow: /img/\n"
        "Allow: /support.html\n"
        "Disallow: /data/\n"
        "Disallow: /app.js\n\n"
        "# Особые правила для Яндекса\n"
        "User-agent: Yandex\n"
        "Allow: /\n"
        "Allow: /articles/\n"
        "Allow: /img/\n"
        "Allow: /support.html\n"
        "Disallow: /data/\n"
        "Clean-param: tag&q&search /*\n"
        "Crawl-delay: 0.5\n\n"
        "# Особые правила для Google\n"
        "User-agent: Googlebot\n"
        "Allow: /\n"
        "Allow: /articles/\n"
        "Allow: /img/\n"
        "Allow: /support.html\n"
        "Disallow: /data/\n\n"
        f"Sitemap: {SITE}/sitemap.xml\n"
        f"Sitemap: {SITE}/sitemap-images.xml\n"
        f"Host: {host}\n"
    )
    (ROOT / "robots.txt").write_text(txt, encoding="utf-8")


def write_sitemap_html(arts):
    """Человекочитаемая карта сайта со всеми статьями по тегам."""
    by_tag = {}
    for a in arts:
        for tag in a["tags"]:
            by_tag.setdefault(tag, []).append(a)

    all_tags = sorted(by_tag.keys())

    tag_chips = " ".join(
        f'<a href="#tag-{esc(t)}" class="chip">{esc(t)}</a>' for t in all_tags
    )

    blocks = []
    for tag in all_tags:
        items = by_tag[tag]
        items_html = "\n".join(
            f'        <li>\n'
            f'          <a href="/{a["url"]}"><strong>{esc(a["title"])}</strong></a>\n'
            f'          <span class="sitemap-date">{fmt_date(a["date"])}</span>\n'
            f'          <p>{esc(a["excerpt"])}</p>\n'
            f'        </li>'
            for a in items
        )
        blocks.append(
            f'    <section class="sitemap-tag">\n'
            f'      <h2 id="tag-{esc(tag)}">{esc(tag)} <span class="sitemap-count">({len(items)})</span></h2>\n'
            f'      <ul class="sitemap-list">\n{items_html}\n      </ul>\n'
            f'    </section>'
        )
    blocks_str = "\n\n".join(blocks)

    today = datetime.date.today().isoformat()

    html_out = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Карта сайта — {esc(SITE_NAME)}</title>
  <meta name="description" content="Полная карта сайта {esc(SITE_NAME)}: все статьи по тегам, служебные страницы, RSS-фид и sitemap.xml для поисковых систем.">
  <link rel="canonical" href="{SITE}/sitemap.html">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta property="og:title" content="Карта сайта — {esc(SITE_NAME)}">
  <meta property="og:description" content="Все статьи {esc(SITE_NAME)} по тегам, RSS-фид и sitemap.xml.">
  <meta property="og:url" content="{SITE}/sitemap.html">
  <meta property="og:image" content="{default_og()}">
  {ICONS}
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0d1117">
  <link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)} — новые статьи" href="{SITE}/rss.xml">
  {THEME_SCRIPT}
  <link rel="stylesheet" href="/style.css">
  <style>
    .sitemap-wrap{{max-width:1100px;margin:0 auto;padding:30px 20px 80px;}}
    .sitemap-intro{{margin:20px 0 30px;color:var(--muted);font-size:15px;line-height:1.6;}}
    .sitemap-tags{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:40px;}}
    .sitemap-tag{{margin-bottom:50px;}}
    .sitemap-tag h2{{font-family:Georgia,serif;font-size:24px;color:var(--accent);margin:0 0 18px;border-bottom:1px solid var(--border);padding-bottom:10px;}}
    .sitemap-count{{color:var(--muted);font-size:14px;font-weight:normal;}}
    .sitemap-list{{list-style:none;padding:0;margin:0;display:grid;gap:18px;}}
    .sitemap-list li{{padding:14px 18px;border:1px solid var(--border);border-radius:8px;background:var(--card);transition:border-color .15s;}}
    .sitemap-list li:hover{{border-color:var(--accent);}}
    .sitemap-list a{{text-decoration:none;}}
    .sitemap-list a strong{{font-size:17px;display:block;margin-bottom:6px;}}
    .sitemap-date{{color:var(--muted);font-size:13px;}}
    .sitemap-list p{{margin:8px 0 0;color:var(--muted);font-size:14px;line-height:1.5;}}
    .sitemap-static{{margin-top:60px;padding-top:30px;border-top:2px solid var(--border);}}
    .sitemap-static h2{{font-family:Georgia,serif;font-size:22px;margin:0 0 16px;}}
    .sitemap-static ul{{list-style:none;padding:0;margin:0;display:grid;gap:8px;}}
    .sitemap-static li a{{color:var(--accent);text-decoration:none;font-size:15px;}}
    .sitemap-static li a:hover{{text-decoration:underline;}}
    .chip{{display:inline-block;padding:6px 14px;border:1px solid var(--border);border-radius:16px;background:var(--card);color:var(--text);text-decoration:none;font-size:14px;}}
    .chip:hover{{border-color:var(--accent);color:var(--accent);}}
  </style>
</head>
<body>
  <div id="progress"></div>
  {HEADER}
  <main>
    <section class="hero wrap">
      <h1>Карта сайта</h1>
      <p>Все статьи {esc(SITE_NAME)}, сгруппированные по тегам. Обновлено: {today}.</p>
    </section>
    <div class="sitemap-wrap">
      <p class="sitemap-intro">
        На этой странице собраны все {len(arts)} статей сайта, разбитые по тегам.
        Это удобно и для людей, и для поисковых систем — краулеры Яндекса и Google
        обходят эту страницу по ссылкам и быстрее находят все материалы сайта.
        Для автоматической обработки есть <a href="/sitemap.xml" style="color:var(--accent)">sitemap.xml</a>
        и <a href="/rss.xml" style="color:var(--accent)">RSS-фид</a>.
      </p>
      <div class="sitemap-tags">
        {tag_chips}
      </div>
{blocks_str}
      <section class="sitemap-static">
        <h2>Служебные страницы</h2>
        <ul>
          <li><a href="/">Главная</a></li>
          <li><a href="/about.html">О сайте</a></li>
          <li><a href="/contacts.html">Контакты</a></li>
          <li><a href="/privacy.html">Политика конфиденциальности</a></li>
          <li><a href="/terms.html">Условия использования</a></li>
          <li><a href="/sitemap.xml">Карта сайта (XML)</a></li>
          <li><a href="/rss.xml">RSS-фид</a></li>
        </ul>
      </section>
    </div>
  </main>
  {FOOTER}
  <script src="/app.js"></script>
</body>
</html>
'''
    (ROOT / "sitemap.html").write_text(html_out, encoding="utf-8")


def write_sitemap_images(arts):
    """sitemap-images.xml — карта изображений для индексации в Яндекс.Картинки."""
    urls = []
    seen = set()
    for a in arts:
        # Обложка статьи (OG-картинка если есть, иначе SVG)
        img_url = og_image(a)
        page_url = f"{SITE}/{a['url']}"
        if img_url not in seen:
            urls.append((img_url, page_url, a["title"]))
            seen.add(img_url)
        # OG-default
        default = default_og()
        if default not in seen:
            urls.append((default, SITE + "/", SITE_NAME))
            seen.add(default)

    rows = []
    for img_url, page_url, caption in urls:
        rows.append(
            "  <url>\n"
            f"    <loc>{esc(img_url)}</loc>\n"
            f"    <image:image>\n"
            f"      <image:loc>{esc(img_url)}</image:loc>\n"
            f"      <image:caption>{esc(caption)}</image:caption>\n"
            f"      <image:title>{esc(caption)}</image:title>\n"
            f"      <image:license>{SITE}/terms.html</image:license>\n"
            "    </image:image>\n"
            "  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + "\n".join(rows) + "\n"
        "</urlset>\n"
    )
    (ROOT / "sitemap-images.xml").write_text(xml, encoding="utf-8")


def write_support_page(arts):
    """Страница /support.html с кнопками Telegram/ЮMoney."""
    donate_html = donate_block_html()
    n_articles = len(arts)
    html_out = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Поддержать проект — {esc(SITE_NAME)}</title>
  <meta name="description" content="Поддержка проекта IT·База: Telegram, ЮMoney. Любая сумма идёт на хостинг, домен и создание новых статей.">
  <link rel="canonical" href="{SITE}/support.html">
  <meta name="robots" content="index, follow">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta property="og:title" content="Поддержать проект — {esc(SITE_NAME)}">
  <meta property="og:description" content="Поддержка проекта IT·База: Telegram, ЮMoney.">
  <meta property="og:url" content="{SITE}/support.html">
  <meta property="og:image" content="{default_og()}">
  {ICONS}
  <link rel="manifest" href="/manifest.json">
  <link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)} — новые статьи" href="{SITE}/rss.xml">
  {THEME_SCRIPT}
  <link rel="stylesheet" href="/style.css">
  <style>
    .support-wrap{{max-width:760px;margin:0 auto;padding:40px 20px 80px;}}
    .support-hero{{text-align:center;margin:30px 0 50px;}}
    .support-hero h1{{font-family:Georgia,serif;font-size:42px;margin:0 0 14px;}}
    .support-hero p{{color:var(--muted);font-size:17px;line-height:1.6;margin:0 auto;max-width:560px;}}
    .donate-block{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:36px;margin:30px 0;}}
    .donate-block__title{{font-family:Georgia,serif;font-size:26px;margin:0 0 16px;color:var(--accent);}}
    .donate-block__text{{color:var(--muted);font-size:16px;line-height:1.6;margin:0 0 24px;}}
    .donate-block__buttons{{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:18px;}}
    .donate-btn{{display:inline-flex;align-items:center;gap:8px;padding:14px 24px;border-radius:10px;font-weight:600;font-size:15px;text-decoration:none;transition:transform .15s,box-shadow .15s;}}
    .donate-btn:hover{{transform:translateY(-2px);box-shadow:0 6px 18px rgba(0,0,0,.25);}}
    .donate-boosty{{background:#f8f000;color:#1a1a1a;}}
    .donate-tg{{background:#0088cc;color:#fff;}}
    .donate-yoo{{background:#8b00cc;color:#fff;}}
    .donate-block__hint{{color:var(--muted);font-size:14px;margin:0;}}
    .donate-block__hint a{{color:var(--accent);}}
    .support-stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:20px;margin-top:40px;}}
    .support-stat{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center;}}
    .support-stat__num{{font-family:Georgia,serif;font-size:32px;color:var(--accent);margin-bottom:4px;}}
    .support-stat__label{{font-size:13px;color:var(--muted);}}
    .support-faq{{margin-top:50px;}}
    .support-faq h2{{font-family:Georgia,serif;font-size:26px;margin:0 0 20px;}}
    .support-faq details{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px 22px;margin-bottom:10px;}}
    .support-faq summary{{cursor:pointer;font-weight:600;font-size:16px;color:var(--text);}}
    .support-faq details[open] summary{{color:var(--accent);}}
    .support-faq p{{color:var(--muted);font-size:15px;line-height:1.6;margin:12px 0 0;}}
  </style>
</head>
<body>
  <div id="progress"></div>
  {HEADER}
  <main>
    <section class="support-wrap">
      <div class="support-hero">
        <h1>Поддержать проект</h1>
        <p>IT·База — бесплатный образовательный проект. Здесь нет рекламы, которая мешает
        чтению, и нет пейволов. Если статьи оказались полезными — поддержи автора любой
        суммой. Это поможет платить за хостинг, домен и тратить больше времени на
        написание новых материалов.</p>
      </div>

      {donate_html}

      <div class="support-stats">
        <div class="support-stat">
          <div class="support-stat__num">{n_articles}</div>
          <div class="support-stat__label">статей на сайте</div>
        </div>
        <div class="support-stat">
          <div class="support-stat__num">100%</div>
          <div class="support-stat__label">бесплатно</div>
        </div>
        <div class="support-stat">
          <div class="support-stat__num">0</div>
          <div class="support-stat__label">рекламы в статьях</div>
        </div>
        <div class="support-stat">
          <div class="support-stat__num">2026</div>
          <div class="support-stat__label">год запуска</div>
        </div>
      </div>

      <section class="support-faq">
        <h2>Частые вопросы</h2>
        <details>
          <summary>Зачем мне вас поддерживать?</summary>
          <p>Сайт живёт на хостинге GitHub Pages — он бесплатный, но есть ограничения.
          Домен стоит денег. А главное — время автора: написание одной статьи занимает
          10-20 часов с проверкой фактов и кода. Поддержка позволяет выделять на это
          больше времени.</p>
        </details>
        <details>
          <summary>Какие способы оплаты есть?</summary>
          <p>Telegram-оплата (карты РФ и мира, крипта), ЮMoney (для РФ).
          Все способы — внешние сервисы, данные карты нигде на сайте не сохраняются.
          Если подключу Boosty позже — добавлю сюда.</p>
        </details>
        <details>
          <summary>Можно ли подписаться на регулярную поддержку?</summary>
          <p>Пока регулярной подписки нет. Можно поддержать разово через Telegram-бота
          или ЮMoney. Когда подключу Boosty — там будут тарифы от 100 ₽/мес с
          доступом к закрытому Telegram-каналу и ранним доступом к новым статьям.</p>
        </details>
        <details>
          <summary>Что если я не могу финансово помочь?</summary>
          <p>Поделись ссылкой на статью с другом — это тоже поддержка. Можно подписаться
          на <a href="{TG_CHANNEL_URL}" target="_blank" rel="noopener">Telegram-канал</a>,
          поставить звёздочку в закладки и рассказать о проекте в своём окружении.</p>
        </details>
      </section>
    </section>
  </main>
  {FOOTER}
  <script src="/app.js"></script>
  {analytics_snippet()}
</body>
</html>
'''
    (ROOT / "support.html").write_text(html_out, encoding="utf-8")


# ----------------------------- ТЕГОВЫЕ СТРАНИЦЫ -------------------------------
def slugify_tag(tag):
    """Тег → латиница для URL. Например 'Базы данных' → 'bazy-dannyh'."""
    return clean_slug(tag)


def write_tag_pages(arts):
    """Создаёт /tags/{slug}.html для каждого тега — список статей с SEO."""
    by_tag = {}
    for a in arts:
        for t in a["tags"]:
            by_tag.setdefault(t, []).append(a)

    out_dir = ROOT / "tags"
    out_dir.mkdir(exist_ok=True)

    # Список всех тегов для вставки в sitemap-страницы
    all_tags = sorted(by_tag.keys(), key=lambda x: -len(by_tag[x]))

    for tag, items in by_tag.items():
        slug = slugify_tag(tag)
        items_sorted = sorted(items, key=lambda x: x["date"], reverse=True)
        canon = f"{SITE}/tags/{slug}.html"

        # SEO-описание динамически
        n = len(items_sorted)
        desc = f"Все статьи с тегом «{tag}» на IT·База — {n} материалов. Понятные статьи про технологии простыми словами."
        title = f"{tag} — {n} {'статей' if n != 1 else 'статья'} | IT·База"

        # JSON-LD: ItemList
        ld = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"Статьи по тегу {tag}",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1,
                 "name": a["title"],
                 "url": f"{SITE}/{a['url']}"}
                for i, a in enumerate(items_sorted[:20])
            ]
        }

        # Список статей
        cards = "\n".join(card(a) for a in items_sorted)
        # Переделываем card() чтобы убрать isOn bookmarks — но card() это использует в Article
        # Это норм — кнопка просто не выделена

        # Ссылки на другие теги
        other_tags = " ".join(
            f'<a href="/tags/{slugify_tag(t)}.html" class="chip">{esc(t)} <span class="sitemap-count">({len(by_tag[t])})</span></a>'
            for t in all_tags if t != tag
        )

        html_out = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="keywords" content="{esc(tag)}, статьи {esc(tag)}, {esc(tag)} простыми словами, IT, программирование">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{canon}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{canon}">
  <meta property="og:image" content="{default_og()}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{default_og()}">
  <script type="application/ld+json">{ld_json(ld)}</script>
  {ICONS}
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0d1117">
  <link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)} — {esc(tag)}" href="{SITE}/rss/{slug}.xml">
  {THEME_SCRIPT}
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <div id="progress"></div>
  {HEADER}
  <main>
    <section class="hero wrap">
      <h1>{esc(tag)}</h1>
      <p>{n} материалов на сайте. Объясняю {esc(tag.lower())} простыми словами — без воды, с примерами и кодом.</p>
    </section>
    <div class="wrap" style="padding-bottom:80px">
      <div class="grid" id="grid">
{cards}
      </div>
      <nav class="other-tags" aria-label="Другие теги" style="margin-top:60px;padding-top:30px;border-top:2px solid var(--border)">
        <h2 style="font-family:Georgia,serif;font-size:22px;margin:0 0 16px">Другие темы</h2>
        <div style="display:flex;flex-wrap:wrap;gap:8px">
          {other_tags}
        </div>
      </nav>
    </div>
  </main>
  {FOOTER}
  <script src="/data/index.js"></script>
  <script src="/app.js"></script>
  {analytics_snippet()}
</body>
</html>
'''
        (out_dir / f"{slug}.html").write_text(html_out, encoding="utf-8")


# ----------------------------- АРХИВ ПО МЕСЯЦАМ -------------------------------
def write_archive_page(arts):
    """/archive.html — все статьи сгруппированы по месяцам."""
    by_month = {}
    for a in arts:
        ym = a["date"][:7]  # YYYY-MM
        by_month.setdefault(ym, []).append(a)

    months_sorted = sorted(by_month.keys(), reverse=True)
    MONTH_NAMES = {
        "01": "Январь", "02": "Февраль", "03": "Март", "04": "Апрель",
        "05": "Май", "06": "Июнь", "07": "Июль", "08": "Август",
        "09": "Сентябрь", "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь"
    }

    sections = []
    for ym in months_sorted:
        items = sorted(by_month[ym], key=lambda x: x["date"], reverse=True)
        year, month = ym.split("-")
        title = f"{MONTH_NAMES[month]} {year}"
        items_html = "\n".join(
            f'        <li><time datetime="{a["date"]}">{fmt_date(a["date"])}</time> — '
            f'<a href="/{a["url"]}">{esc(a["title"])}</a></li>'
            for a in items
        )
        sections.append(
            f'    <section class="archive-month">\n'
            f'      <h2>{title} <span class="sitemap-count">({len(items)})</span></h2>\n'
            f'      <ul class="archive-list">\n{items_html}\n      </ul>\n'
            f'    </section>'
        )
    sections_str = "\n\n".join(sections)
    today = datetime.date.today().isoformat()

    html_out = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Архив статей — {esc(SITE_NAME)}</title>
  <meta name="description" content="Полный архив всех статей IT·База по месяцам. {len(arts)} статей про программирование, ИИ, DevOps, базы данных простыми словами.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{SITE}/archive.html">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Архив статей — {esc(SITE_NAME)}">
  <meta property="og:description" content="Полный архив всех статей IT·База по месяцам.">
  <meta property="og:url" content="{SITE}/archive.html">
  <meta property="og:image" content="{default_og()}">
  {ICONS}
  <link rel="manifest" href="/manifest.json">
  {THEME_SCRIPT}
  <link rel="stylesheet" href="/style.css">
  <style>
    .archive-wrap{{max-width:900px;margin:0 auto;padding:30px 20px 80px;}}
    .archive-month{{margin-bottom:50px;}}
    .archive-month h2{{font-family:Georgia,serif;font-size:24px;color:var(--accent);margin:0 0 18px;border-bottom:1px solid var(--border);padding-bottom:10px;}}
    .archive-list{{list-style:none;padding:0;margin:0;display:grid;gap:14px;}}
    .archive-list li{{padding:8px 0;border-bottom:1px dotted var(--border);font-size:16px;}}
    .archive-list time{{color:var(--muted);font-size:14px;margin-right:14px;white-space:nowrap;}}
    .archive-list a{{color:var(--text);text-decoration:none;}}
    .archive-list a:hover{{color:var(--accent);}}
    .sitemap-count{{color:var(--muted);font-size:14px;font-weight:normal;}}
  </style>
</head>
<body>
  <div id="progress"></div>
  {HEADER}
  <main>
    <section class="hero wrap">
      <h1>Архив статей</h1>
      <p>Все {len(arts)} статей сайта, отсортированы по месяцам. Обновлено: {today}.</p>
    </section>
    <div class="archive-wrap">
{sections_str}
    </div>
  </main>
  {FOOTER}
  <script src="/app.js"></script>
  {analytics_snippet()}
</body>
</html>
'''
    (ROOT / "archive.html").write_text(html_out, encoding="utf-8")


# ----------------------------- ТОП СТАТЕЙ ------------------------------------
def write_top_page(arts):
    """/top.html — топ-10 статей по длине + недавние."""
    # Топ-10 по длине контента (прокси для «самые большие статьи»)
    by_len = sorted(arts, key=lambda a: -len(a["content"]))
    top10 = by_len[:10]

    # Топ по тегам — 5 самых популярных тегов
    by_tag = {}
    for a in arts:
        for t in a["tags"]:
            by_tag.setdefault(t, []).append(a)
    top_tags = sorted(by_tag.items(), key=lambda x: -len(x[1]))[:5]

    cards = "\n".join(card(a) for a in top10)
    tags_html = " ".join(
        f'<a href="/tags/{slugify_tag(t)}.html" class="chip">{esc(t)} ({len(items)})</a>'
        for t, items in top_tags
    )

    today = datetime.date.today().isoformat()
    total_words = sum(len(a["content"].split()) for a in arts)

    html_out = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Лучшие статьи — {esc(SITE_NAME)}</title>
  <meta name="description" content="Топ-10 статей IT·База по объёму и качеству. Самые подробные материалы про программирование, ИИ, DevOps.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{SITE}/top.html">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Лучшие статьи — {esc(SITE_NAME)}">
  <meta property="og:description" content="Топ-10 самых подробных статей IT·База.">
  <meta property="og:url" content="{SITE}/top.html">
  <meta property="og:image" content="{default_og()}">
  {ICONS}
  <link rel="manifest" href="/manifest.json">
  {THEME_SCRIPT}
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <div id="progress"></div>
  {HEADER}
  <main>
    <section class="hero wrap">
      <h1>Лучшие статьи</h1>
      <p>Топ-10 материалов сайта по объёму и качеству. Обновлено: {today}.</p>
    </section>
    <div class="wrap" style="padding-bottom:60px">
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:18px;margin:30px 0 40px">
        <div class="support-stat"><div class="support-stat__num">{len(arts)}</div><div class="support-stat__label">статей всего</div></div>
        <div class="support-stat"><div class="support-stat__num">{total_words:,}</div><div class="support-stat__label">слов написано</div></div>
        <div class="support-stat"><div class="support-stat__num">{len(by_tag)}</div><div class="support-stat__label">тегов</div></div>
        <div class="support-stat"><div class="support-stat__num">{max(a['readTime'] for a in arts)}</div><div class="support-stat__label">макс. минут чтения</div></div>
      </div>
      <h2 style="font-family:Georgia,serif;font-size:26px;margin:30px 0 20px">Топ-10 по объёму</h2>
      <div class="grid" id="grid">
{cards}
      </div>
      <h2 style="font-family:Georgia,serif;font-size:26px;margin:50px 0 20px">Популярные теги</h2>
      <div style="display:flex;flex-wrap:wrap;gap:10px">
        {tags_html}
      </div>
      <p style="margin-top:50px;text-align:center">
        <a href="/archive.html" style="display:inline-block;padding:14px 28px;background:var(--accent);color:#fff;text-decoration:none;border-radius:10px;font-weight:600">Смотреть все статьи в архиве →</a>
      </p>
    </div>
  </main>
  {FOOTER}
  <script src="/data/index.js"></script>
  <script src="/app.js"></script>
  {analytics_snippet()}
</body>
</html>
'''
    (ROOT / "top.html").write_text(html_out, encoding="utf-8")


# ----------------------------- JSON FEED -------------------------------------
def write_json_feed(arts):
    """/feed.json — JSON Feed (современная альтернатива RSS)."""
    items = []
    for a in arts[:25]:
        items.append({
            "id": f"{SITE}/{a['url']}",
            "url": f"{SITE}/{a['url']}",
            "title": a["title"],
            "content_html": a["content"],
            "summary": a["excerpt"],
            "date_published": f"{a['date']}T00:00:00+03:00",
            "tags": a["tags"],
            "image": abs_url(a["cover"]),
        })
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": f"{SITE_NAME} — понятные статьи про ИИ, программирование и IT",
        "description": "Статьи про технологии простыми словами: ИИ, программирование, веб, базы данных, DevOps.",
        "home_page_url": SITE + "/",
        "feed_url": SITE + "/feed.json",
        "language": "ru-RU",
        "authors": [{"name": AUTHOR_NAME, "url": SITE + "/"}],
        "items": items,
    }
    (ROOT / "feed.json").write_text(
        json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ----------------------------- ТЕГОВЫЕ RSS-каналы ----------------------------
def write_tag_rss(arts):
    """/rss/{tag}.xml для каждого тега — отдельный RSS-канал."""
    by_tag = {}
    for a in arts:
        for t in a["tags"]:
            by_tag.setdefault(t, []).append(a)

    rss_dir = ROOT / "rss"
    rss_dir.mkdir(exist_ok=True)

    last_build = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    for tag, items in by_tag.items():
        slug = slugify_tag(tag)
        items = sorted(items, key=lambda x: x["date"], reverse=True)[:15]
        items_xml = []
        for a in items:
            url = f"{SITE}/{a['url']}"
            cover_url = abs_url(a["cover"])
            items_xml.append(
                "    <item>\n"
                f"      <title>{esc(a['title'])}</title>\n"
                f"      <link>{url}</link>\n"
                f"      <guid isPermaLink=\"true\">{url}</guid>\n"
                f"      <description>{esc(a['excerpt'])}</description>\n"
                f"      <category>{esc(tag)}</category>\n"
                f"      <pubDate>{datetime.datetime.strptime(a['date'], '%Y-%m-%d').strftime('%a, %d %b %Y %H:%M:%S +0300')}</pubDate>\n"
                f"      <enclosure url=\"{cover_url}\" type=\"image/svg+xml\" length=\"0\"/>\n"
                "    </item>"
            )
        xml = (
            '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n'
            '<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n'
            '  <channel>\n'
            f'    <title>{esc(SITE_NAME)} — {esc(tag)}</title>\n'
            f'    <link>{SITE}/tags/{slug}.html</link>\n'
            f'    <description>Статьи с тегом {esc(tag)} на {esc(SITE_NAME)}</description>\n'
            '    <language>ru-ru</language>\n'
            f'    <lastBuildDate>{last_build}</lastBuildDate>\n'
            f'    <atom:link href=\"{SITE}/rss/{slug}.xml\" rel=\"self\" type=\"application/rss+xml\"/>\n'
            + "\n".join(items_xml) + "\n"
            '  </channel>\n'
            '</rss>\n'
        )
        (rss_dir / f"{slug}.xml").write_text(xml, encoding="utf-8")


# ----------------------------- ЗАПУСК ----------------------------------------
def main():
    raw = load_articles()
    arts, removed = prepare(raw)
    print(f"Статей: {len(arts)}")
    if removed:
        print(f"Убрано партнёрских блоков с заглушкой вместо ссылки: {removed}")
    made = make_og_images(arts)
    print(f"OG-картинок создано: {made}")
    write_articles(arts)
    write_index_js(arts)
    write_sitemap(arts)
    update_index_html(arts)
    normalize_pages()
    # Новые SEO-файлы, добавленные ботом
    write_robots()
    write_rss(arts)
    write_manifest()
    write_sitemap_html(arts)
    write_sitemap_images(arts)
    write_support_page(arts)
    # Новые страницы для роста трафика
    write_tag_pages(arts)
    write_archive_page(arts)
    write_top_page(arts)
    write_json_feed(arts)
    write_tag_rss(arts)
    print("Все SEO-файлы созданы: теги, архив, топ, JSON Feed, теговые RSS.")
    print("Готово.")


if __name__ == "__main__":
    main()
