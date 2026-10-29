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

## Visual pass (later on 2026-10-29)
- Home + property pages got a split hero: sage brand panel (title, copy, buttons, four facts) beside a real photo of the
  Suite kitchen with the farm view (`img/suite-interior-detail.webp`, the only clean 1440px property photo). The stats bar and
  the gold Superhost banner were folded into the hero panel (the Superhost claim was repeated five times above the fold).
- House logo mark (favicon drawing, inline SVG) in the nav and footer on every page; the nav's "Superhost" badge was dropped.
- "The two homes, side by side" table under the stay cards on the home page (prices via the existing config hooks).
- Key-less Google Maps embed + address bar under the location grid (home, Suite, Smart Home, Monthly); `hasMap` in the schema.
- Fixed a real layout bug: the About mosaic overflowed the page by 74px on desktop (grid images needed `minmax(0,1fr)`).
- New social image `img/og/suite-kitchen-farm-view.jpg` (1200x630) for the home page; sitemap lists the hero photo.
- `tools/shot.py`: headless-Chrome screenshots + checks (see README). Every page passed desktop + mobile before the push.
- Photos found in `C:/Users/RWERK/Downloads/BBreakfast` but NOT used: `Kitchen.jpg`/`cubbords.jpg` have a composited
  "Bed & Breakfast" caption (inaccurate), `living2_tv.jpg` (Smart Home great room) and `living_room_tv3.jpg` (Suite living room)
  have a composited TV welcome screen. If the owner is happy with the TV mock-up, `living2_tv.jpg` (1440px) would make a much
  sharper Smart Home hero than the current 720px kitchen photo — one `hero_split(...)` argument in `tools/gen_pages.py`.

## Facts discovered (verify before changing strategy)
- Airbnb: both listings only bookable for 30+ nights (checked Nov/Dec 2026 and Jul 2027). Suite Airbnb monthly
  total $6,554 incl. tax; smart home $19,745 (Nov) / $23,335 (Jul). Suite base nightly on Airbnb ~ $284.
- Airbnb iCal feeds show no reservations in the next 12 months (the "booked" ranges are rolling advance-notice blocks).
- Airbnb shows 4.84 (77 reviews) suite + 5.0 (7) smart home; site still says 4.9 / 88 (owner's choice).
- Nearby 2BR comps all-in: Nov $216-$400/night, Jul $255-$850. 4BR: Nov $550-$875, Jul $930-$2,450.
- Google Business Profile exists ("Modern Farm Oasis", category Bed & breakfast, phone 250-889-3111).

## Open items (need the owner)
- Google Business Profile is DONE (owner, Oct 29: photos etc.). The remaining gap is Google reviews: there are none yet.
  Airbnb reviews don't carry over, so the first ones have to be asked for, guest by guest, after checkout (post-stay
  message/text with the GBP review link, a QR card in the welcome binder). Never incentivise reviews (Google policy).
  Once a few exist: add a "reviews on Google" line/widget to the site, and link to the profile from the footer.
- Payment option for non-Canadian guests (Interac only today).
- Review count/rating on site vs Airbnb.
- If short stays are ever re-opened on Airbnb, keep Airbnb nightly >= direct nightly.

## Ideas for next time
- Photography is still the biggest lever: an exterior/patio shot at 2000px+ (or a short walkthrough clip) and full-size
  exports of the gallery photos from Airbnb (most are 480-720px). The hero and galleries are ready to take them.
- Google reviews widget once the Google Business Profile has reviews.
- Ranking for "Sidney B&B": the on-page side is done (FAQ answer, map, schema, consistent address/phone) and the Google
  Business Profile is set up. What moves the needle now is Google reviews (see Open items) — the map pack ranks
  profiles with reviews above profiles without, and a self-catering farm stay with zero reviews won't show for "B&B".
