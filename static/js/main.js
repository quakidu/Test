/**
 * Körper im Einklang – Interaktion der Startseite.
 *
 * Enthält: mobiles Menü, Sticky-Header, Scroll-Reveal, Scrollspy
 * und animierte Kennzahlen.
 */
(function () {
  'use strict';

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Mobiles Menü ─────────────────────────────────────────────────── */
  function initMenu() {
    var burger = document.getElementById('burger');
    var nav = document.getElementById('nav');
    var backdrop = document.getElementById('nav-backdrop');
    if (!burger || !nav) return;

    function setMenu(open) {
      nav.classList.toggle('is-open', open);
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute(
        'aria-label',
        open ? burger.dataset.labelClose : burger.dataset.labelOpen
      );
      document.body.classList.toggle('nav-open', open);

      if (backdrop) {
        if (open) {
          backdrop.hidden = false;
          // Reflow erzwingen, damit die Transition greift.
          void backdrop.offsetWidth;
          backdrop.classList.add('is-visible');
        } else {
          backdrop.classList.remove('is-visible');
          window.setTimeout(function () {
            if (!nav.classList.contains('is-open')) backdrop.hidden = true;
          }, 250);
        }
      }
    }

    burger.addEventListener('click', function () {
      setMenu(burger.getAttribute('aria-expanded') !== 'true');
    });

    if (backdrop) backdrop.addEventListener('click', function () { setMenu(false); });

    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) setMenu(false);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        setMenu(false);
        burger.focus();
      }
    });

    // Beim Wechsel auf Desktop-Breite aufräumen.
    window.matchMedia('(min-width: 861px)').addEventListener('change', function (event) {
      if (event.matches) setMenu(false);
    });
  }

  /* ── Sticky-Header ────────────────────────────────────────────────── */
  function initHeader() {
    var header = document.getElementById('site-header');
    if (!header) return;

    var ticking = false;
    function update() {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    }, { passive: true });
    update();
  }

  /* ── Scroll-Reveal ────────────────────────────────────────────────── */
  function initReveal() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length) return;

    items.forEach(function (item) {
      if (item.dataset.revealDelay) {
        item.style.setProperty('--reveal-delay', item.dataset.revealDelay);
      }
    });

    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
      items.forEach(function (item) { item.classList.add('is-visible'); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    items.forEach(function (item) { observer.observe(item); });
  }

  /* ── Scrollspy für die Navigation ─────────────────────────────────── */
  function initScrollspy() {
    var links = Array.prototype.slice.call(document.querySelectorAll('.nav__link[href^="#"]'));
    if (!links.length || !('IntersectionObserver' in window)) return;

    var map = {};
    var sections = [];
    links.forEach(function (link) {
      var section = document.querySelector(link.getAttribute('href'));
      if (section) {
        map[section.id] = link;
        sections.push(section);
      }
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (link) { link.classList.remove('is-current'); });
        var active = map[entry.target.id];
        if (active) active.classList.add('is-current');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });

    sections.forEach(function (section) { observer.observe(section); });
  }

  /* ── Animierte Kennzahlen ─────────────────────────────────────────── */
  function initCounters() {
    var values = Array.prototype.slice.call(document.querySelectorAll('[data-count]'));
    if (!values.length) return;
    if (prefersReducedMotion || !('IntersectionObserver' in window)) return;

    function countUp(el) {
      var raw = el.dataset.count || '';
      var match = raw.match(/^(\D*)(\d+)(.*)$/);
      if (!match) return;

      var prefix = match[1];
      var target = parseInt(match[2], 10);
      var suffix = match[3];
      var duration = 1200;
      var start = null;

      function frame(timestamp) {
        if (start === null) start = timestamp;
        var progress = Math.min((timestamp - start) / duration, 1);
        // Ease-out, damit der Zähler weich ausläuft.
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = prefix + Math.round(target * eased) + suffix;
        if (progress < 1) window.requestAnimationFrame(frame);
      }
      window.requestAnimationFrame(frame);
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          countUp(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });

    values.forEach(function (value) { observer.observe(value); });
  }

  /* ── Kleinkram ────────────────────────────────────────────────────── */
  function initMisc() {
    var year = document.getElementById('year');
    if (year) year.textContent = String(new Date().getFullYear());
  }

  function init() {
    initMenu();
    initHeader();
    initReveal();
    initScrollspy();
    initCounters();
    initMisc();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
