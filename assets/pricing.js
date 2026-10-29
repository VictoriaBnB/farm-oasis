/* victoriabnb.ca — shared pricing module.
   Loaded by index.html and the property pages. Edit ONLY PRICING_CONFIG
   to change rates; cards, calculator and schema all derive from it. */

/* ══════════════════════════════════════════════════════════════════
   PRICING CONFIG — edit ONLY this object to update all pricing.
   Pricing cards, booking calculator, and JSON-LD schema are all
   derived from these numbers; nothing else needs to change.
   ══════════════════════════════════════════════════════════════════ */
const PRICING_CONFIG = {
  suite: {
    nightly:          380,   // $ CAD – nightly base rate
    cleaningFee:      150,   // $ one-time cleaning fee (keep as-is unless changing)
    weeklyTotal:     2139,   // $ total for weeklyMin nights before cleaning fee
    weeklyMin:          7,   // night threshold to unlock weekly rate
    monthlyTotal:    8961,   // $ total for monthlyExNights before cleaning fee
    monthlyExNights:   30,   // nights the monthlyTotal covers (used for $/night calc)
    monthlyMin:        30,   // night threshold to unlock monthly rate
  },
  smarthome: {
    nightly:          880,   // $ CAD – nightly base rate
    cleaningFee:      175,   // $ one-time cleaning fee (keep as-is unless changing)
    weeklyTotal:     5500,   // $ total for weeklyMin nights before cleaning fee
    weeklyMin:          7,   // night threshold to unlock weekly rate
    monthlyTotal:   15000,   // $ total for monthlyExNights before cleaning fee
    monthlyExNights:   30,   // nights the monthlyTotal covers (used for $/night calc)
    monthlyMin:        28,   // night threshold to unlock monthly rate (NOTE: 28, not 30)
  }
};

/* ── Derived PRICING object used by the calculator ────────────────────
   Auto-computed from PRICING_CONFIG — do not edit directly.         */
const PRICING = {};
(function buildPricing() {
  for (const [key, c] of Object.entries(PRICING_CONFIG)) {
    const wRate = c.weeklyTotal / c.weeklyMin;
    const mRate = c.monthlyTotal / c.monthlyExNights;
    PRICING[key] = {
      base:  c.nightly,
      clean: c.cleaningFee,
      tiers: [
        { min: c.monthlyMin, rate: mRate,
          label: 'Monthly discount (' + ((1 - mRate/c.nightly)*100).toFixed(1) + '%)' },
        { min: c.weeklyMin,  rate: wRate,
          label: 'Weekly discount ('  + ((1 - wRate /c.nightly)*100).toFixed(1) + '%)' }
      ]
    };
  }
})();

/* ── Formatting helpers ───────────────────────────────────────────────── */
function fmtMoney(n) { return '$' + Math.round(n).toLocaleString('en-CA'); }
function fmtRate(n)  { return (n === Math.round(n)) ? n.toLocaleString() : n.toFixed(2); }

/* ── Render pricing cards from PRICING_CONFIG ────────────────────────── */
function renderPricingCards() {
  const props = {
    suite:     { gridId: 'pricingGridSuite',     guests: 6 },
    smarthome: { gridId: 'pricingGridSmarthome', guests: 8 },
  };
  for (const [key, def] of Object.entries(props)) {
    const c  = PRICING_CONFIG[key];
    const p  = PRICING[key];
    const wt = p.tiers[1];  // weekly tier
    const mt = p.tiers[0];  // monthly tier
    const wSave      = c.nightly * c.weeklyMin       - c.weeklyTotal;
    const mSave      = c.nightly * c.monthlyExNights - c.monthlyTotal;
    const wWithClean = c.weeklyTotal  + c.cleaningFee;
    const mWithClean = c.monthlyTotal + c.cleaningFee;
    const wPct = ((1 - wt.rate / c.nightly) * 100).toFixed(1);
    const mPct = ((1 - mt.rate / c.nightly) * 100).toFixed(1);
    document.getElementById(def.gridId).innerHTML = [
      /* Nightly */
      `<div class="price-card">
        <div class="price-label">Nightly Rate</div>
        <div class="price-amount"><sup>$</sup>${fmtRate(c.nightly)}</div>
        <div class="price-per">per night · CAD</div>
        <div class="price-fees">
          <div class="price-fee-row"><span>Cleaning fee (one-time)</span><strong>${fmtMoney(c.cleaningFee)}</strong></div>
          <div class="price-fee-row"><span>Check-in</span><strong>3:00 PM</strong></div>
          <div class="price-fee-row"><span>Check-out</span><strong>10:00 AM</strong></div>
          <div class="price-fee-row"><span>Max guests</span><strong>${def.guests}</strong></div>
        </div>
      </div>`,
      /* Weekly */
      `<div class="price-card featured">
        <div class="price-badge">Best Value — ${c.weeklyMin}+ Nights</div>
        <div class="price-label">Weekly Stay</div>
        <div class="price-amount"><sup>$</sup>${fmtRate(wt.rate)}</div>
        <div class="price-per">per night · ${wPct}% off</div>
        <div class="price-save">Save ${fmtMoney(wSave)} per week</div>
        <div class="price-fees">
          <div class="price-fee-row"><span>${c.weeklyMin} nights subtotal</span><strong>${fmtMoney(c.weeklyTotal)}</strong></div>
          <div class="price-fee-row"><span>+ Cleaning fee</span><strong>${fmtMoney(c.cleaningFee)}</strong></div>
          <div class="price-fee-row"><span>Total for ${c.weeklyMin} nights</span><strong>${fmtMoney(wWithClean)}</strong></div>
        </div>
      </div>`,
      /* Monthly */
      `<div class="price-card">
        <div class="price-badge" style="background:var(--gold)">Best Rate — ${mt.min}+ Nights</div>
        <div class="price-label">Monthly Stay</div>
        <div class="price-amount"><sup>$</sup>${fmtRate(mt.rate)}</div>
        <div class="price-per">per night · ${mPct}% off</div>
        <div class="price-save">Save ${fmtMoney(mSave)} per month</div>
        <div class="price-fees">
          <div class="price-fee-row"><span>${c.monthlyExNights} nights subtotal</span><strong>${fmtMoney(c.monthlyTotal)}</strong></div>
          <div class="price-fee-row"><span>+ Cleaning fee</span><strong>${fmtMoney(c.cleaningFee)}</strong></div>
          <div class="price-fee-row"><span>Total for ${c.monthlyExNights} nights</span><strong>${fmtMoney(mWithClean)}</strong></div>
        </div>
      </div>`
    ].join('');
  }
}
