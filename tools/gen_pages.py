"""Generates the static pages that share the site chrome:
/the-suite/, /the-smart-home/, /things-to-do-sidney-north-saanich/,
/monthly-stays-sidney-north-saanich/, /book-direct/

    python tools/gen_pages.py            (run from the repo root)

Edit the copy in this file, re-run, commit. Rates and availability are NOT in
here: they come from assets/site-config.js at page load (see Site Manager).
"""
import json, os, re, sys, html as H

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATING = "4.9"
REVIEWS = "88"
BASE = "https://victoriabnb.ca"

GUIDES = [
    ("/swartz-bay-ferry-stay/", "10 minutes to Swartz Bay", "Near Swartz Bay Ferry"),
    ("/farmhouse-stay-victoria-bc/", "Saanich Peninsula · near Victoria", "Farmhouse Stay near Victoria"),
    ("/sidney-north-saanich-vacation-rental/", "5 minutes to Sidney", "Sidney & North Saanich"),
    ("/victoria-airport-accommodation/", "3 minutes to YYJ", "Near Victoria Airport (YYJ)"),
    ("/butchart-gardens-accommodation/", "15 minutes to Butchart Gardens", "Near Butchart Gardens"),
    ("/group-vacation-rental-victoria/", "The Smart Home · sleeps 8", "Groups & Family Reunions"),
    ("/things-to-do-sidney-north-saanich/", "Beaches, gardens, islands", "Things to Do Nearby"),
    ("/monthly-stays-sidney-north-saanich/", "28+ nights · furnished", "Monthly &amp; Extended Stays"),
    ("/book-direct/", "Lowest rates, no fees", "Why Book Direct"),
]

# ── photo lists come straight from the index galleries (single source) ──────
idx = open(os.path.join(REPO, "index.html"), encoding="utf-8").read()
def gallery(block_id):
    m = re.search(r'<div class="gallery-block" id="%s"[^>]*>(.*?)\n      </div>\n    </div>\n' % block_id, idx, re.S)
    body = m.group(1)
    items = re.findall(r'<div class="gitem" data-cat="([^"]+)" data-src="([^"]+)" onclick="openLb\(this\)"><img src="([^"]+)" alt="([^"]*)"', body)
    tabs = re.findall(r'<button class="gtab[^"]*" onclick="filterGal\(\'([^\']+)\',this\)">([^<]+)</button>', body)
    return items, tabs
SUITE_PHOTOS, SUITE_TABS = gallery("gallery-suite")
SMART_PHOTOS, SMART_TABS = gallery("gallery-smarthome")
assert len(SUITE_PHOTOS) > 20 and len(SMART_PHOTOS) > 40, (len(SUITE_PHOTOS), len(SMART_PHOTOS))

FAV = ('<link rel="icon" href="/favicon.ico" sizes="32x32">\n'
       '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
       '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
       '<link rel="manifest" href="/site.webmanifest">\n'
       '<meta name="theme-color" content="#3D5E41">')
HERO_BG = ('<picture class="hero-bg"><source media="(max-width:700px)" srcset="/img/pat-bay-beach-sunset-800.webp">'
           '<img src="/img/pat-bay-beach-sunset.webp" width="1600" height="1200" alt="" fetchpriority="high" decoding="async"></picture>')

def esc(s):
    return H.escape(s, quote=True)

def head(p):
    url = BASE + p["slug"]
    body_attr = p.get("body_attr", "")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["desc"])}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="New Bright Modern Farm Oasis">
<meta property="og:locale" content="en_CA">
<meta property="og:title" content="{esc(p["title"])}">
<meta property="og:description" content="{esc(p["desc"])}">
<meta property="og:image" content="{BASE}{p["og"]}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(p["title"])}">
<meta name="twitter:description" content="{esc(p["desc"])}">
<meta name="twitter:image" content="{BASE}{p["og"]}">
{FAV}
<script type="application/ld+json">
{json.dumps(p["jsonld"], indent=2, ensure_ascii=False)}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/guides.css">
<link rel="stylesheet" href="/assets/ui.css">
{p.get("extra_css", "")}
<script src="/assets/site-config.js"></script>
<script src="/assets/pricing.js"></script>
<script src="/assets/site.js" defer></script>
</head>
<body{body_attr}>
'''

def chrome_top(crumb):
    mobile_guides = "".join(f'<a href="{u}">{n}</a>' for u, e, n in GUIDES)
    return f'''
<div class="announce-bar">
  <span>⭐ Airbnb Superhost · {RATING}/5 from {REVIEWS} verified reviews</span>
  <span class="announce-sep">|</span>
  <span>3 min to Victoria Airport · 10 min to Swartz Bay ferry</span>
  <span class="announce-sep">|</span>
  <a href="/#booking">Book direct — lowest rates, no platform fees ↓</a>
</div>

<nav id="mainNav">
  <div class="nav-inner">
    <a class="nav-logo" href="/" style="text-decoration:none">
      <span class="nav-logo-name">New Bright Modern Farm Oasis</span>
      <span class="nav-logo-sub">North Saanich · Sidney, BC</span>
    </a>
    <ul class="nav-links">
      <li><a href="/the-suite/">The Suite</a></li>
      <li><a href="/the-smart-home/">The Smart Home</a></li>
      <li><a href="/#reviews">Reviews</a></li>
      <li><a href="/#pricing">Rates</a></li>
      <li><a href="/#availability">Availability</a></li>
      <li><a href="/#booking" class="nav-cta">Book Direct</a></li>
    </ul>
    <button class="hamburger" id="menuBtn" aria-label="Open menu"><span></span><span></span><span></span></button>
  </div>
</nav>
<div class="mobile-menu" id="mobileMenu">
  <button class="mobile-close" id="menuClose" aria-label="Close menu">×</button>
  <a href="/">Home</a>
  <a href="/the-suite/">The Suite</a>
  <a href="/the-smart-home/">The Smart Home</a>
  <a href="/#gallery-suite">Photos</a>
  <a href="/#pricing">Rates</a>
  <a href="/#availability">Availability</a>
  {mobile_guides}
  <a href="/#booking" style="color:var(--sage-dark);font-weight:600">Book Direct ↓</a>
</div>

<div class="crumbs"><a href="/">Farm Oasis</a> &rsaquo; {crumb}</div>
'''

def hero(eyebrow, h1, sub, btn1=("/#booking", "Check Dates &amp; Book Direct"), btn2=None):
    b2 = f'\n      <a href="{btn2[0]}" class="btn-outline">{btn2[1]}</a>' if btn2 else ""
    return f'''
<div class="hero hero-photo hero-short">
  {HERO_BG}
  <div class="hero-content">
    <div class="hero-eyebrow"><span class="hero-eyebrow-star">★★★★★</span> {eyebrow}</div>
    <h1>{h1}</h1>
    <p class="hero-sub">{sub}</p>
    <div class="hero-btns">
      <a href="{btn1[0]}" class="btn-primary">{btn1[1]}</a>{b2}
    </div>
  </div>
</div>
'''

def section_head(eyebrow, title, center=False):
    c = ' style="text-align:center"' if center else ""
    r = ' style="margin-left:auto;margin-right:auto"' if center else ""
    return f'''    <div class="eyebrow"{c}>{eyebrow}</div>
    <h2 class="section-title"{c}>{title}</h2>
    <div class="rule"{r}></div>
'''

def faq_section(items, eyebrow="Good to know", title="Questions"):
    lis = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items)
    return f'''
<section class="faq-section">
  <div class="wrap">
{section_head(eyebrow, title, center=True)}    <div class="faq-list">{lis}</div>
  </div>
</section>
'''

def faq_ld(slug, items):
    return {"@type": "FAQPage", "@id": f"{BASE}{slug}#faq",
            "mainEntity": [{"@type": "Question", "name": H.unescape(re.sub('<[^>]+>', '', q)),
                            "acceptedAnswer": {"@type": "Answer", "text": H.unescape(re.sub('<[^>]+>', '', a))}} for q, a in items]}

def cta_band(h2="Book Direct &amp; Save", p="Send us your dates and we'll confirm availability and a quote within a few hours. No platform fees when you book direct.", btn="Send a Booking Inquiry"):
    return f'''
<div class="cta-band">
  <h2>{h2}</h2>
  <p>{p}</p>
  <a href="/#booking" class="btn-primary">{btn}</a>
</div>
'''

def guides_section(exclude):
    cards = "".join(f'<a class="guide-card" href="{u}"><span class="guide-eyebrow">{e}</span><span class="guide-title">{n}</span><span class="guide-go">Read guide &rarr;</span></a>'
                    for u, e, n in GUIDES if u != exclude)
    return f'''
<section class="guides-section">
  <div class="wrap">
{section_head("Plan your stay", "Area Guides", center=True)}  </div>
  <div class="guides-grid">{cards}</div>
</section>
'''

def quotes_section(quotes, eyebrow=None, title="What Guests Say"):
    eyebrow = eyebrow or f"{RATING}★ from {REVIEWS} guest reviews"
    cards = "".join(f'<div class="quote-card"><div class="quote-stars">★★★★★</div><p class="quote-text">&ldquo;{q}&rdquo;</p><div class="quote-who"><strong>{w}</strong> · {where}</div></div>' for q, w, where in quotes)
    return f'''
<section class="reviews-section">
  <div class="wrap">
{section_head(eyebrow, title, center=True)}  </div>
  <div class="quotes-grid">{cards}</div>
  <p style="text-align:center;margin-top:2rem"><a href="/#reviews" style="color:var(--sage-dark);font-size:14px">Read more reviews &rarr;</a></p>
</section>
'''

def footer():
    guides = "".join(f'<li><a href="{u}">{n}</a></li>' for u, e, n in GUIDES if u not in ("/monthly-stays-sidney-north-saanich/", "/book-direct/"))
    return f'''
<footer>
  <div class="footer-grid">
    <div>
      <div class="footer-name">New Bright Modern Farm Oasis</div>
      <div class="footer-loc">1345 Munro Road · North Saanich (Sidney), BC V8L 5S9 · Canada</div>
      <p>Two modern vacation rentals on one farm property: a 2-bedroom + loft suite and a 4-bedroom smart home. Steps from Pat Bay Beach, minutes to Victoria Airport, Swartz Bay ferry &amp; Butchart Gardens.</p>
      <p style="margin-top:0.75rem;font-size:11px;color:rgba(255,255,255,0.28)">Check-in 3:00 PM · Check-out 10:00 AM · Self-catering (no breakfast served) · No pets, smoking or vaping</p>
    </div>
    <div class="footer-col">
      <h4>The Farm</h4>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/the-suite/">The Suite &middot; 2BR + Loft</a></li>
        <li><a href="/the-smart-home/">The Smart Home &middot; 4BR</a></li>
        <li><a href="/#gallery-suite">Photos</a></li>
        <li><a href="/#reviews">Guest Reviews</a></li>
        <li><a href="/#pricing">Rates &amp; Policies</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Book</h4>
      <ul>
        <li><a href="/#availability">Check Availability</a></li>
        <li><a href="/#booking">Book Direct</a></li>
        <li><a href="/book-direct/">Why Book Direct</a></li>
        <li><a href="/monthly-stays-sidney-north-saanich/">Monthly Stays</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Area Guides</h4>
      <ul>{guides}</ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© <span id="footerYear">2026</span> New Bright Modern Farm Oasis · North Saanich, BC</span>
  </div>
</footer>
'''

MENU_JS = '''
<script>
(function(){
  var m=document.getElementById('mobileMenu');
  document.getElementById('menuBtn').onclick=function(){m.classList.add('open')};
  document.getElementById('menuClose').onclick=function(){m.classList.remove('open')};
  m.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){m.classList.remove('open')})});
  var y=document.getElementById('footerYear');if(y)y.textContent=new Date().getFullYear();
})();
</script>
'''

LIGHTBOX_HTML = '''
<div class="lb" id="lightbox">
  <button class="lb-close" onclick="closeLb()" aria-label="Close image viewer">×</button>
  <button class="lb-arrow" id="lbPrev" aria-label="Previous image">&#8592;</button>
  <img class="lb-img" id="lbImg" src="" alt="">
  <button class="lb-arrow" id="lbNext" aria-label="Next image">&#8594;</button>
  <div class="lb-counter" id="lbCounter"></div>
</div>
'''

GALLERY_JS = '''
<script>
function filterGal(cat,btn){
  document.querySelectorAll('.gtab').forEach(function(t){t.classList.remove('active')});
  btn.classList.add('active');
  document.querySelectorAll('.gitem').forEach(function(el){el.style.display=(cat==='all'||el.dataset.cat===cat)?'block':'none';});
}
var lbImgs=[],lbIdx=0;
function openLb(el){
  var vis=[].slice.call(document.querySelectorAll('.gitem')).filter(function(e){return e.style.display!=='none'});
  lbImgs=vis.map(function(e){return {src:e.dataset.src,alt:e.querySelector('img').alt}});
  lbIdx=vis.indexOf(el);showLb();
  document.getElementById('lightbox').classList.add('open');document.body.style.overflow='hidden';
}
function showLb(){
  document.getElementById('lbImg').src=lbImgs[lbIdx].src;
  document.getElementById('lbImg').alt=lbImgs[lbIdx].alt;
  document.getElementById('lbCounter').textContent=(lbIdx+1)+' / '+lbImgs.length;
}
function closeLb(){document.getElementById('lightbox').classList.remove('open');document.body.style.overflow='';}
document.getElementById('lbPrev').onclick=function(){lbIdx=(lbIdx-1+lbImgs.length)%lbImgs.length;showLb()};
document.getElementById('lbNext').onclick=function(){lbIdx=(lbIdx+1)%lbImgs.length;showLb()};
document.addEventListener('keydown',function(e){
  if(!document.getElementById('lightbox').classList.contains('open'))return;
  if(e.key==='Escape')closeLb();
  if(e.key==='ArrowLeft'){lbIdx=(lbIdx-1+lbImgs.length)%lbImgs.length;showLb()}
  if(e.key==='ArrowRight'){lbIdx=(lbIdx+1)%lbImgs.length;showLb()}
});
document.getElementById('lightbox').addEventListener('click',function(e){if(e.target===this)closeLb()});
document.querySelectorAll('.gitem').forEach(function(el){
  el.setAttribute('role','button');el.setAttribute('tabindex','0');
  var img=el.querySelector('img');el.setAttribute('aria-label','View larger photo: '+(img?img.alt:'photo'));
  el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();el.click();}});
});
</script>
'''

def gallery_section(photos, tabs, eyebrow, title, intro):
    tab_html = "".join(f'<button class="gtab{" active" if i == 0 else ""}" onclick="filterGal(\'{k}\',this)">{label}</button>' for i, (k, label) in enumerate(tabs))
    items = "\n      ".join(f'<div class="gitem" data-cat="{cat}" data-src="{src}" onclick="openLb(this)"><img src="{thumb}" alt="{alt}" loading="lazy"><div class="gitem-overlay"><div class="gitem-zoom">+</div></div></div>' for cat, src, thumb, alt in photos)
    return f'''
<section id="photos" class="gallery-section">
  <div class="wrap">
    <div class="gallery-block">
{section_head(eyebrow, title)}      <p style="font-size:15px;color:var(--mid);max-width:720px;margin-bottom:1.25rem">{intro}</p>
      <div class="gtabs">{tab_html}</div>
      <div class="gallery-grid">
      {items}
      </div>
    </div>
  </div>
</section>
'''

def amenities_section(items, eyebrow="Everything included", title="Amenities"):
    cells = "".join(f'<div class="amenity"><span class="am-check">✓</span>{a}</div>' for a in items)
    return f'''
<section id="amenities" class="amenities-section">
  <div class="wrap">
{section_head(eyebrow, title)}    <div class="amenities-grid">{cells}</div>
  </div>
</section>
'''

def rates_section(prop, grid_id, eyebrow, title, name):
    return f'''
<section id="rates" class="pricing-section">
  <div class="wrap" data-prop="{prop}">
{section_head(eyebrow, title)}    <p class="pricing-intro">Direct rates are set <strong>below our Airbnb pricing</strong>, with no platform fee on top. Nightly rates change with the season, and every night costs less the longer you stay: <strong><span data-ladder="{prop}"></span></strong>, plus a flat monthly rate for longer stays. The only extra is a one-time cleaning fee, and the booking form applies every discount automatically.</p>
    <div class="pricing-grid" id="{grid_id}" style="margin-top:1.5rem"></div>
    <div class="prop-paused-msg">{name} isn&rsquo;t taking bookings right now. <span class="prop-note"></span></div>
    <p style="font-size:13.5px;color:var(--mid);margin-top:1.25rem;max-width:760px">Prices in Canadian dollars. Check-in 3:00 PM, check-out 10:00 AM. Self-catering. No pets, smoking or vaping.</p>
    <div class="cancel-box">
      <div class="cancel-title">📋 Cancellation Policy — Moderate</div>
      <div class="cancel-row"><div class="cancel-dot"></div><div><strong>Full refund</strong> if cancelled at least 5 days before check-in</div></div>
      <div class="cancel-row"><div class="cancel-dot"></div><div><strong>Partial refund</strong> if cancelled within 5 days of check-in</div></div>
    </div>
  </div>
</section>
<script>renderPricingCards();</script>
'''

def breadcrumb_ld(slug, name):
    return {"@type": "BreadcrumbList", "@id": f"{BASE}{slug}#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Farm Oasis", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": f"{BASE}{slug}"}]}

def webpage_ld(slug, title, desc, image, about=None, extra=None):
    d = {"@type": "WebPage", "@id": f"{BASE}{slug}#webpage", "url": f"{BASE}{slug}", "name": title, "description": desc,
         "isPartOf": {"@id": f"{BASE}/#website"}, "primaryImageOfPage": f"{BASE}{image}", "breadcrumb": {"@id": f"{BASE}{slug}#breadcrumb"}}
    if about: d["about"] = about
    if extra: d.update(extra)
    return d

LOC_LIST = '''<ul class="dist-list">
        <li class="dist-item"><a href="https://www.google.com/maps/search/?api=1&amp;query=Patricia+Bay+Beach+North+Saanich+BC" target="_blank" rel="noopener">🏖️ &nbsp;Pat Bay Beach</a><span class="dist-time">2 min walk</span></li>
        <li class="dist-item"><a href="https://www.victoriaairport.com/" target="_blank" rel="noopener">✈️ &nbsp;Victoria Airport (YYJ)</a><span class="dist-time">3 min drive</span></li>
        <li class="dist-item"><a href="https://www.sidney.ca/" target="_blank" rel="noopener">🏘️ &nbsp;Sidney, BC</a><span class="dist-time">5 min drive</span></li>
        <li class="dist-item"><a href="https://seacider.ca/" target="_blank" rel="noopener">🍏 &nbsp;Sea Cider Farm &amp; Cidery</a><span class="dist-time">5 min drive</span></li>
        <li class="dist-item"><a href="https://bcparks.ca/lau-welnew-john-dean-park/" target="_blank" rel="noopener">🥾 &nbsp;John Dean Provincial Park</a><span class="dist-time">~5 min drive</span></li>
        <li class="dist-item"><a href="https://www.bcferries.com/" target="_blank" rel="noopener">⛴️ &nbsp;BC Ferries — Swartz Bay</a><span class="dist-time">10 min drive</span></li>
        <li class="dist-item"><a href="https://www.butchartgardens.com/" target="_blank" rel="noopener">🌸 &nbsp;Butchart Gardens</a><span class="dist-time">15 min drive</span></li>
        <li class="dist-item"><a href="https://www.tourismvictoria.com/" target="_blank" rel="noopener">🏛️ &nbsp;Downtown Victoria</a><span class="dist-time">~35 min drive</span></li>
      </ul>'''

def location_section(eyebrow, title, paras):
    ps = "".join(f"<p>{p}</p>" for p in paras)
    return f'''
<section class="location-section">
  <div class="loc-grid">
    <div>
{section_head(eyebrow, title)}      <div class="loc-body">{ps}</div>
    </div>
    <div>{LOC_LIST}</div>
  </div>
</section>
'''

def stay_card(prop):
    if prop == "suite":
        return '''      <div class="stay-card" data-prop="suite">
        <div class="stay-ribbon">Not taking bookings right now</div>
        <div class="stay-card-img"><img src="/img/suite-exterior-farm-views.webp" alt="2-bedroom + loft suite with farm views in North Saanich" loading="lazy"></div>
        <div class="stay-card-eyebrow">The Suite &middot; Sleeps 6</div>
        <h3 class="stay-card-title">2BR + Loft Suite</h3>
        <p class="stay-card-desc">A bright, brand-new suite with a private entrance and patio overlooking the farm. Two bedrooms with full ensuites, a queen loft and a powder room. Great for couples, small families or two couples travelling together.</p>
        <div class="stay-stats">
          <div class="stay-stat"><span class="stay-stat-num">2</span><span class="stay-stat-label">Bedrooms + Loft</span></div>
          <div class="stay-stat"><span class="stay-stat-num">2.5</span><span class="stay-stat-label">Bathrooms</span></div>
          <div class="stay-stat"><span class="stay-stat-num">6</span><span class="stay-stat-label">Max Guests</span></div>
        </div>
        <div class="stay-from">From <strong data-from-price="suite"></strong> <span>/ night</span> <span class="stay-from-note">· up to <span data-max-discount="suite"></span> off longer stays</span></div>
        <p class="prop-note" hidden></p>
        <a href="/the-suite/" class="btn-primary stay-link">Details, Photos &amp; Rates &rarr;</a>
      </div>'''
    return '''      <div class="stay-card" data-prop="smarthome">
        <div class="stay-ribbon">Not taking bookings right now</div>
        <div class="stay-card-img"><img src="/img/smart-home-chefs-kitchen-island.webp" alt="4-bedroom solar-powered smart home chef's kitchen" loading="lazy"></div>
        <div class="stay-card-eyebrow">The Smart Home &middot; Sleeps 8</div>
        <h3 class="stay-card-title">4BR Solar Smart Home</h3>
        <p class="stay-card-desc">A 4,500&nbsp;sq&nbsp;ft solar-powered home for families and groups: four bedrooms each with a private bathroom, a chef&rsquo;s kitchen that seats 12, a home gym and the same farm views. Step-free entry.</p>
        <div class="stay-stats">
          <div class="stay-stat"><span class="stay-stat-num">4</span><span class="stay-stat-label">Bedrooms</span></div>
          <div class="stay-stat"><span class="stay-stat-num">5.5</span><span class="stay-stat-label">Bathrooms</span></div>
          <div class="stay-stat"><span class="stay-stat-num">8</span><span class="stay-stat-label">Max Guests</span></div>
        </div>
        <div class="stay-from">From <strong data-from-price="smarthome"></strong> <span>/ night</span> <span class="stay-from-note">· up to <span data-max-discount="smarthome"></span> off longer stays</span></div>
        <p class="prop-note" hidden></p>
        <a href="/the-smart-home/" class="btn-primary stay-link">Details, Photos &amp; Rates &rarr;</a>
      </div>'''

def stays_section(which_first="suite"):
    order = ["suite", "smarthome"] if which_first == "suite" else ["smarthome", "suite"]
    cards = "\n".join(stay_card(p) for p in order)
    return f'''
<section class="stays-section">
  <div class="wrap">
{section_head("Two ways to stay", "Choose Your Space", center=True)}    <div class="stays-grid">
{cards}
    </div>
  </div>
</section>
'''

def about_section(eyebrow, title, paras, highlights, photos, anchor="about"):
    ps = "".join(f"<p>{p}</p>" for p in paras)
    hl = "".join(f'<div class="about-hl"><span class="hl-icon">{i}</span><div><div class="hl-title">{t}</div><div class="hl-sub">{s}</div></div></div>' for i, t, s in highlights)
    mosaic = "".join(f'<img src="{src}" class="{cls}" alt="{alt}" loading="lazy">' for src, cls, alt in photos)
    return f'''
<section id="{anchor}" class="about-section">
  <div class="wrap">
    <div class="about-grid">
      <div>
{section_head(eyebrow, title)}        <div class="about-body">{ps}</div>
        <div class="about-highlights">{hl}</div>
      </div>
      <div class="mosaic">{mosaic}</div>
    </div>
  </div>
</section>
'''

def facts_strip(items):
    cells = '<div class="stat-sep"></div>'.join(f'<div class="stat">{i}</div>' for i in items)
    return f'''
<div class="stats-bar">
  <div class="stats-bar-inner">
    {cells}
  </div>
</div>
'''

def rooms_section(eyebrow, title, rows, intro):
    cells = "".join(f'<div class="rule-card rule-ok"><span class="rule-icon">{i}</span><div class="rule-name">{n}</div><div class="rule-note">{d}</div></div>' for i, n, d in rows)
    return f'''
<section id="rooms" class="pricing-section" style="padding-top:4rem;padding-bottom:4rem">
  <div class="wrap">
{section_head(eyebrow, title)}    <p style="font-size:15px;color:var(--mid);max-width:760px">{intro}</p>
    <div class="rules-grid" style="margin-top:1.5rem">{cells}</div>
  </div>
</section>
'''

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: THE SUITE
# ═══════════════════════════════════════════════════════════════════════════
SUITE_FAQ = [
    ("Who is the suite best for?", "Couples, small families and two couples travelling together. There are two bedrooms with their own full bathrooms, a queen bed in the loft and a powder room off the living area, so up to six people can stay without anyone sharing a bathroom with strangers."),
    ("Is the suite private?", "Yes. It has its own entrance and patio, its own kitchen and laundry, and it is one of only two rentals on the farm. The second rental, the Smart Home, is a separate house."),
    ("What are the beds?", "A king bed in the master bedroom, a queen in the second bedroom and a queen in the loft. Premium linens, extra pillows and blankets are provided."),
    ("Do longer stays cost less?", "Yes. Stays of 7+ nights are discounted, 14+ nights more so, and a flat monthly rate applies to the longest stays. The booking form shows the discount instantly when you enter your dates."),
    ("How do I check in?", "Self check-in from 3:00 PM through the private entrance. Check-out is 10:00 AM. We send arrival details before your stay."),
    ("Is there parking?", "Yes, free parking on the property."),
    ("Can we rent a car nearby?", "The airport is 3 minutes away with the usual rental desks. If you'd rather book a car through Turo, ask us and we'll share a link."),
    ("Are pets allowed?", "No. The suite is pet-free and strictly smoke- and vape-free."),
]
SUITE_AMENITIES = ["Free high-speed WiFi", "Full kitchen: fridge &amp; freezer, oven &amp; stovetop, microwave", "Dishwasher", "Blender, kettle &amp; toaster",
                   "Cooking basics, dishes &amp; silverware", "Coffee &amp; coffee maker", "Dining table", "Washer &amp; dryer in suite",
                   "Rain shower in the master bath", "Full ensuite in bedroom 2", "Powder room off the living area", "Infloor heating",
                   "Smart TV", "Premium bed linens &amp; extra bedding", "Hair dryer, iron &amp; ironing board", "Shampoo, conditioner &amp; body soap",
                   "Private entrance", "Patio with outdoor seating", "Outdoor dining &amp; BBQ", "Free parking on premises", "Beach access — Pat Bay",
                   "Smoke &amp; carbon monoxide alarms", "Fire extinguisher &amp; first aid kit"]

suite = {
    "slug": "/the-suite/",
    "title": "The Suite: 2-Bedroom + Loft Farmhouse Suite near Sidney, BC | Farm Oasis",
    "desc": "New 2BR + loft suite near Sidney, BC with two ensuites, private entrance and farm-view patio. Sleeps 6, steps to the beach, 3 min to YYJ. Book direct.",
    "og": "/img/og/suite-exterior-farm-views.jpg",
    "body_attr": ' data-prop-page="suite"',
}
suite["jsonld"] = {"@context": "https://schema.org", "@graph": [
    webpage_ld(suite["slug"], suite["title"], suite["desc"], "/img/suite-exterior-farm-views.webp",
               about={"@id": f"{BASE}/#suite"}, extra={"mainEntity": {"@id": f"{BASE}/#suite"}}),
    breadcrumb_ld(suite["slug"], "The Suite"),
    faq_ld(suite["slug"], SUITE_FAQ),
]}
suite["body"] = (
    chrome_top("The Suite")
    + hero("The Suite &nbsp;·&nbsp; 2 bedrooms + loft &nbsp;·&nbsp; sleeps 6",
           "The Suite: <em>Two Bedrooms, a Loft</em> and the Farm Out the Window",
           "A brand-new, self-contained suite on our North Saanich farm: two bedrooms with their own full bathrooms, a queen loft, a bright open kitchen and a patio looking over the fields. Five minutes from Sidney, three from the airport.",
           btn2=("#photos", "See the Photos"))
    + facts_strip(['🛏️ <strong>2 bedrooms</strong>&nbsp;+ queen loft', '🚿 <strong>2.5 baths</strong>&nbsp;· 2 full ensuites', '👨‍👩‍👧‍👦 <strong>Sleeps 6</strong>&nbsp;· 3 real beds', '💰 <strong>From <span data-from-price="suite"></span></strong>&nbsp;/ night direct'])
    + about_section("Finished in 2025", "Everything New, Nothing Shared",
        ["The suite is the newer of our two rentals, finished in 2025 with new appliances, furniture and fixtures throughout. It has its own entrance, so you come and go without passing through anyone else's space, and the patio outside the door has seating for morning coffee or an evening glass of something from <a href=\"https://seacider.ca/\" target=\"_blank\" rel=\"noopener\" style=\"color:var(--sage-dark)\">Sea Cider</a> down the road.",
         "Inside, the living, dining and kitchen area is one bright open room with high ceilings and big windows onto the farm. The kitchen is fully equipped — full-size fridge and freezer, oven and stovetop, dishwasher, microwave, blender, kettle, toaster, and the pots, pans, dishes and basics you need to cook properly. A washer and dryer are in the suite.",
         "Both bedrooms have a full ensuite bathroom. The master has a king bed and a large bathroom with a walk-in rain shower; the second bedroom has a queen bed and its own full bath. Up the stairs, the loft holds a third queen bed, and a powder room off the living area serves the loft and guests.",
         "Outside the door: eagles over the fields, deer at the fence line, herons on the shore. Pat Bay Beach is a two-minute walk."],
        [("🛏️", "King + two queens", "Master, bedroom 2 and loft"), ("🚿", "Rain shower", "Plus a full ensuite in bedroom 2"), ("🧺", "Washer &amp; dryer", "Inside the suite"), ("🦅", "Farm &amp; wildlife views", "Eagles, deer, herons")],
        [("/img/suite-living-area-with-farm-views.webp", "tall", "Suite living area with farm views"), ("/img/suite-master-bath-rain-shower.webp", "sq", "Master bathroom rain shower"), ("/img/suite-loft-queen-bed.webp", "sq", "Queen bed in the loft")])
    + rooms_section("Sleeping &amp; bathrooms", "Who Sleeps Where",
        [("🛏️", "Master bedroom", "King bed · full ensuite with rain shower"), ("🛏️", "Bedroom 2", "Queen bed · full ensuite bathroom"), ("🛏️", "Loft", "Queen bed · up the stairs from the living area"), ("🚽", "Powder room", "Off the main living &amp; dining area"), ("👥", "Up to 6 guests", "Three beds, no sofa beds needed"), ("🧺", "Laundry", "Washer &amp; dryer in the suite")],
        "Three proper beds and two and a half bathrooms, so a family of five or two couples can spread out.")
    + gallery_section(SUITE_PHOTOS, SUITE_TABS, "Photos", "Inside the Suite", "Tap any photo to view it full size. All photos are of this suite and the farm it sits on.")
    + amenities_section(SUITE_AMENITIES)
    + rates_section("suite", "pricingGridSuite", "Rates", "Suite Rates &amp; Policies", "The Suite")
    + location_section("North Saanich, BC", "Where You Are", [
        "The farm sits on the Saanich Peninsula between Pat Bay and the airport, which means almost everything is close: the beach is a short walk, Sidney's waterfront and shops are five minutes, the Swartz Bay ferry ten, Butchart Gardens fifteen and downtown Victoria about thirty-five.",
        "If you're flying in late or out early, this is as convenient as it gets without sleeping in the terminal."])
    + quotes_section([
        ("'Bright Modern Farm Oasis' is a perfect description. Wonderful for a vacation with a day at Butchart Gardens. The master bath shower is as luxurious as it looks in the pictures.", "Joanna", "Vancouver, BC · Aug 2024"),
        ("The bright, modern, very clean farm house was beautiful and peaceful. The kitchen is well stocked. We enjoyed coffee on the back patio watching the cows graze on the neighbouring hill.", "Kyra", "St. Albert, AB · Oct 2024"),
        ("We were so impressed! Absolutely beautiful, modern home with a lovely patio overlooking farmland. My husband and I stayed with our 2 adult sons — plenty of room for all. Highly recommend!", "Sophie", "Vancouver, BC · Sep 2024")])
    + faq_section(SUITE_FAQ, title="Suite Questions")
    + cta_band("Book the Suite Direct", "Tell us your dates and we'll confirm availability and a quote within a few hours. A 50% deposit holds your booking; no platform fees.")
    + stays_section("smart")
    + guides_section(None)
    + footer() + LIGHTBOX_HTML + MENU_JS + GALLERY_JS
)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: THE SMART HOME
# ═══════════════════════════════════════════════════════════════════════════
SMART_FAQ = [
    ("How many people can stay?", "Up to 8 guests in four bedrooms: a king in the master and queens in the other three. Every bedroom has its own private bathroom, and there are 5.5 bathrooms in total."),
    ("Is the Smart Home wheelchair accessible?", "It has step-free access and a guest entrance wider than 32 inches (81 cm). If you have specific needs — bathroom layout, bed height, door widths inside the house — tell us in your inquiry and we'll confirm the details honestly before you book."),
    ("Do longer stays cost less?", "Yes. Stays of 7+ nights are discounted, 14+ nights more so, and a flat monthly rate applies to the longest stays. The booking form shows the discount instantly when you enter your dates."),
    ("Is there air conditioning?", "Yes. The house has air conditioning for summer and heating for the rest of the year."),
    ("Can we use the gym?", "Yes. The home gym with free weights, a treadmill and a Tacx Neo smart bike (bring your Zwift login) is included with the house."),
    ("Can we book the Smart Home and the Suite together?", "Yes. The two rentals sit on the same farm, so a group of up to 14 can book both and still have separate kitchens, bathrooms and front doors. Ask in your inquiry."),
    ("Can we host a party or event?", "No. Parties and events aren't permitted, and the house is pet-free and strictly smoke- and vape-free. Family dinners for the twelve the table seats are very much allowed."),
    ("How do we check in?", "Self check-in from 3:00 PM; check-out is 10:00 AM. There is ample parking on the property."),
]
SMART_AMENITIES = ["Telus gigabit fibre internet", "85&quot; Samsung Frame TV with Sonos Arc soundbar", "Netflix &amp; a Plex movie library", "Air conditioning &amp; heating",
                   "Chef's kitchen: 8-burner gas range with two ovens", "Two dishwashers, three sinks &amp; a pot filler", "Vitamix blender &amp; full cookware", "Dining table for 12 plus island seating",
                   "Four bedrooms, each with a private bathroom", "Bidet toilet in the master ensuite", "Soaker tub in the master ensuite", "Walk-in closet in the master",
                   "Home gym: free weights, treadmill, Tacx Neo smart bike", "Home office", "Full laundry room with washer &amp; dryer", "Large concrete patio with BBQ",
                   "Solar-powered home", "Exterior smart security system", "Step-free access, 32&quot;+ guest entrance", "Kid-friendly amenities",
                   "Ample free parking", "Beach access — Pat Bay", "Smoke &amp; carbon monoxide alarms, fire extinguisher"]

smart = {
    "slug": "/the-smart-home/",
    "title": "The Smart Home: 4-Bedroom Solar House near Sidney, BC | Farm Oasis",
    "desc": "4,500 sq ft solar smart home in North Saanich: 4 bedrooms with private baths, chef's kitchen for 12, gym, A/C, step-free access. Sleeps 8. Book direct.",
    "og": "/img/og/smart-home-chefs-kitchen-island.jpg",
    "body_attr": ' data-prop-page="smarthome"',
}
smart["jsonld"] = {"@context": "https://schema.org", "@graph": [
    webpage_ld(smart["slug"], smart["title"], smart["desc"], "/img/smart-home-chefs-kitchen-island.webp",
               about={"@id": f"{BASE}/#smarthome"}, extra={"mainEntity": {"@id": f"{BASE}/#smarthome"}}),
    breadcrumb_ld(smart["slug"], "The Smart Home"),
    faq_ld(smart["slug"], SMART_FAQ),
]}
smart["body"] = (
    chrome_top("The Smart Home")
    + hero("The Smart Home &nbsp;·&nbsp; 4 bedrooms, 5.5 baths &nbsp;·&nbsp; sleeps 8",
           "The Smart Home: <em>Four Bedrooms, Four Ensuites</em>, Room for Everyone",
           "A 4,500-square-foot solar-powered house built for families and groups: four bedrooms with private bathrooms, a kitchen that seats twelve, a gym, a home office and a wide patio over the farm. Step-free entry, three minutes from the airport.",
           btn2=("#photos", "See the Photos"))
    + facts_strip(['🛏️ <strong>4 bedrooms</strong>&nbsp;· king + 3 queens', '🚿 <strong>5.5 baths</strong>&nbsp;· every bedroom has one', '🍽️ <strong>Seats 12</strong>&nbsp;at the table', '💰 <strong>From <span data-from-price="smarthome"></span></strong>&nbsp;/ night direct'])
    + about_section("4,500 sq ft, solar-powered", "Built for a Full House",
        ["The Smart Home is the larger of our two rentals: a new build on the same North Saanich farm as the suite. The main level is open-concept — kitchen, dining and living room flow together under high ceilings — with big windows and doors out to a large concrete patio with a BBQ and the farm and valley views our guests keep writing about.",
         "The kitchen was designed for cooking for a crowd: an 8-burner gas range with two ovens, two dishwashers, three sinks, a pot filler, a Vitamix and a long island with bar seating, plus a dining table that seats twelve. Everything you'd need for a holiday dinner is already in the drawers.",
         "Four bedrooms, each with its own private bathroom: a king in the master, with a walk-in closet, soaker tub, shower and bidet toilet, and queens in the other three. A fifth full bathroom is off the gym and there's a powder room for the main living space, so nobody is waiting in the hallway.",
         "The extras are what make it a smart home: Telus gigabit fibre internet, an 85-inch Samsung Frame TV with a Sonos Arc soundbar, Netflix and a Plex movie library, a quiet home office, a gym with free weights, a treadmill and a Tacx Neo smart bike set up for Zwift, air conditioning, a full laundry room and an exterior smart security system. The whole house runs on solar."],
        [("🍳", "Chef's kitchen", "8-burner gas range, 2 dishwashers, pot filler"), ("🏋️", "Home gym", "Weights, treadmill, Tacx Neo smart bike"), ("📺", "85&quot; Frame TV + Sonos", "Netflix &amp; Plex library"), ("☀️", "Solar-powered", "Air conditioning &amp; gigabit fibre")],
        [("/img/smart-home-chefs-kitchen-island.webp", "tall", "Chef's kitchen with island seating"), ("/img/smart-home-master-bedroom-with-king-bed.webp", "sq", "Master bedroom with king bed"), ("/img/smart-home-private-home-gym.webp", "sq", "Private home gym")])
    + rooms_section("Sleeping &amp; bathrooms", "Who Sleeps Where",
        [("🛏️", "Master bedroom", "King bed · ensuite with soaker tub, shower &amp; bidet · walk-in closet"), ("🛏️", "Bedroom 2", "Queen bed · private ensuite bathroom"), ("🛏️", "Bedroom 3", "Queen bed · private ensuite bathroom"), ("🛏️", "Bedroom 4", "Queen bed · private ensuite bathroom"), ("🚿", "Gym bathroom", "Fifth full bathroom, off the home gym"), ("🚽", "Powder room", "For the main living level · 5.5 baths in all")],
        "Four real beds for up to eight guests, and a bathroom for every bedroom. Need more room? The Suite next door sleeps six more.")
    + '''
<section class="location-section" style="padding:3.5rem 2rem">
  <div class="loc-grid" style="align-items:center">
    <div>
      <div class="eyebrow">Accessibility</div>
      <h2 class="section-title">Step-Free, With Honest Answers</h2>
      <div class="rule"></div>
      <div class="loc-body"><p>The Smart Home has step-free access and a guest entrance wider than 32 inches (81 cm), and the main living level — kitchen, dining, living room and patio — is on one floor. We would rather answer a specific question than let you guess: if you need details on bathroom layouts, bed heights, interior door widths or where each bedroom is, ask in your inquiry and we'll tell you exactly what to expect.</p></div>
    </div>
    <div>
      <ul class="dist-list">
        <li class="dist-item"><span>♿ &nbsp;Step-free access to the house</span><span class="dist-time">Yes</span></li>
        <li class="dist-item"><span>🚪 &nbsp;Guest entrance wider than 32&quot; (81 cm)</span><span class="dist-time">Yes</span></li>
        <li class="dist-item"><span>🅿️ &nbsp;Parking close to the entrance</span><span class="dist-time">Yes</span></li>
        <li class="dist-item"><span>🛁 &nbsp;Bathroom details, bed heights, door widths</span><span class="dist-time">Ask us</span></li>
      </ul>
    </div>
  </div>
</section>
'''
    + gallery_section(SMART_PHOTOS, SMART_TABS, "Photos", "Inside the Smart Home", "Tap any photo to view it full size. Use the tabs to jump to the kitchen, bedrooms, bathrooms or gym.")
    + amenities_section(SMART_AMENITIES)
    + rates_section("smarthome", "pricingGridSmarthome", "Rates", "Smart Home Rates &amp; Policies", "The Smart Home")
    + location_section("North Saanich, BC", "Where You Are", [
        "The farm sits on the Saanich Peninsula between Pat Bay and the airport. The beach is a short walk, Sidney's waterfront and shops are five minutes, the Swartz Bay ferry ten, Butchart Gardens fifteen and downtown Victoria about thirty-five.",
        "For a group arriving on different flights or ferries, nothing is easier: everyone is a few minutes from the airport and the terminal."])
    + quotes_section([
        ("The home is amazing — incredibly spacious, new and beautiful. The land it's on is gorgeous. By proximity, very close to the airport and ferry. This is one of our top Airbnb experiences.", "Kristen", "Tulsa, OK · July 2025"),
        ("It's a peaceful and idyllic property. Loved the deer, the chickens, the neighbours' cows and watching airplanes. The owners were so thoughtful in building their dream home and sharing it!", "Nancy", "Vancouver, BC · Aug 2025"),
        ("Beautiful home with amazing views! Pristine condition, we truly felt like we were on an amazing retreat! So peaceful and yet close to many things. Jessica was very helpful and responsive!", "Laura", "Omaha, NE · Nov 2025")],
        eyebrow="What guests say about the farm")
    + faq_section(SMART_FAQ, title="Smart Home Questions")
    + cta_band("Book the Smart Home Direct", "Tell us your dates and group size and we'll confirm availability and a quote within a few hours. A 50% deposit holds your booking; no platform fees.")
    + stays_section("suite")
    + guides_section("/group-vacation-rental-victoria/")
    + footer() + LIGHTBOX_HTML + MENU_JS + GALLERY_JS
)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: THINGS TO DO
# ═══════════════════════════════════════════════════════════════════════════
TTD_FAQ = [
    ("Do we need a car?", "It helps. Sidney is five minutes away, Butchart fifteen and Victoria thirty-five, and the best beaches and trails are spread around the peninsula. The airport's rental desks are three minutes from the farm, or ask us for a Turo link."),
    ("What's the closest beach?", "Pat Bay Beach, a two-minute walk from both rentals, on the Saanich Inlet side of the peninsula. It faces west, so the sunsets are the ones in our photos. Island View Beach and Coles Bay are short drives."),
    ("Can we do a Gulf Islands day trip?", "Yes. The Swartz Bay terminal is ten minutes away, with BC Ferries sailings to Salt Spring, the Penders, Galiano, Mayne and Saturna. Salt Spring's Saturday market in Ganges is the classic day out from April to October."),
    ("Is Butchart Gardens worth it outside summer?", "Yes. Spring bulbs, summer blooms and Saturday-night fireworks in July and August are the famous seasons, but the Christmas lights in December are a local tradition, and the quieter winter gardens are fifteen minutes from the farm."),
    ("What's there to do with kids?", "The beach, the Shaw Centre for the Salish Sea aquarium in Sidney, the BC Aviation Museum beside the airport, the Butterfly Gardens near Butchart, and watching the chickens, deer and eagles from the patio."),
]
def ttd_block(eyebrow, title, intro, items):
    lis = "".join(f'<li class="dist-item"><span>{n}</span><span class="dist-time">{d}</span></li>' for n, d in items)
    return f'''
    <div class="ttd-block">
      <div class="eyebrow">{eyebrow}</div>
      <h2 class="section-title" style="font-size:clamp(1.6rem,2.6vw,2.1rem)">{title}</h2>
      <div class="rule"></div>
      <p>{intro}</p>
      <ul class="dist-list ttd-list">{lis}</ul>
    </div>
'''
ttd = {
    "slug": "/things-to-do-sidney-north-saanich/",
    "title": "Things to Do in Sidney & North Saanich, BC | Farm Oasis Guide",
    "desc": "Local guide from our North Saanich farm: Pat Bay Beach, Sidney's waterfront, Butchart Gardens, John Dean Park, Sea Cider, whale watching and Gulf Islands trips.",
    "og": "/img/og/pat-bay-beach.jpg",
    "extra_css": '<style>.ttd-wrap{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:3rem 4rem}.ttd-block p{font-size:15px;color:var(--mid);line-height:1.8;margin:1rem 0 1.2rem}.ttd-list .dist-item{font-size:14.5px}.ttd-list a{color:var(--sage-dark)}@media(max-width:900px){.ttd-wrap{grid-template-columns:1fr}}</style>',
}
ttd["jsonld"] = {"@context": "https://schema.org", "@graph": [
    webpage_ld(ttd["slug"], ttd["title"], ttd["desc"], "/img/pat-bay-beach.webp", about=[{"@id": f"{BASE}/#suite"}, {"@id": f"{BASE}/#smarthome"}]),
    breadcrumb_ld(ttd["slug"], "Things to Do"),
    faq_ld(ttd["slug"], TTD_FAQ),
]}
ttd["body"] = (
    chrome_top("Things to Do Nearby")
    + hero("Sidney &nbsp;·&nbsp; North Saanich &nbsp;·&nbsp; Saanich Peninsula",
           "Things to Do <em>Around the Farm</em>",
           "Beaches you can walk to, a seaside town five minutes away, world-famous gardens at fifteen, and islands by ferry at ten. Here is how our guests actually spend their days.",
           btn1=("/#booking", "Check Dates &amp; Book Direct"), btn2=("/the-suite/", "See the Stays"))
    + '''
<section class="about-section" style="padding-bottom:3rem">
  <div class="ttd-wrap">
'''
    + ttd_block("On foot from the farm", "Pat Bay Beach &amp; the Fields",
        "You don't need the car for the first stop. Pat Bay Beach is a two-minute walk, facing west over the Saanich Inlet, which is why the sunsets look the way they do in our photos. Expect herons on the shoreline, eagles overhead and float planes landing at the airport across the bay.",
        [('<a href="https://www.google.com/maps/search/?api=1&amp;query=Patricia+Bay+Beach+North+Saanich+BC" target="_blank" rel="noopener">Pat Bay Beach</a> — sunsets, beachcombing, herons', "2 min walk"), ("Quiet farm roads for a morning walk or run", "Out the door"), ("Deer, eagles, chickens and the neighbours' cows", "From the patio")])
    + ttd_block("5 minutes", "Sidney-by-the-Sea",
        "Sidney is a walkable seaside town: Beacon Avenue runs from the highway down to the water, lined with cafés, restaurants, independent shops and more bookstores than a town this size has any right to. At the bottom is the pier, the waterfront walkway and the Shaw Centre's aquarium of the Salish Sea.",
        [('<a href="https://www.sidney.ca/" target="_blank" rel="noopener">Beacon Avenue</a> — cafés, restaurants, shops', "5 min drive"), ('<a href="https://salishseacentre.org/" target="_blank" rel="noopener">Shaw Centre for the Salish Sea</a> — aquarium', "5 min drive"), ("Sidney Pier &amp; waterfront walkway", "5 min drive"), ("Bookshops of Canada's &ldquo;Booktown&rdquo;", "5 min drive"), ("Sidney Street Market — summer Thursday evenings", "5 min drive"), ("Whale-watching tours from the Sidney waterfront", "5 min drive"), ("Sidney Spit (Gulf Islands National Park Reserve) by summer passenger ferry", "From the pier"), ('<a href="https://www.bcam.net/" target="_blank" rel="noopener">BC Aviation Museum</a> — beside the airport', "3 min drive")])
    + ttd_block("Parks &amp; trails", "Forest, Hilltops &amp; Shoreline",
        "The peninsula is small enough that you can hike an old-growth summit in the morning and be on a beach by lunch. John Dean Park (ȽÁU,WELṈEW̱) is the classic: Douglas fir, arbutus and a viewpoint over the Gulf Islands. For a long flat ride, the Lochside Regional Trail runs from near the ferry all the way into Victoria.",
        [('<a href="https://bcparks.ca/lau-welnew-john-dean-park/" target="_blank" rel="noopener">John Dean Provincial Park</a> — old-growth forest, summit views', "~5 min drive"), ("Horth Hill Regional Park — short hike, Gulf Islands views", "~8 min drive"), ("Coles Bay Regional Park — sheltered beach on the inlet", "~5 min drive"), ("Island View Beach — long sandy beach, Central Saanich", "~15 min drive"), ("Lochside Regional Trail — cycle to Victoria", "Nearby")])
    + ttd_block("Gardens, farms &amp; cider", "Butchart Gardens &amp; the Farm Country",
        "Butchart Gardens is fifteen minutes away in Brentwood Bay and worth it in every season: bulbs in spring, Saturday-night fireworks in July and August, Christmas lights in December. Around it, the peninsula is farm country — cideries, small wineries, farm stands, a Saturday farm market and the Saanich Fair on Labour Day weekend, one of the oldest agricultural fairs in Western Canada.",
        [('<a href="https://www.butchartgardens.com/" target="_blank" rel="noopener">Butchart Gardens</a>', "15 min drive"), ('<a href="https://www.butterflygardens.com/" target="_blank" rel="noopener">Victoria Butterfly Gardens</a> — near Butchart', "15 min drive"), ('<a href="https://seacider.ca/" target="_blank" rel="noopener">Sea Cider Farm &amp; Ciderhouse</a> — orchard tastings', "5 min drive"), ("Peninsula wineries &amp; farm stands", "5–15 min drive"), ("North Saanich Farm Market — summer Saturdays", "~5 min drive"), ("Saanich Fair — Labour Day weekend", "~10 min drive")])
    + ttd_block("By ferry", "Gulf Islands Day Trips",
        "The Swartz Bay terminal is ten minutes from the farm, which makes the Southern Gulf Islands day-trip territory. Salt Spring is the big one — the Saturday market in Ganges runs April to October — while the Penders, Galiano, Mayne and Saturna are quieter. Check sailing times before you go; some routes run only a few times a day.",
        [('<a href="https://www.bcferries.com/" target="_blank" rel="noopener">Swartz Bay ferry terminal</a>', "10 min drive"), ("Salt Spring Island — Ganges Saturday market", "By ferry"), ("Pender, Galiano, Mayne &amp; Saturna Islands", "By ferry"), ("Brentwood Bay–Mill Bay ferry — the scenic shortcut to the Cowichan Valley", "15 min drive")])
    + ttd_block("35 minutes", "Downtown Victoria",
        "Victoria is a comfortable day trip: the Inner Harbour, the Royal BC Museum, the Parliament Buildings, Fisherman's Wharf, Chinatown and Beacon Hill Park are all within a few blocks of each other. Go in for the day and come back to the farm for a quiet evening.",
        [('<a href="https://www.tourismvictoria.com/" target="_blank" rel="noopener">Inner Harbour &amp; downtown</a>', "~35 min drive"), ("Royal BC Museum &amp; Parliament Buildings", "~35 min drive"), ("Fisherman's Wharf — seafood, seals, float homes", "~35 min drive"), ("Beacon Hill Park &amp; Dallas Road waterfront", "~40 min drive"), ("Craigdarroch Castle", "~35 min drive")])
    + '''
  </div>
</section>
'''
    + '''
<section class="location-section">
  <div class="loc-grid">
    <div>
      <div class="eyebrow">Season by season</div>
      <h2 class="section-title">When to Come</h2>
      <div class="rule"></div>
      <div class="loc-body">
        <p><strong style="color:white">Spring (March–May):</strong> cherry blossoms, Butchart's bulbs, the first markets, and the calmest water for whale watching as the season opens.</p>
        <p><strong style="color:white">Summer (June–September):</strong> long evenings on the patio, Sidney's Thursday street market, Butchart fireworks, Sidney Spit, Gulf Islands ferries and the Saanich Fair on Labour Day weekend.</p>
        <p><strong style="color:white">Autumn (October–November):</strong> apple harvest at the cideries, quiet trails, storm-watching light over the inlet.</p>
        <p><strong style="color:white">Winter (December–February):</strong> Butchart's Christmas lights, mild temperatures by Canadian standards, and the best rates of the year.</p>
      </div>
    </div>
    <div>''' + LOC_LIST + '''</div>
  </div>
</section>
'''
    + stays_section("suite")
    + faq_section(TTD_FAQ, title="Planning Questions")
    + cta_band("Make the Farm Your Base", "Two rentals, one farm, everything above within a short drive. Send us your dates and we'll confirm availability within a few hours.")
    + guides_section(ttd["slug"])
    + footer() + MENU_JS
)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: MONTHLY STAYS
# ═══════════════════════════════════════════════════════════════════════════
MONTHLY_FAQ = [
    ("What is the minimum stay for the monthly rate?", "The monthly rate applies from 28–30 nights depending on the home (the exact minimum is shown on the rate cards). Stays of 7+ and 14+ nights are discounted too."),
    ("What's included in a monthly stay?", "Everything a nightly guest gets: furniture, linens and towels, a fully equipped kitchen, washer and dryer, high-speed internet, utilities, parking and the patio. The Smart Home also has a dedicated home office and gigabit fibre."),
    ("Is there a cleaning fee on long stays?", "One cleaning fee per stay. If you'd like mid-stay cleaning, ask and we'll quote it."),
    ("Can I stay longer than a month?", "Usually, yes. Tell us your dates in the inquiry and we'll confirm availability and a quote for the full period."),
    ("Is it close to the hospital and the airport?", "Saanich Peninsula Hospital in Saanichton is about 10 minutes, Victoria Airport is 3 minutes, and Victoria General Hospital is roughly 25 minutes."),
    ("Are pets allowed on long stays?", "No. Both rentals are pet-free and smoke- and vape-free for every length of stay."),
]
monthly = {
    "slug": "/monthly-stays-sidney-north-saanich/",
    "title": "Monthly Furnished Rentals near Sidney, BC | Farm Oasis",
    "desc": "Furnished monthly stays near Sidney, BC, 3 min from Victoria Airport: a 2BR + loft suite or a 4BR smart home with office and gym. Discounted 28–30+ night rates.",
    "og": "/img/og/suite-living-area.jpg",
}
monthly["jsonld"] = {"@context": "https://schema.org", "@graph": [
    webpage_ld(monthly["slug"], monthly["title"], monthly["desc"], "/img/suite-living-area.webp", about=[{"@id": f"{BASE}/#suite"}, {"@id": f"{BASE}/#smarthome"}]),
    breadcrumb_ld(monthly["slug"], "Monthly Stays"),
    faq_ld(monthly["slug"], MONTHLY_FAQ),
]}
monthly["body"] = (
    chrome_top("Monthly &amp; Extended Stays")
    + hero("Furnished &nbsp;·&nbsp; 28–30+ nights &nbsp;·&nbsp; North Saanich, BC",
           "Monthly Stays: <em>Furnished, Equipped</em>, Minutes from the Airport",
           "Move in with a suitcase. Both rentals come fully furnished with linens, a real kitchen, laundry, fast internet and farm views, at a flat monthly rate well below the nightly price. Five minutes from Sidney, three from YYJ.",
           btn2=("#monthly-rates", "See Monthly Rates"))
    + about_section("Who stays a month", "Somewhere to Land for a While",
        ["Monthly guests come to us for all the ordinary reasons a month somewhere takes: relocating to the Saanich Peninsula or Victoria and house-hunting from a comfortable base; a renovation or insurance claim that has put the family out of the house; visiting professionals and crews working at the airport, the marine-science and aviation employers around it, or the hospital in Saanichton; family visiting for a new baby or a long recovery; and winter escapes from colder parts of the country.",
         "What you get is a home rather than a hotel room. The Suite has two bedrooms with their own bathrooms plus a loft, a full kitchen, in-suite laundry and a patio. The Smart Home has four bedrooms with four private bathrooms, a kitchen that seats twelve, a home office, a gym and gigabit fibre — enough room for a family or a crew to work and live without getting in each other's way.",
         "Both are self check-in, with parking at the door, and you are on a quiet farm road with a beach at the end of it. Sidney's grocery stores, pharmacies, cafés and the waterfront are five minutes away."],
        [("📶", "Fast internet", "Gigabit fibre in the Smart Home"), ("🧺", "Laundry in-suite", "Washer &amp; dryer in both rentals"), ("💡", "Utilities included", "Heat, power, water, WiFi"), ("🏥", "Hospital 10 min", "Saanich Peninsula Hospital")],
        [("/img/suite-living-and-dining-area.webp", "tall", "Suite living and dining area"), ("/img/smart-home-home-office.webp", "sq", "Home office in the Smart Home"), ("/img/suite-laundry-area.webp", "sq", "In-suite laundry")])
    + '''
<section id="monthly-rates" class="pricing-section">
  <div class="wrap">
    <div class="eyebrow">Monthly rates</div>
    <h2 class="section-title">What a Month Costs</h2>
    <div class="rule"></div>
    <p class="pricing-intro">The monthly rate is a flat amount for the first <span data-monthly-nights="suite"></span> nights plus one cleaning fee — a long way below the nightly price, and below our Airbnb monthly pricing too. Because you book direct there are no platform fees on top.</p>
    <div class="rules-grid" style="margin-top:1.5rem">
      <div class="rule-card rule-ok" data-prop="suite"><span class="rule-icon">🏡</span><div class="rule-name">The Suite · 2BR + loft</div><div class="rule-note"><strong data-monthly-total="suite"></strong> for <span data-monthly-nights="suite"></span> nights · about <span data-monthly-night="suite"></span>/night · from <span data-monthly-min="suite"></span> nights · + <span data-cleaning-fee="suite"></span> cleaning</div><p class="prop-note" hidden></p></div>
      <div class="rule-card rule-ok" data-prop="smarthome"><span class="rule-icon">🏠</span><div class="rule-name">The Smart Home · 4BR</div><div class="rule-note"><strong data-monthly-total="smarthome"></strong> for <span data-monthly-nights="smarthome"></span> nights · about <span data-monthly-night="smarthome"></span>/night · from <span data-monthly-min="smarthome"></span> nights · + <span data-cleaning-fee="smarthome"></span> cleaning</div><p class="prop-note" hidden></p></div>
      <div class="rule-card rule-ok"><span class="rule-icon">📅</span><div class="rule-name">Shorter long stays</div><div class="rule-note"><span data-ladder="suite"></span> — applied automatically on the booking form</div></div>
    </div>
    <p style="font-size:13.5px;color:var(--mid);margin-top:1.25rem;max-width:760px">Prices in Canadian dollars. Your quote confirms the total for your exact dates. Self-catering; no pets, smoking or vaping.</p>
  </div>
</section>
'''
    + location_section("North Saanich, BC", "Daily Life Nearby", [
        "Groceries, pharmacies, banks and the post office are in Sidney, five minutes away, along with the waterfront walkway for an evening stroll. The airport is three minutes, the Swartz Bay ferry ten, and downtown Victoria about thirty-five by car.",
        "Working from here is easy: the Smart Home has a dedicated office and gigabit fibre, and the Suite has a dining table with a view and fast WiFi."])
    + stays_section("suite")
    + faq_section(MONTHLY_FAQ, title="Monthly Stay Questions")
    + cta_band("Ask About a Monthly Stay", "Send your dates and which rental you have in mind. We'll confirm availability and send a full quote within a few hours.", "Send a Monthly Stay Inquiry")
    + guides_section(monthly["slug"])
    + footer() + MENU_JS
)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: BOOK DIRECT
# ═══════════════════════════════════════════════════════════════════════════
BD_FAQ = [
    ("Is it safe to book direct?", "You're booking with the same hosts and the same two homes you'll find on Airbnb, where we're a Superhost with more than 80 five-star reviews. The Suite is registered with the Province of BC (registration H295535660). We confirm everything in writing before any deposit is paid."),
    ("Is it really cheaper than Airbnb?", "Yes. Our direct rates are set below our Airbnb pricing, there's no platform guest fee on top, and longer stays are discounted further than anywhere else we list."),
    ("How do I pay?", "By Interac e-Transfer from a Canadian bank account: a 50% deposit holds your dates and we confirm the balance due date in your quote. Travelling from the US or overseas? Say so in your inquiry and we'll let you know your options."),
    ("What does the quote include?", "The nightly rate for your dates, any long-stay discount, and the one-time cleaning fee. We'll spell out the total in writing so there are no surprises."),
    ("What is the cancellation policy?", "Moderate: a full refund if you cancel at least 5 days before check-in, and a partial refund inside 5 days."),
    ("How quickly will I hear back?", "Usually within a few hours during the day, and always within 24 hours."),
    ("Can I check availability first?", "Yes. The calendar on the home page syncs from our booking calendars every few hours. If your dates show as free, send the inquiry and we'll confirm them."),
]
bookdirect = {
    "slug": "/book-direct/",
    "title": "Book Direct & Save — How Direct Booking Works | Farm Oasis, Sidney BC",
    "desc": "Book the Suite or the Smart Home directly with the hosts: no platform fees, a written quote within hours, a 50% deposit holds your dates, moderate cancellation.",
    "og": "/img/og/pat-bay-beach-sunset.jpg",
    "extra_css": '<style>.steps{max-width:960px;margin:2rem auto 0;display:grid;grid-template-columns:repeat(4,1fr);gap:1.25rem}.step{background:var(--white);border:1px solid var(--border-light);border-radius:10px;padding:1.5rem}.step-n{font-family:var(--serif);font-size:2rem;color:var(--sage);line-height:1}.step h3{font-family:var(--serif);font-weight:500;font-size:1.25rem;margin:0.5rem 0 0.4rem;color:var(--charcoal)}.step p{font-size:14px;color:var(--mid);line-height:1.7}@media(max-width:900px){.steps{grid-template-columns:1fr 1fr}}@media(max-width:520px){.steps{grid-template-columns:1fr}}</style>',
}
bookdirect["jsonld"] = {"@context": "https://schema.org", "@graph": [
    webpage_ld(bookdirect["slug"], bookdirect["title"], bookdirect["desc"], "/img/pat-bay-beach-sunset.webp", about=[{"@id": f"{BASE}/#suite"}, {"@id": f"{BASE}/#smarthome"}]),
    breadcrumb_ld(bookdirect["slug"], "Book Direct"),
    faq_ld(bookdirect["slug"], BD_FAQ),
]}
bookdirect["body"] = (
    chrome_top("Why Book Direct")
    + hero("Lowest rates &nbsp;·&nbsp; no platform fees &nbsp;·&nbsp; the same hosts",
           "Book Direct: <em>Same Homes, Lower Price</em>",
           "Our direct rates are set below our Airbnb pricing, nothing is added on top, and the longer you stay the less each night costs. You deal with the hosts, you get a written quote, and your deposit holds the dates.",
           btn1=("/#booking", "Send a Booking Inquiry"), btn2=("/#availability", "Check Availability"))
    + '''
<section class="about-section" style="padding-bottom:3rem">
  <div class="wrap">
    <div class="eyebrow" style="text-align:center">Four steps</div>
    <h2 class="section-title" style="text-align:center">How a Direct Booking Works</h2>
    <div class="rule" style="margin-left:auto;margin-right:auto"></div>
    <div class="steps">
      <div class="step"><div class="step-n">1</div><h3>Send your dates</h3><p>Use the <a href="/#booking" style="color:var(--sage-dark)">inquiry form</a>: pick the Suite or the Smart Home, your check-in and check-out, and how many guests. The form shows a price estimate instantly, discounts included.</p></div>
      <div class="step"><div class="step-n">2</div><h3>We confirm and quote</h3><p>We check the calendar and reply, usually within a few hours, with your confirmed dates and a written total: nightly rate, any long-stay discount, and the cleaning fee.</p></div>
      <div class="step"><div class="step-n">3</div><h3>Deposit holds the dates</h3><p>A 50% deposit by Interac e-Transfer secures the booking. We confirm the balance due date in the quote. Outside Canada? Tell us and we'll explain your options.</p></div>
      <div class="step"><div class="step-n">4</div><h3>Arrival details</h3><p>Before your stay we send directions, the self check-in details and our phone number. Check-in is from 3:00 PM, check-out 10:00 AM.</p></div>
    </div>
  </div>
</section>
'''
    + '''
<section class="location-section">
  <div class="loc-grid">
    <div>
      <div class="eyebrow">What you pay</div>
      <h2 class="section-title">Where the Saving Comes From</h2>
      <div class="rule"></div>
      <div class="loc-body">
        <p>Platforms charge guests a service fee on top of the host's price — typically around 14% of the subtotal — and charge the host another fee on their side. When you book direct, neither applies, and we pass that on: our direct nightly rates are set below our Airbnb pricing to begin with.</p>
        <p id="bdExample"></p>
        <p>Longer stays cost less per night — <span data-ladder="suite"></span>, and a flat monthly rate for the longest stays. Prices are in Canadian dollars; your written quote is the number you'll pay.</p>
      </div>
    </div>
    <div>
      <ul class="dist-list">
        <li class="dist-item"><span>✓ &nbsp;Nightly rate for your dates</span><span class="dist-time">Below Airbnb</span></li>
        <li class="dist-item"><span>✓ &nbsp;Long-stay discounts</span><span class="dist-time">Automatic</span></li>
        <li class="dist-item"><span>✓ &nbsp;One cleaning fee per stay</span><span class="dist-time" id="bdClean"></span></li>
        <li class="dist-item"><span>✗ &nbsp;Platform guest service fee</span><span class="dist-time">None</span></li>
        <li class="dist-item"><span>✗ &nbsp;Hidden extras</span><span class="dist-time">None</span></li>
      </ul>
    </div>
  </div>
</section>
<script>
(function(){
  if(!window.Pricing)return;
  var c=Pricing.cfg('suite'), t=new Date();
  function iso(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
  var e=new Date(t);e.setDate(t.getDate()+3);
  var q=Pricing.quote('suite',iso(t),iso(e));
  if(q){
    var fee=Math.round(q.total*0.14);
    document.getElementById('bdExample').innerHTML='For example, '+q.nights+' nights in the Suite this month at '+fmtMoney(q.avgNightly)+' a night is '+fmtMoney(q.subtotal)+' plus the '+fmtMoney(q.cleaning)+' cleaning fee: <strong style="color:white">'+fmtMoney(q.total)+' direct</strong>. A platform guest fee of around 14% alone would add roughly '+fmtMoney(fee)+' to a stay like that.';
  }
  document.getElementById('bdClean').textContent=fmtMoney(c.cleaningFee||0)+' / '+fmtMoney((Pricing.cfg('smarthome')||{}).cleaningFee||0);
})();
</script>
'''
    + '''
<section class="pricing-section" style="padding-top:4rem;padding-bottom:4rem">
  <div class="wrap">
    <div class="eyebrow">Policies</div>
    <h2 class="section-title">The Small Print, Kept Small</h2>
    <div class="rule"></div>
    <div class="rules-grid" style="margin-top:1.5rem">
      <div class="rule-card rule-ok"><span class="rule-icon">✓</span><div class="rule-name">Moderate cancellation</div><div class="rule-note">Full refund 5+ days before check-in; partial inside 5 days</div></div>
      <div class="rule-card rule-ok"><span class="rule-icon">✓</span><div class="rule-name">50% deposit</div><div class="rule-note">Holds your dates; balance due date in your quote</div></div>
      <div class="rule-card rule-ok"><span class="rule-icon">✓</span><div class="rule-name">Self check-in</div><div class="rule-note">From 3:00 PM · check-out 10:00 AM</div></div>
      <div class="rule-card rule-ok"><span class="rule-icon">✓</span><div class="rule-name">Self-catering</div><div class="rule-note">Full kitchens · breakfast not served</div></div>
      <div class="rule-card rule-no"><span class="rule-icon">✗</span><div class="rule-name">No pets</div><div class="rule-note">In either rental</div></div>
      <div class="rule-card rule-no"><span class="rule-icon">✗</span><div class="rule-name">No smoking or vaping</div><div class="rule-note">Indoors or on the property</div></div>
      <div class="rule-card rule-no"><span class="rule-icon">✗</span><div class="rule-name">No parties or events</div><div class="rule-note">Family dinners welcome</div></div>
    </div>
  </div>
</section>
'''
    + quotes_section([
        ("Jessica was an exceptional host, and the property was absolutely stunning. Meticulously equipped and designed for incredible comfort. We will undoubtedly return. Thank you, Jessica and Ryan!", "Sachin", "Mumbai, India · Mar 2025"),
        ("Absolutely beautiful location, with a home to match. Jessica was great to work with and reached out to make sure things were going smoothly. Will definitely stay here again.", "Jared", "Kaysville, UT · Apr 2025"),
        ("This property was exceptionally beautiful and comfortable. We loved waking up to the chickens and a family of deer on the horizon. 100% would stay here again if visiting the islands.", "Haley", "Boston, MA · Apr 2025")],
        eyebrow="The hosts you're booking with")
    + stays_section("suite")
    + faq_section(BD_FAQ, title="Direct Booking Questions")
    + cta_band("Ready When You Are", "Send your dates and we'll confirm availability and a written quote within a few hours.", "Send a Booking Inquiry")
    + guides_section(bookdirect["slug"])
    + footer() + MENU_JS
)

# ═══════════════════════════════════════════════════════════════════════════
PAGES = [suite, smart, ttd, monthly, bookdirect]
if __name__ == "__main__":
    for p in PAGES:
        out_dir = os.path.join(REPO, p["slug"].strip("/"))
        os.makedirs(out_dir, exist_ok=True)
        html_out = head(p) + p["body"] + "</body>\n</html>\n"
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(html_out)
        print("wrote", p["slug"], len(html_out), "bytes")
