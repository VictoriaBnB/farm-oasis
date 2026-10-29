/* victoriabnb.ca — shared behaviour: property status (open / paused / hidden),
   "from" prices, scroll reveals, analytics. Loaded with defer on every page. */
(function () {
  'use strict';
  const CFG = window.SITE_CONFIG || {};
  const NAMES = { suite: 'The Suite', smarthome: 'The Smart Home' };

  /* ── property status ─────────────────────────────────────────────── */
  function statusOf(prop) { const p = CFG.properties && CFG.properties[prop]; return (p && p.status) || 'open'; }
  function noteOf(prop) { const p = CFG.properties && CFG.properties[prop]; return (p && p.note) || ''; }

  function applyStatus() {
    const props = Object.keys(CFG.properties || {});
    props.forEach(function (prop) {
      const st = statusOf(prop), note = noteOf(prop);
      document.querySelectorAll('[data-prop="' + prop + '"]').forEach(function (el) {
        if (el.tagName === 'OPTION') {
          el.disabled = st !== 'open';
          el.hidden = st === 'hidden';
          el.textContent = el.textContent.replace(/ \(unavailable\)$/, '') + (st === 'open' ? '' : ' (unavailable)');
          return;
        }
        el.classList.toggle('prop-paused', st === 'paused');
        el.classList.toggle('prop-hidden', st === 'hidden');
        if (st === 'hidden') el.setAttribute('hidden', ''); else el.removeAttribute('hidden');
        el.querySelectorAll('.prop-note').forEach(function (n) { n.textContent = note; n.hidden = !note; });
      });
    });
    // booking form: make sure an available property is selected
    const sel = document.getElementById('bProperty');
    if (sel) {
      const cur = sel.options[sel.selectedIndex];
      if (cur && cur.disabled) {
        const ok = Array.prototype.find.call(sel.options, function (o) { return !o.disabled; });
        if (ok) { sel.value = ok.value; if (typeof window.onPropertyChange === 'function') window.onPropertyChange(); }
      }
      const anyOpen = Array.prototype.some.call(sel.options, function (o) { return !o.disabled; });
      const form = document.getElementById('bookingForm');
      if (form && !anyOpen) {
        form.querySelectorAll('input,select,textarea,button').forEach(function (i) { i.disabled = true; });
        const msg = document.createElement('p');
        msg.className = 'prop-closed-msg';
        msg.textContent = 'We are not taking new bookings right now. Please check back soon.';
        form.parentNode.insertBefore(msg, form);
      }
    }
    // property page banner
    const page = document.body.getAttribute('data-prop-page');
    if (page && statusOf(page) !== 'open') {
      const b = document.createElement('div');
      b.className = 'prop-banner';
      b.innerHTML = '<strong>' + (NAMES[page] || 'This home') + ' is not taking bookings right now.</strong> ' +
        (noteOf(page) ? noteOf(page) + ' ' : '') + 'Our other home may be available — <a href="/#stays">see the stays</a>.';
      const hero = document.querySelector('.hero');
      if (hero && hero.parentNode) hero.parentNode.insertBefore(b, hero.nextSibling); else document.body.prepend(b);
    }
  }

  /* ── from-prices / monthly figures ───────────────────────────────── */
  function fillPrices() { if (window.Pricing) { window.Pricing.renderFromPrices(); } }

  /* ── one-time reveal on scroll (respects reduced motion) ─────────── */
  function reveals() {
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const bot = /bot|crawl|spider|slurp|HeadlessChrome|Lighthouse|facebookexternalhit|Twitterbot|Applebot|PageSpeed|GTmetrix/i.test(navigator.userAgent);
    if (bot) return;
    const targets = document.querySelectorAll('.section-title, .stay-card, .price-card, .guide-card, .quote-card, .rule-card, .about-hl, .step, .tile, .amenity, .ttd-block');
    if (reduce || !('IntersectionObserver' in window) || !targets.length) return;
    const groups = new Map();
    targets.forEach(function (el) {
      el.classList.add('reveal');
      const parent = el.parentNode;
      const n = groups.get(parent) || 0; groups.set(parent, n + 1);
      el.style.transitionDelay = (Math.min(n, 8) * 55) + 'ms';
    });
    const pendingEls = [];
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(function (el) {
      const r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.9) { el.classList.add('in'); } else { io.observe(el); pendingEls.push(el); }
    });
    // belt and braces: also reveal on scroll by geometry, and reveal everything before printing
    let ticking = false;
    function sweep() {
      ticking = false;
      const limit = window.innerHeight * 0.95;
      for (let i = pendingEls.length - 1; i >= 0; i--) {
        const el = pendingEls[i];
        if (el.classList.contains('in')) { pendingEls.splice(i, 1); continue; }
        const r = el.getBoundingClientRect();
        if (r.top < limit && r.bottom > 0) { el.classList.add('in'); io.unobserve(el); pendingEls.splice(i, 1); }
      }
    }
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(sweep); } }, { passive: true });
    window.addEventListener('resize', sweep);
    window.addEventListener('beforeprint', function () { pendingEls.forEach(function (el) { el.classList.add('in'); }); });
  }

  /* ── analytics (only if configured) ──────────────────────────────── */
  function analytics() {
    const a = CFG.analytics || {};
    if (a.goatcounter) {
      const s = document.createElement('script');
      s.async = true; s.src = 'https://gc.zgo.at/count.js';
      s.setAttribute('data-goatcounter', 'https://' + a.goatcounter + '.goatcounter.com/count');
      document.head.appendChild(s);
    }
    if (a.ga4) {
      const s = document.createElement('script');
      s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(a.ga4);
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date()); window.gtag('config', a.ga4, { anonymize_ip: true });
    }
  }

  /* ── nav shadow once scrolled ─────────────────────────────────────── */
  function navShadow() {
    const nav = document.getElementById('mainNav'); if (!nav) return;
    const on = function () { nav.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', on, { passive: true }); on();
  }

  function init() { applyStatus(); fillPrices(); reveals(); navShadow(); analytics(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
