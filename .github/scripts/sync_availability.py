#!/usr/bin/env python3
"""Pull booked dates from the Airbnb iCal export links and write availability.json.

The links are secret (anyone with them can read the calendar), so they come from
GitHub repository secrets, never from this file:
  AIRBNB_ICAL_SUITE      -> The Suite (2BR + loft)
  AIRBNB_ICAL_SMARTHOME  -> The Smart Home (4BR)

Output (public, dates only):
  {"updated": "...", "suite": {"connected": true, "busy": [["2026-10-12","2026-10-15"], ...]}, ...}
Each busy range is [check-in, check-out): the check-out day itself is free.
If a feed can't be fetched, that listing's previous data is kept rather than wiped.
"""
import json, os, re, sys, urllib.request
from datetime import date, datetime, timezone

OUT = sys.argv[1] if len(sys.argv) > 1 else "availability.json"
FEEDS = {"suite": "AIRBNB_ICAL_SUITE", "smarthome": "AIRBNB_ICAL_SMARTHOME"}

def load_previous():
    try:
        with open(OUT, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def parse_date(value):
    m = re.match(r"(\d{4})(\d{2})(\d{2})", value)
    return date(int(m[1]), int(m[2]), int(m[3])) if m else None

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
        if start and end and end > today:
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
    url = os.environ.get(env, "").strip()
    if not url:
        out[key] = {"connected": False, "busy": []}
        continue
    try:
        out[key] = {"connected": True, "busy": fetch_busy(url)}
    except Exception as e:
        problems.append(f"{key}: {e}")
        out[key] = prev.get(key) or {"connected": False, "busy": []}

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
if configured and len(problems) == len(configured):
    sys.exit(1)  # every configured feed failed: make the run show red in GitHub
