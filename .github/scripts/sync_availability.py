#!/usr/bin/env python3
"""Pull booked dates from calendar links (iCal) and write availability.json.

The links are secret (anyone with them can read the calendar), so they come from
GitHub repository secrets, never from this file:
  AIRBNB_ICAL_SUITE      -> The Suite (2BR + loft)
  AIRBNB_ICAL_SMARTHOME  -> The Smart Home (4BR)
Each secret may hold SEVERAL links, one per line (or separated by spaces), e.g. the
Airbnb export link AND the Google Calendar "secret address in iCal format" used for
direct bookings. A night is shown as booked if it is booked in ANY of the links.

Output (public, dates only):
  {"updated": "...", "suite": {"connected": true, "busy": [["2026-10-12","2026-10-15"], ...]}, ...}
Each busy range is [check-in, check-out): the check-out day itself is free.
If a feed can't be fetched, that listing's previous data is kept rather than wiped.
"""
import json, os, re, sys, urllib.request
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

OUT = sys.argv[1] if len(sys.argv) > 1 else "availability.json"
FEEDS = {"suite": "AIRBNB_ICAL_SUITE", "smarthome": "AIRBNB_ICAL_SMARTHOME"}

def load_previous():
    try:
        with open(OUT, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

LOCAL = ZoneInfo("America/Vancouver")

def parse_date(value):
    """All-day dates (Airbnb) stay as-is; UTC times (Google timed events) become the local date."""
    m = re.match(r"(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})(Z?))?", value.strip())
    if not m:
        return None
    if m[4] and m[7] == "Z":
        dt = datetime(int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6]), tzinfo=timezone.utc)
        return dt.astimezone(LOCAL).date()
    return date(int(m[1]), int(m[2]), int(m[3]))

def fetch_busy(url):
    req = urllib.request.Request(url, headers={"User-Agent": "victoriabnb.ca availability sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        text = r.read().decode("utf-8", "replace")
    if "BEGIN:VCALENDAR" not in text:
        raise ValueError("response is not an iCal calendar")
    text = re.sub(r"\r?\n[ \t]", "", text)  # unfold folded lines
    today, ranges = date.today(), []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, re.S):
        start = end = None
        for line in block.splitlines():
            key, _, val = line.partition(":")
            if key.startswith("DTSTART"):
                start = parse_date(val)
            elif key.startswith("DTEND"):
                end = parse_date(val)
        if start and end and end > start and end > today:
            ranges.append([start.isoformat(), end.isoformat()])
    ranges.sort()
    merged = []
    for s, e in ranges:  # merge back-to-back / overlapping blocks
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged

prev = load_previous()
out, problems = {}, []
for key, env in FEEDS.items():
    urls = [u for u in re.split(r"[\s,]+", os.environ.get(env, "")) if u.startswith("http")]
    if not urls:
        out[key] = {"connected": False, "busy": []}
        continue
    ranges, failed = [], 0
    for n, url in enumerate(urls, 1):
        try:
            ranges += fetch_busy(url)
        except Exception as e:
            failed += 1
            problems.append(f"{key} link {n}: {e}")
    if failed:  # keep last good data rather than showing booked nights as free
        out[key] = prev.get(key) or {"connected": False, "busy": []}
        continue
    ranges.sort()
    merged = []
    for s_, e_ in ranges:
        if merged and s_ <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e_)
        else:
            merged.append([s_, e_])
    out[key] = {"connected": True, "busy": merged}

changed = {k: prev.get(k) for k in FEEDS} != out
out["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if changed else prev.get("updated")
if changed or not os.path.exists(OUT):
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"updated": out["updated"], "suite": out["suite"], "smarthome": out["smarthome"]}, f, indent=1)
        f.write("\n")
print("changed" if changed else "no change", "|", {k: len(out[k]["busy"]) for k in FEEDS}, "booked ranges")
for p in problems:
    print("WARNING", p)
configured = [k for k, v in FEEDS.items() if os.environ.get(v, "").strip()]
problems_by_key = {k for k in FEEDS if any(p.startswith(k + " ") for p in problems)}
if configured and problems_by_key >= set(configured):
    sys.exit(1)  # every configured feed failed: make the run show red in GitHub
