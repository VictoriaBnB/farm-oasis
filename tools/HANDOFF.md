# Handoff notes (state as of 2026-10-29)

Read `tools/README.md` first for how the site is put together. This file is the
"where things stand" summary for the next working session.

## Done today
- 5 new pages (property pages, things-to-do, monthly stays, book direct), favicons, FAQ + breadcrumb schema,
  corrected geo (48.6612, -123.4434), postal code V8L 5T8, phone 250-889-3111, image sitemap, IndexNow pings.
- Config-driven pricing (`assets/site-config.js`): seasonal nightly, 15%/25% off 7+/14+ nights, monthly
  totals ($5,995 suite / $17,000 smart home), tax-inclusive wording everywhere.
- `Site Manager.pyw`: pause/hide a home, edit rates, analytics token, Publish (commit + push).
- Photo hero (Pat Bay sunset), one-time reveals, "from $X/night" on stay cards.
- Cloudflare Web Analytics beacon enabled (token in config). Baseline for traffic starts 2026-10-29.

## Facts discovered (verify before changing strategy)
- Airbnb: both listings only bookable for 30+ nights (checked Nov/Dec 2026 and Jul 2027). Suite Airbnb monthly
  total $6,554 incl. tax; smart home $19,745 (Nov) / $23,335 (Jul). Suite base nightly on Airbnb ~ $284.
- Airbnb iCal feeds show no reservations in the next 12 months (the "booked" ranges are rolling advance-notice blocks).
- Airbnb shows 4.84 (77 reviews) suite + 5.0 (7) smart home; site still says 4.9 / 88 (owner's choice).
- Nearby 2BR comps all-in: Nov $216-$400/night, Jul $255-$850. 4BR: Nov $550-$875, Jul $930-$2,450.
- Google Business Profile exists ("Modern Farm Oasis", category Bed & breakfast, phone 250-889-3111).

## Open items (need the owner)
- Google Business Profile: add photos, description mentioning self-catering, Farmstay/Vacation home rental as
  secondary categories, and start collecting Google reviews (review link from the profile).
- Payment option for non-Canadian guests (Interac only today).
- Review count/rating on site vs Airbnb.
- If short stays are ever re-opened on Airbnb, keep Airbnb nightly >= direct nightly.

## Ideas for a visual pass (next session)
- Real hero photography: the property photos in `img/` are only 480-720px wide; a 2000px+ wide exterior/patio
  shot (or a 15s drone/walkthrough clip) would replace the generic sunset hero. Export originals from the
  owner's phone/Airbnb at full size, then regenerate galleries at 1200px.
- Embedded map section (Google Maps place embed, no API key needed).
- "Compare the two homes" table on the home page.
- Logo mark in the nav (the favicon house works as a starting point).
- Google reviews widget once GBP has reviews.
