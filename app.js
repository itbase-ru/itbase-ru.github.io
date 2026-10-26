/* ==========================================================
   IT·База — логика сайта
   Страницы статей готовит build.py, здесь только интерактив.
   ========================================================== */
const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

/* Номер счётчика Яндекс.Метрики (только цифры). 0 = выключено. */
const METRIKA_ID = 0;

const MONTHS = ['января','февраля','марта','апреля','мая','июня',
                'июля','августа','сентября','октября','ноября','декабря'];

function formatDate(iso){
  const [y,m,d] = iso.split('-');
  return `${Number(d)} ${MONTHS[Number(m)-1]} ${y}`;
}
function esc(s){
  return String(s).replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}
function absPath(p){
  return /^(https?:)?\/\//.test(p) || p.startsWith('/') ? p : '/' + p;
}
const yEl = $('#year');
if (yEl) yEl.textContent = new Date().getFullYear();


/* ==========================================================
   ЯНДЕКС.МЕТРИКА
   ========================================================== */
if (METRIKA_ID) {
  (function(m,e,t,r,i,k,a){
    m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
    m[i].l=1*new Date();
    for (var j=0; j<document.scripts.length; j++){
      if (document.scripts[j].src === r) return;
    }
    k=e.createElement(t); a=e.getElementsByTagName(t)[0];
    k.async=1; k.src=r; a.parentNode.insertBefore(k,a);
  })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');
  ym(METRIKA_ID, 'init', {
    clickmap: true, trackLinks: true, accurateTrackBounce: true, webvisor: true
  });
}


/* ==========================================================
   ТЕМА
   ========================================================== */
const THEME_KEY = 'itbase_theme';
function applyTheme(t){
  if (t === 'light') document.documentElement.setAttribute('data-theme','light');
  else document.documentElement.removeAttribute('data-theme');
  const b = $('#themeToggle');
  if (b) b.textContent = (t === 'light') ? '☀' : '☾';
}
(function initTheme(){
  const btn = $('#themeToggle');
  if (!btn) return;
  let saved = null;
  try { saved = localStorage.getItem(THEME_KEY); } catch(e){}
  applyTheme(saved || 'dark');
  btn.addEventListener('click', () => {
    let cur = null;
    try { cur = localStorage.getItem(THEME_KEY); } catch(e){}
    const next = (cur === 'light') ? 'dark' : 'light';
    try { localStorage.setItem(THEME_KEY, next); } catch(e){}
    applyTheme(next);
  });
})();


/* ==========================================================
   ЗАКЛАДКИ
   ========================================================== */
const BM_KEY = 'itbase_bookmarks';
function getBookmarks(){
  try{
    const raw = localStorage.getItem(BM_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  }catch(e){ return []; }
}
function setBookmarks(list){
  try { localStorage.setItem(BM_KEY, JSON.stringify(list)); } catch(e){}
}
function isBookmarked(slug){ return getBookmarks().includes(slug); }
function toggleBookmark(slug){
  const list = getBookmarks();
  const i = list.indexOf(slug);
  if (i === -1) list.push(slug); else list.splice(i,1);
  setBookmarks(list);
  return i === -1;
}


/* ==========================================================
   КАРТОЧКИ
   ========================================================== */
function cardHTML(a, isOn){
  const href = absPath(a.url);
  return `
    <article class="card">
      <a class="card__cover" href="${href}">
        <img src="${esc(absPath(a.cover))}" alt="${esc(a.title)}" loading="lazy">
      </a>
      <div class="card__body">
        <div class="card__tags">
          ${a.tags.map(t => `<span class="tag">${esc(t)}</span>`).join('')}
        </div>
        <a href="${href}">
          <h2 class="card__title">${esc(a.title)}</h2>
        </a>
        <p class="card__excerpt">${esc(a.excerpt)}</p>
        <div class="card__meta">
          <span>${formatDate(a.date)}</span>
          <span class="dot">•</span>
          <span>${a.readTime} мин</span>
          <button class="card__bm${isOn?' is-on':''}" data-slug="${esc(a.slug)}"
                  title="В закладки" aria-label="В закладки">★</button>
        </div>
      </div>
    </article>`;
}

/* Оживляет кнопки ★ в готовых карточках: цвет по закладкам + клик */
function enhanceCards(root, cb){
  const bm = getBookmarks();
  $$('.card__bm', root).forEach(btn => {
    btn.classList.toggle('is-on', bm.includes(btn.dataset.slug));
    btn.addEventListener('click', e => {
      e.preventDefault();
      const slug = btn.dataset.slug;
      const on = toggleBookmark(slug);
      btn.classList.toggle('is-on', on);
      if (cb) cb(slug, on);
    });
  });
}


/* ==========================================================
   ГЛАВНАЯ
   (карточки уже лежат в HTML — их видят поисковики;
    скрипт добавляет фильтры по тегам и поиск)
   ========================================================== */
if ($('#grid') && !$('#bmExport')) initHome();

function initHome(){
  const grid = $('#grid');
  const chipsBox = $('#chips');
  const searchEl = $('#search');

  const urlTag = new URLSearchParams(location.search).get('tag');
  let activeTag = urlTag || null;
  let onlyBM = false;
  let query = '';

  const sorted = ARTICLES.slice().sort((a,b) => b.date.localeCompare(a.date));
  const tags = [...new Set(sorted.flatMap(a => a.tags))].sort();

  const chipAll = document.createElement('button');
  chipAll.className = 'chip';
  chipAll.textContent = 'Все';
  chipAll.onclick = () => { activeTag = null; onlyBM = false; updateURL(); render(); };
  chipsBox.appendChild(chipAll);

  tags.forEach(t => {
    const c = document.createElement('button');
    c.className = 'chip';
    c.textContent = t;
    c.onclick = () => {
      activeTag = (activeTag === t) ? null : t;
      updateURL();
      render();
    };
    chipsBox.appendChild(c);
  });

  const bmChip = document.createElement('button');
  bmChip.className = 'chip';
  bmChip.textContent = '★ Закладки';
  bmChip.onclick = () => { onlyBM = !onlyBM; render(); };
  chipsBox.appendChild(bmChip);

  if (searchEl) searchEl.addEventListener('input', e => {
    query = e.target.value.trim().toLowerCase();
    render();
  });

  function updateURL(){
    const url = new URL(location.href);
    if (activeTag) url.searchParams.set('tag', activeTag);
    else url.searchParams.delete('tag');
    history.replaceState(null, '', url);
  }

  function markChips(){
    $$('.chip', chipsBox).forEach(c => c.classList.remove('is-active'));
    if (!activeTag && !onlyBM) chipAll.classList.add('is-active');
    if (onlyBM) bmChip.classList.add('is-active');
    if (activeTag){
      const f = $$('.chip', chipsBox).find(c => c.textContent === activeTag);
      if (f) f.classList.add('is-active');
    }
  }

  function onToggle(slug){
    if (onlyBM && !isBookmarked(slug)) render();
  }

  function render(){
    markChips();
    const bm = getBookmarks();
    const list = sorted.filter(a => {
      if (onlyBM && !bm.includes(a.slug)) return false;
      if (activeTag && !a.tags.includes(activeTag)) return false;
      if (query){
        const hay = (a.title + ' ' + a.excerpt + ' ' + a.tags.join(' ')).toLowerCase();
        if (!hay.includes(query)) return false;
      }
      return true;
    });

    if (list.length === 0){
      grid.innerHTML = `<div class="empty" style="grid-column:1/-1">
        <b>Ничего не найдено</b>
        <span>Попробуй другой запрос или сбрось фильтры</span></div>`;
      return;
    }
    grid.innerHTML = list.map(a => cardHTML(a, bm.includes(a.slug))).join('');
    enhanceCards(grid, onToggle);
  }

  if (activeTag) {
    render();
  } else {
    markChips();
    enhanceCards(grid, onToggle);
  }
}


/* ==========================================================
   СТАТЬЯ (страница уже готова, здесь только оживляем)
   ========================================================== */
if ($('#article-view') && $('#article-body')) initArticle();

function initArticle(){
  const view = $('#article-view');
  const slug = view.dataset.slug;
  const body = $('#article-body');

  // Подсветка кода
  if (window.Prism){
    try { Prism.highlightAllUnder(body); } catch(e){}
  }

  // Кнопки «Копировать» у блоков кода
  $$('pre', body).forEach(pre => {
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.type = 'button';
    btn.textContent = 'Копировать';
    btn.addEventListener('click', async () => {
      const codeEl = pre.querySelector('code');
      const text = (codeEl || pre).innerText;
      try { await navigator.clipboard.writeText(text); }
      catch(e){
        const ta = document.createElement('textarea');
        ta.value = text; ta.style.position='fixed'; ta.style.opacity='0';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); } catch(_){}
        ta.remove();
      }
      btn.textContent = 'Скопировано';
      btn.classList.add('is-done');
      setTimeout(() => {
        btn.textContent = 'Копировать';
        btn.classList.remove('is-done');
      }, 1600);
    });
    pre.appendChild(btn);
  });

  // Оглавление: подсветка текущего раздела
  const links = $$('#toc a');
  const heads = $$('h2, h3', body).filter(h => h.id);
  if (links.length && 'IntersectionObserver' in window){
    const spy = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting){
          links.forEach(l => l.classList.toggle(
            'is-active', l.getAttribute('href') === '#' + en.target.id));
        }
      });
    }, { rootMargin: '-80px 0px -70% 0px' });
    heads.forEach(h => spy.observe(h));
  }

  // Закладка
  const bmBtn = $('#bmBtn');
  if (bmBtn){
    if (isBookmarked(slug)){
      bmBtn.classList.add('is-on');
      bmBtn.textContent = '★ В закладках';
    }
    bmBtn.addEventListener('click', () => {
      const nowOn = toggleBookmark(slug);
      bmBtn.classList.toggle('is-on', nowOn);
      bmBtn.textContent = nowOn ? '★ В закладках' : '★ В закладки';
    });
  }

  // Поделиться (берём канонический адрес, а не случайный из строки браузера)
  const canon = $('link[rel="canonical"]');
  const pageUrl = canon ? canon.href : location.href;
  const shareText = ($('h1', view) || {}).textContent || document.title;
  const tg = $('#shareTg');
  const vk = $('#shareVk');
  const cp = $('#shareCopy');
  if (tg) tg.addEventListener('click', () => {
    window.open('https://t.me/share/url?url=' + encodeURIComponent(pageUrl) +
                '&text=' + encodeURIComponent(shareText), '_blank');
  });
  if (vk) vk.addEventListener('click', () => {
    window.open('https://vk.com/share.php?url=' + encodeURIComponent(pageUrl) +
                '&title=' + encodeURIComponent(shareText), '_blank');
  });
  if (cp) cp.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(pageUrl); }
    catch(e){
      const ta = document.createElement('textarea');
      ta.value = pageUrl; ta.style.position='fixed'; ta.style.opacity='0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch(_){}
      ta.remove();
    }
    const old = cp.textContent;
    cp.textContent = 'Скопировано';
    setTimeout(() => cp.textContent = old, 1500);
  });

  // «Читай дальше» — карточки уже в HTML, оживляем звёздочки
  const rel = $('#related');
  if (rel) enhanceCards(rel);

  // Полоса прогресса чтения
  const bar = $('#progress');
  if (bar){
    let ticking = false;
    const upd = () => {
      const h = document.documentElement;
      const t = h.scrollHeight - h.clientHeight;
      bar.style.width = t > 0 ? (h.scrollTop / t * 100) + '%' : '0%';
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking){ ticking = true; requestAnimationFrame(upd); }
    }, { passive: true });
    upd();
  }
}


/* ==========================================================
   ЗАКЛАДКИ (страница)
   ========================================================== */
if ($('#bmExport')) initBookmarksPage();

function initBookmarksPage(){
  const grid = $('#grid');

  function render(){
    const bm = getBookmarks();
    const list = ARTICLES
      .filter(a => bm.includes(a.slug))
      .sort((a,b) => b.date.localeCompare(a.date));

    if (list.length === 0){
      grid.innerHTML = `<div class="empty" style="grid-column:1/-1;padding:70px 0">
        <b>Пока пусто</b>
        <span>Открой любую статью и нажми «★ В закладки»</span>
        <p style="margin-top:20px">
          <a href="/" style="color:var(--accent)">← Ко всем статьям</a>
        </p></div>`;
      return;
    }
    grid.innerHTML = list.map(a => cardHTML(a, true)).join('');
    enhanceCards(grid, slug => {
      if (!isBookmarked(slug)) render();
    });
  }

  $('#bmExport').addEventListener('click', () => {
    const bm = getBookmarks();
    if (bm.length === 0){ alert('Список пуст.'); return; }
    const data = { version:1, exportedAt:new Date().toISOString(), bookmarks:bm };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type:'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `itbase-bookmarks-${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  const file = $('#bmFile');
  $('#bmImport').addEventListener('click', () => file.click());
  file.addEventListener('change', e => {
    const f = e.target.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      try{
        const parsed = JSON.parse(reader.result);
        const incoming = Array.isArray(parsed) ? parsed :
                         Array.isArray(parsed.bookmarks) ? parsed.bookmarks : [];
        if (incoming.length === 0){ alert('В файле нет закладок.'); return; }
        const valid = new Set(ARTICLES.map(a => a.slug));
        const merged = new Set(getBookmarks());
        let added = 0;
        incoming.forEach(s => {
          if (valid.has(s) && !merged.has(s)){ merged.add(s); added++; }
        });
        setBookmarks([...merged]);
        render();
        alert(`Импортировано: ${added}`);
      }catch(err){
        alert('Не удалось прочитать файл.');
      }
    };
    reader.readAsText(f);
    file.value = '';
  });

  $('#bmClear').addEventListener('click', () => {
    if (getBookmarks().length === 0) return;
    if (confirm('Удалить все закладки?')){ setBookmarks([]); render(); }
  });

  render();
}


/* ==========================================================
   404 — показать случайные статьи
   ========================================================== */
if ($('#grid404')) init404();

function init404(){
  const grid = $('#grid404');
  const rand = ARTICLES.slice().sort(() => Math.random() - .5).slice(0, 3);
  grid.innerHTML = rand.map(a => cardHTML(a, isBookmarked(a.slug))).join('');
  enhanceCards(grid);
}


/* ==========================================================
   УВЕДОМЛЕНИЕ О COOKIE
   Показывается один раз; ответ хранится в localStorage.
   ========================================================== */
(function initCookieBanner() {
  const KEY = 'itbase_cookie_ok';

  try {
    if (localStorage.getItem(KEY) === '1') return;
  } catch (e) { return; }

  const banner = document.createElement('div');
  banner.className = 'cookie-banner';
  banner.innerHTML = `
    <div class="cookie-banner__text">
      Сайт использует cookie и память браузера: для закладок, темы оформления
      и статистики посещений. Подробнее — в
      <a href="/privacy.html">Политике конфиденциальности</a>.
    </div>
    <button class="cookie-banner__btn" type="button">Понятно</button>
  `;
  document.body.appendChild(banner);

  setTimeout(() => banner.classList.add('is-open'), 400);

  banner.querySelector('.cookie-banner__btn').addEventListener('click', () => {
    try { localStorage.setItem(KEY, '1'); } catch (e) {}
    banner.classList.remove('is-open');
    setTimeout(() => banner.remove(), 350);
  });
})();

/* ==========================================================
   РАЗМЕР ШРИФТА (доступность)
   ========================================================== */
(function initFontSize() {
  const KEY = 'itbase_font_scale';
  let scale = 1;
  try { scale = parseFloat(localStorage.getItem(KEY)) || 1; } catch (e) {}
  // Ограничения: 0.85 (меньше) — 1.4 (больше)
  scale = Math.max(0.85, Math.min(1.4, scale));
  document.documentElement.style.setProperty('--font-scale', scale);
  // Применяем масштаб к body через CSS-переменную
  function applyScale() {
    // Увеличиваем базовый шрифт article-body, заголовков, etc.
    document.documentElement.style.fontSize = (16 * scale) + 'px';
  }
  applyScale();

  const smaller = document.getElementById('fontSmaller');
  const larger = document.getElementById('fontLarger');
  if (smaller) smaller.addEventListener('click', () => {
    scale = Math.max(0.85, scale - 0.1);
    try { localStorage.setItem(KEY, scale.toFixed(2)); } catch (e) {}
    applyScale();
  });
  if (larger) larger.addEventListener('click', () => {
    scale = Math.min(1.4, scale + 0.1);
    try { localStorage.setItem(KEY, scale.toFixed(2)); } catch (e) {}
    applyScale();
  });
})();

/* ==========================================================
   КНОПКА ПЕЧАТЬ / PDF
   ========================================================== */
(function initPrintButton() {
  const btn = document.getElementById('sharePrint');
  if (!btn) return;
  btn.addEventListener('click', () => {
    // Удаляем ad-слоты перед печатью
    document.querySelectorAll('.ad-slot').forEach(el => el.style.display = 'none');
    setTimeout(() => window.print(), 100);
  });
})();

/* ==========================================================
   ЗАПОМИНАНИЕ ПОЗИЦИИ ЧТЕНИЯ
   ========================================================== */
(function initReadingProgress() {
  const articleView = document.getElementById('article-view');
  if (!articleView) return;
  // Получаем slug из data-slug или из URL
  const slug = articleView.dataset.slug ||
               new URLSearchParams(location.search).get('a') ||
               (location.pathname.match(/\/articles\/([^.]+)\.html/) || [])[1];
  if (!slug) return;

  const KEY = 'itbase_read_pos_' + slug;
  const NOTICE_KEY = 'itbase_read_notice_' + slug;

  // Восстанавливаем позицию
  let savedPos = 0;
  try { savedPos = parseInt(localStorage.getItem(KEY) || '0', 10); } catch (e) {}
  if (savedPos > 500) {
    // Показываем уведомление, продолжить ли
    let noticeDismissed = false;
    try { noticeDismissed = localStorage.getItem(NOTICE_KEY) === '1'; } catch (e) {}
    if (!noticeDismissed) {
      const notice = document.createElement('div');
      notice.className = 'read-progress-notice is-visible';
      notice.innerHTML = `
        <span>Ты остановился на ${Math.round(savedPos / window.innerHeight * 100)}% статьи.</span>
        <a href="#" id="resumeReading">Продолжить →</a>
        <button id="dismissNotice" aria-label="Закрыть">×</button>
      `;
      document.body.appendChild(notice);

      const resume = notice.querySelector('#resumeReading');
      const dismiss = notice.querySelector('#dismissNotice');

      resume.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({ top: savedPos, behavior: 'smooth' });
        notice.remove();
      });

      dismiss.addEventListener('click', () => {
        notice.remove();
        try { localStorage.setItem(NOTICE_KEY, '1'); } catch (e) {}
      });

      // Автоскрытие через 15 секунд
      setTimeout(() => {
        if (notice.parentNode) {
          notice.classList.remove('is-visible');
          setTimeout(() => notice.remove(), 300);
        }
      }, 15000);
    }
  }

  // Сохранение при скролле (debounced)
  let ticking = false;
  let lastSave = 0;
  function savePos() {
    const y = window.scrollY;
    // Сохраняем только если прокрутил значительно
    if (y > 500) {
      try { localStorage.setItem(KEY, String(y)); } catch (e) {}
    }
    ticking = false;
  }
  window.addEventListener('scroll', () => {
    if (!ticking) {
      ticking = true;
      // Не чаще раза в 3 секунды
      const now = Date.now();
      if (now - lastSave > 3000) {
        lastSave = now;
        requestAnimationFrame(savePos);
      } else {
        ticking = false;
      }
    }
  }, { passive: true });
  // Финальное сохранение при уходе со страницы
  window.addEventListener('beforeunload', savePos);
})();

/* ==========================================================
   SERVICE WORKER (PWA офлайн)
   ========================================================== */
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      // Тихо: SW — приятный бонус, не должен ломать сайт
    });
  });
}
