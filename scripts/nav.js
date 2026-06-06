(function () {
  const INDEX_SECTIONS = ['setup', 'prototype', 'features'];

  function isIndexPage() {
    const page = location.pathname.split('/').pop() || 'index.html';
    return page === '' || page === 'index.html';
  }

  function clearActive() {
    document.querySelectorAll('.nav-links a').forEach((a) => a.classList.remove('active'));
  }

  function activateHome() {
    const el = document.querySelector('.nav-links a[data-nav="home"]');
    if (el) el.classList.add('active');
  }

  function activateHash(id) {
    const el = document.querySelector('.nav-links a[href="#' + id + '"]');
    if (el) el.classList.add('active');
  }

  function indexScrollSpy() {
    const trigger = window.innerHeight * 0.28;
    let current = null;
    INDEX_SECTIONS.forEach((id) => {
      const el = document.getElementById(id);
      if (el && el.getBoundingClientRect().top + window.scrollY - trigger <= window.scrollY) {
        current = id;
      }
    });
    clearActive();
    if (current) activateHash(current);
    else activateHome();
  }

  function currentPage() {
    const page = location.pathname.split('/').pop();
    if (!page || page === '/') return 'index.html';
    return page;
  }

  function otherPageActive() {
    const page = currentPage();
    clearActive();
    document.querySelectorAll('.nav-links a').forEach((a) => {
      const href = a.getAttribute('href') || '';
      if (href.startsWith('#')) return;
      const base = href.split('#')[0];
      if (base && base === page) a.classList.add('active');
    });
    const cta = document.querySelector('.nav-cta');
    if (cta) {
      const ctaBase = (cta.getAttribute('href') || '').split('#')[0];
      cta.classList.toggle('active', ctaBase === page);
    }
  }

  if (isIndexPage() && document.querySelector('.nav-links a[data-nav="home"]')) {
    window.addEventListener('scroll', indexScrollSpy, { passive: true });
    window.addEventListener('hashchange', () => {
      const id = location.hash.slice(1);
      clearActive();
      if (INDEX_SECTIONS.includes(id)) activateHash(id);
      else indexScrollSpy();
    });
    indexScrollSpy();
  } else if (document.querySelector('.nav-links')) {
    otherPageActive();
  }
})();
