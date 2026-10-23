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
import re
import subprocess
import sys
from pathlib import Path

# ----------------------------- НАСТРОЙКИ ------------------------------------
SITE = "https://itbase-ru.github.io"   # адрес сайта БЕЗ слэша в конце
SITE_NAME = "IT·База"                  # название сайта
AUTHOR_NAME = "IT·База"                # автор в микроразметке (можно своё имя)
CONTACT_EMAIL = "kirillfomichev05@mail.ru"
FORCE_OG = False                       # True = перерисовать все OG-картинки
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
    <a href="/contacts.html">Контакты</a>
    <a href="/privacy.html">Политика</a>
    <a href="/terms.html">Условия</a>
    <a href="/bookmarks.html" style="margin-left:auto;color:var(--accent)">★ Закладки</a>
  </div>
</footer>"""

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
    scored = [(len(set(x["tags"]) & set(a["tags"])), x)
              for x in arts if x["slug"] != a["slug"]]
    scored = [s for s in scored if s[0] > 0]
    scored = sorted(scored, key=lambda s: -s[0])  # arts уже по дате, порядок сохраняется
    res = [x for _, x in scored[:3]]
    if len(res) < 3:
        used = {x["slug"] for x in res} | {a["slug"]}
        for x in arts:
            if len(res) < 3 and x["slug"] not in used:
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
         "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE + "/"},
         "mainEntityOfPage": {"@type": "WebPage", "@id": canon}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": first_tag,
              "item": f"{SITE}/?tag={first_tag}"},
             {"@type": "ListItem", "position": 3, "name": a["title"], "item": canon}]},
    ]

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
  <script type="application/ld+json">{ld_json(ld)}</script>
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

      <div class="article-layout">
        <article class="article-body" id="article-body">{a['content']}</article>
        <aside class="toc" id="toc">{toc}</aside>
      </div>

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
    urls = [(SITE + "/", newest)]
    for page in ("about", "contacts", "privacy", "terms"):
        urls.append((f"{SITE}/{page}.html", None))
    for a in arts:
        urls.append((f"{SITE}/{a['url']}", a["date"]))
    rows = []
    for loc, last in urls:
        row = f"  <url>\n    <loc>{esc(loc)}</loc>\n"
        if last:
            row += f"    <lastmod>{last}</lastmod>\n"
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
    print("Готово.")


if __name__ == "__main__":
    main()
