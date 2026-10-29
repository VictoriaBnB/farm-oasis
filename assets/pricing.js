/* victoriabnb.ca — pricing engine. Reads SITE_CONFIG from assets/site-config.js.
   Nothing here needs editing to change rates: use Site Manager or site-config.js. */
(function (global) {
  'use strict';
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const NAMES = { suite: 'The Suite', smarthome: 'The Smart Home' };

  function pricing() { return (global.SITE_CONFIG && global.SITE_CONFIG.pricing) || {}; }
  function cfg(prop) { return pricing()[prop] || null; }
  function props() { return Object.keys(pricing()).filter(k => typeof pricing()[k] === 'object'); }
  function status(prop) {
    const p = global.SITE_CONFIG && global.SITE_CONFIG.properties && global.SITE_CONFIG.properties[prop];
    return (p && p.status) || 'open';
  }
  function note(prop) {
    const p = global.SITE_CONFIG && global.SITE_CONFIG.properties && global.SITE_CONFIG.properties[prop];
    return (p && p.note) || '';
  }

  function pad(n) { return String(n).padStart(2, '0'); }
  function mmdd(d) { return pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function inRange(md, from, to) { return from <= to ? (md >= from && md <= to) : (md >= from || md <= to); }
  function parseISO(iso) { const p = iso.split('-').map(Number); return new Date(p[0], p[1] - 1, p[2], 12); }
  function fmtMoney(n) { return '$' + Math.round(n).toLocaleString('en-CA'); }
  function fmtMD(md) { const p = md.split('-').map(Number); return MONTHS[p[0] - 1] + ' ' + p[1]; }

  function seasonFor(prop, date) {
    const c = cfg(prop); if (!c) return null;
    const md = mmdd(date);
    for (const s of c.seasons || []) if (inRange(md, s.from, s.to)) return s;
    return null;
  }
  function nightlyFor(prop, date) {
    const c = cfg(prop); if (!c) return 0;
    const s = seasonFor(prop, date);
    return s ? s.nightly : (c.defaultNightly || 0);
  }
  function fromPrice(prop) {
    const c = cfg(prop); if (!c) return 0;
    const rates = (c.seasons || []).map(s => s.nightly);
    if (c.defaultNightly) rates.push(c.defaultNightly);
    return rates.length ? Math.min.apply(null, rates) : 0;
  }
  function maxPrice(prop) {
    const c = cfg(prop); if (!c) return 0;
    const rates = (c.seasons || []).map(s => s.nightly);
    if (c.defaultNightly) rates.push(c.defaultNightly);
    return rates.length ? Math.max.apply(null, rates) : 0;
  }
  function monthlyPerNight(prop) {
    const c = cfg(prop); if (!c || !c.monthly) return 0;
    return c.monthly.total / c.monthly.perNights;
  }
  function lowestPerNight(prop) {
    const m = monthlyPerNight(prop);
    return m ? Math.min(m, fromPrice(prop)) : fromPrice(prop);
  }

  /* Price a stay. Returns null when dates are missing or invalid. */
  function quote(prop, checkinISO, checkoutISO) {
    const c = cfg(prop); if (!c || !checkinISO || !checkoutISO) return null;
    const a = parseISO(checkinISO), b = parseISO(checkoutISO);
    const nights = Math.round((b - a) / 86400000);
    if (!(nights > 0)) return null;
    let subtotal = 0; const seasons = [];
    for (let i = 0; i < nights; i++) {
      const d = new Date(a); d.setDate(a.getDate() + i);
      const s = seasonFor(prop, d);
      const rate = s ? s.nightly : (c.defaultNightly || 0);
      subtotal += rate;
      const name = s ? s.name : 'Standard';
      const last = seasons[seasons.length - 1];
      if (last && last.name === name && last.rate === rate) last.nights++; else seasons.push({ name, rate, nights: 1 });
    }
    let accom = subtotal, discountPct = 0, discountAmt = 0, label = '', tier = null;
    const m = c.monthly;
    if (m && nights >= m.minNights) {
      accom = Math.round(m.total / m.perNights * nights);
      discountAmt = Math.max(0, subtotal - accom);
      discountPct = subtotal ? Math.round(discountAmt / subtotal * 100) : 0;
      label = 'Monthly rate (' + m.minNights + '+ nights)';
      tier = 'monthly';
    } else {
      let best = null;
      for (const t of c.discounts || []) if (nights >= t.minNights && (!best || t.minNights > best.minNights)) best = t;
      if (best) {
        discountPct = best.pct;
        discountAmt = Math.round(subtotal * best.pct / 100);
        accom = subtotal - discountAmt;
        label = best.pct + '% off for ' + best.minNights + '+ nights';
        tier = best.minNights;
      }
    }
    const cleaning = c.cleaningFee || 0;
    return { prop, nights, subtotal, seasons, accom, discountPct, discountAmt, label, tier, cleaning, total: accom + cleaning, perNight: accom / nights, avgNightly: subtotal / nights };
  }

  /* Seasons grouped by name, in config order, for display: [{name, ranges:'Nov 1 – Mar 31', nightly, current}] */
  function seasonRows(prop) {
    const c = cfg(prop); if (!c) return [];
    const today = mmdd(new Date()), rows = [], byName = {};
    for (const s of c.seasons || []) {
      let r = byName[s.name];
      if (!r) { r = byName[s.name] = { name: s.name, ranges: [], nightly: s.nightly, current: false }; rows.push(r); }
      r.ranges.push(fmtMD(s.from) + ' – ' + fmtMD(s.to));
      if (inRange(today, s.from, s.to)) r.current = true;
    }
    return rows;
  }

  function cardsHTML(prop) {
    const c = cfg(prop); if (!c) return '';
    const rows = seasonRows(prop);
    const from = fromPrice(prop);
    const seasonRowsHTML = rows.map(r =>
      '<div class="price-fee-row' + (r.current ? ' price-row-now' : '') + '"><span>' + r.name + '<small>' + r.ranges.join(', ') + (r.current ? ' · now' : '') + '</small></span><strong>' + fmtMoney(r.nightly) + '</strong></div>').join('');
    const discounts = (c.discounts || []).slice().sort((x, y) => x.minNights - y.minNights);
    const bestPct = discounts.length ? Math.max.apply(null, discounts.map(d => d.pct)) : 0;
    const minPct = discounts.length ? Math.min.apply(null, discounts.map(d => d.pct)) : 0;
    const discountRows = discounts.map(d => '<div class="price-fee-row"><span>' + d.minNights + '+ nights</span><strong>' + d.pct + '% off</strong></div>').join('');
    // worked example: 7 nights starting today
    const t = new Date(); const ci = t.getFullYear() + '-' + pad(t.getMonth() + 1) + '-' + pad(t.getDate());
    const ex = discounts.length ? quote(prop, ci, (function () { const e = new Date(t); e.setDate(t.getDate() + discounts[0].minNights); return e.getFullYear() + '-' + pad(e.getMonth() + 1) + '-' + pad(e.getDate()); })()) : null;
    const exRow = ex ? '<div class="price-fee-row"><span>e.g. ' + ex.nights + ' nights this month, incl. cleaning &amp; taxes</span><strong>' + fmtMoney(ex.total) + '</strong></div>' : '';
    const m = c.monthly;
    const monthlyCard = m ? '<div class="price-card">' +
      '<div class="price-badge" style="background:var(--gold)">Lowest Rate — ' + m.minNights + '+ Nights</div>' +
      '<div class="price-label">Monthly Stay</div>' +
      '<div class="price-amount"><sup>$</sup>' + Math.round(m.total / m.perNights).toLocaleString('en-CA') + '</div>' +
      '<div class="price-per">per night · CAD · taxes included</div>' +
      '<div class="price-save">All year, any season</div>' +
      '<div class="price-fees">' +
      '<div class="price-fee-row"><span>' + m.perNights + ' nights</span><strong>' + fmtMoney(m.total) + '</strong></div>' +
      '<div class="price-fee-row"><span>+ Cleaning fee</span><strong>' + fmtMoney(c.cleaningFee || 0) + '</strong></div>' +
      '<div class="price-fee-row"><span>Total for ' + m.perNights + ' nights, taxes incl.</span><strong>' + fmtMoney(m.total + (c.cleaningFee || 0)) + '</strong></div>' +
      '</div></div>' : '';
    return '<div class="price-card">' +
      '<div class="price-label">Nightly Rate</div>' +
      '<div class="price-amount"><sup>$</sup>' + from.toLocaleString('en-CA') + '</div>' +
      '<div class="price-per">per night from · CAD · taxes included</div>' +
      '<div class="price-fees price-seasons">' + seasonRowsHTML +
      '<div class="price-fee-row"><span>Cleaning fee (one-time)</span><strong>' + fmtMoney(c.cleaningFee || 0) + '</strong></div>' +
      '<div class="price-fee-row"><span>Max guests</span><strong>' + (c.maxGuests || '') + '</strong></div>' +
      '</div></div>' +
      (discounts.length ? '<div class="price-card featured">' +
        '<div class="price-badge">Best Value — ' + discounts[0].minNights + '+ Nights</div>' +
        '<div class="price-label">Stay Longer, Pay Less</div>' +
        '<div class="price-amount">' + (minPct === bestPct ? bestPct : minPct + '–' + bestPct) + '<sup>%</sup></div>' +
        '<div class="price-per">off the nightly rate</div>' +
        '<div class="price-save">The longer the stay, the bigger the discount</div>' +
        '<div class="price-fees">' + discountRows + exRow + '</div></div>' : '') +
      monthlyCard;
  }

  function renderPricingCards() {
    for (const prop of props()) {
      const grid = document.getElementById(prop === 'suite' ? 'pricingGridSuite' : prop === 'smarthome' ? 'pricingGridSmarthome' : 'pricingGrid_' + prop);
      if (!grid) continue;
      grid.innerHTML = cardsHTML(prop);
    }
  }
  function renderFromPrices() {
    document.querySelectorAll('[data-from-price]').forEach(el => { el.textContent = fmtMoney(fromPrice(el.getAttribute('data-from-price'))); });
    document.querySelectorAll('[data-monthly-total]').forEach(el => { const c = cfg(el.getAttribute('data-monthly-total')); if (c && c.monthly) el.textContent = fmtMoney(c.monthly.total); });
    document.querySelectorAll('[data-monthly-night]').forEach(el => { const c = cfg(el.getAttribute('data-monthly-night')); if (c && c.monthly) el.textContent = fmtMoney(c.monthly.total / c.monthly.perNights); });
    document.querySelectorAll('[data-monthly-min]').forEach(el => { const c = cfg(el.getAttribute('data-monthly-min')); if (c && c.monthly) el.textContent = c.monthly.minNights; });
    document.querySelectorAll('[data-monthly-nights]').forEach(el => { const c = cfg(el.getAttribute('data-monthly-nights')); if (c && c.monthly) el.textContent = c.monthly.perNights; });
    document.querySelectorAll('[data-cleaning-fee]').forEach(el => { const c = cfg(el.getAttribute('data-cleaning-fee')); if (c) el.textContent = fmtMoney(c.cleaningFee || 0); });
    document.querySelectorAll('[data-ladder]').forEach(el => { const c = cfg(el.getAttribute('data-ladder')); if (!c) return; const ds = (c.discounts || []).slice().sort((a, b) => a.minNights - b.minNights); el.textContent = ds.map(d => d.pct + '% off ' + d.minNights + '+ nights').join(', '); });
    document.querySelectorAll('[data-max-discount]').forEach(el => { const c = cfg(el.getAttribute('data-max-discount')); if (c) el.textContent = Math.max.apply(null, (c.discounts || [{ pct: 0 }]).map(d => d.pct)) + '%'; });
  }

  global.Pricing = { cfg, props, status, note, quote, nightlyFor, seasonFor, fromPrice, maxPrice, monthlyPerNight, lowestPerNight, seasonRows, cardsHTML, renderPricingCards, renderFromPrices, fmtMoney, NAMES };
  global.renderPricingCards = renderPricingCards;
  global.fmtMoney = fmtMoney;
})(typeof window !== 'undefined' ? window : globalThis);
