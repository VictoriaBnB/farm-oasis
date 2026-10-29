"""Keeps the parts of the site that crawlers read without JavaScript in sync
with assets/site-config.js. Run after changing the config (Site Manager does
this for you):

    python tools/render_static.py

Currently updates:
  - index.html  -> JSON-LD priceRange for both properties, "updated" date
Also validates the config and exits non-zero with a readable message if
something is wrong (bad date, missing number, unknown status).
"""
import json, os, re, sys, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(REPO, "assets", "site-config.js")
INDEX = os.path.join(REPO, "index.html")
STATUSES = ("open", "paused", "hidden")


def load_config():
    text = open(CONFIG, encoding="utf-8").read()
    m = re.search(r"(?:var|const|let) SITE_CONFIG = (\{.*\});\s*$", text, re.S)
    if not m:
        raise SystemExit("site-config.js: could not find 'var SITE_CONFIG = {...};'")
    try:
        cfg = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit(f"site-config.js is not valid JSON inside SITE_CONFIG: {e}")
    return cfg, text[: m.start(1)], text[m.end(1):]


def save_config(cfg, head, tail):
    cfg["updated"] = datetime.date.today().isoformat()
    body = json.dumps(cfg, indent=2, ensure_ascii=False)
    with open(CONFIG, "w", encoding="utf-8", newline="\n") as f:
        f.write(head + body + tail)


def validate(cfg):
    errs = []
    for prop, p in (cfg.get("properties") or {}).items():
        if p.get("status") not in STATUSES:
            errs.append(f"{prop}: status must be one of {STATUSES}, got {p.get('status')!r}")
    pricing = cfg.get("pricing") or {}
    for prop in ("suite", "smarthome"):
        c = pricing.get(prop)
        if not isinstance(c, dict):
            errs.append(f"pricing.{prop} missing"); continue
        for k in ("cleaningFee", "maxGuests", "defaultNightly"):
            if not isinstance(c.get(k), (int, float)) or c.get(k) < 0:
                errs.append(f"pricing.{prop}.{k} must be a number")
        for s in c.get("seasons") or []:
            for k in ("from", "to"):
                v = str(s.get(k, ""))
                if not re.fullmatch(r"(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])", v):
                    errs.append(f"pricing.{prop} season {s.get('name')!r}: {k} must be MM-DD, got {v!r}")
            if not isinstance(s.get("nightly"), (int, float)) or s.get("nightly") <= 0:
                errs.append(f"pricing.{prop} season {s.get('name')!r}: nightly must be a positive number")
        for d in c.get("discounts") or []:
            if not isinstance(d.get("minNights"), int) or d["minNights"] < 2:
                errs.append(f"pricing.{prop} discount: minNights must be a whole number of 2 or more")
            if not isinstance(d.get("pct"), (int, float)) or not (0 < d["pct"] < 100):
                errs.append(f"pricing.{prop} discount: pct must be between 0 and 100")
        m = c.get("monthly")
        if m:
            for k in ("minNights", "perNights", "total"):
                if not isinstance(m.get(k), (int, float)) or m.get(k) <= 0:
                    errs.append(f"pricing.{prop}.monthly.{k} must be a positive number")
    return errs


def price_range(c):
    rates = [s["nightly"] for s in c.get("seasons") or []]
    if c.get("defaultNightly"):
        rates.append(c["defaultNightly"])
    low = min(rates) if rates else 0
    high = max(rates) if rates else 0
    m = c.get("monthly")
    if m:
        low = min(low, m["total"] / m["perNights"])
    return f"${round(low)}–${round(high)} CAD/night"


def render_index(cfg):
    raw = open(INDEX, "rb").read()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    m = re.search(r'(<script type="application/ld\+json" id="schemaJsonLd">\n)(.*?)(\n</script>)', t, re.S)
    if not m:
        raise SystemExit("index.html: schemaJsonLd block not found")
    ld = json.loads(m.group(2))
    changed = []
    for ent in ld.get("@graph", []):
        key = {"LodgingBusiness": "suite", "House": "smarthome"}.get(ent.get("@type"))
        if key and key in cfg["pricing"]:
            new = price_range(cfg["pricing"][key])
            if ent.get("priceRange") != new:
                ent["priceRange"] = new
                changed.append(f"{key}: priceRange -> {new}")
    t = t[: m.start(2)] + json.dumps(ld, indent=2, ensure_ascii=False) + t[m.end(2):]
    with open(INDEX, "w", encoding="utf-8", newline="\r\n" if crlf else "\n") as f:
        f.write(t)
    return changed


def main():
    cfg, head, tail = load_config()
    errs = validate(cfg)
    if errs:
        print("Config problems:\n  - " + "\n  - ".join(errs))
        sys.exit(1)
    save_config(cfg, head, tail)
    changed = render_index(cfg)
    print("config OK; index.html " + ("updated: " + "; ".join(changed) if changed else "already in sync"))


if __name__ == "__main__":
    main()
