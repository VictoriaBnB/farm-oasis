"""Headless-Chrome screenshots + page checks over the DevTools protocol.

    python tools/shot.py                      # every page, desktop + mobile
    python tools/shot.py / /the-suite/        # just these paths
    python tools/shot.py / --clip .hero "#location"   # just these elements (desktop; add --only mobile)
    python tools/shot.py / --only mobile      # one viewport only

Serves the repo on http://127.0.0.1:PORT with Python's http.server, drives
Chrome headless through the DevTools protocol, and for each page writes
    tools/shots/<slug>-desktop.png   (1440 wide, full page)
    tools/shots/<slug>-mobile.png    (390 wide @2x, full page)
and prints a report: console errors, uncaught exceptions, failed requests,
horizontal overflow, broken images, images without alt, empty "from" prices.
Exit status is 1 if any page had a problem. Needs: Chrome (or Edge) and
`pip install websocket-client`.
"""
import argparse, base64, json, os, re, subprocess, sys, tempfile, time, urllib.request

try:
    import websocket
except ImportError:
    raise SystemExit("pip install websocket-client")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "tools", "shots")
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
PAGES = ["/", "/the-suite/", "/the-smart-home/", "/things-to-do-sidney-north-saanich/",
         "/monthly-stays-sidney-north-saanich/", "/book-direct/",
         "/sidney-north-saanich-vacation-rental/", "/swartz-bay-ferry-stay/", "/farmhouse-stay-victoria-bc/",
         "/victoria-airport-accommodation/", "/butchart-gardens-accommodation/", "/group-vacation-rental-victoria/",
         "/404.html"]
VIEWPORTS = {"desktop": dict(width=1440, height=900, deviceScaleFactor=1, mobile=False),
             "mobile": dict(width=390, height=844, deviceScaleFactor=2, mobile=True)}
MAX_PIXELS_TALL = 16000  # Chrome's texture limit


def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("Chrome/Edge not found; edit CHROME_CANDIDATES in tools/shot.py")


class CDP:
    """Minimal DevTools client: send(method, params) -> result; events are buffered in .events."""

    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=30)
        self.n = 0
        self.events = []

    def send(self, method, params=None):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError("%s: %s" % (method, msg["error"]))
                return msg.get("result", {})
            if "method" in msg:
                self.events.append(msg)

    def pump(self, seconds):
        """Collect events for a while (lets the page settle)."""
        end = time.time() + seconds
        self.ws.settimeout(0.25)
        try:
            while time.time() < end:
                try:
                    msg = json.loads(self.ws.recv())
                    if "method" in msg:
                        self.events.append(msg)
                except websocket.WebSocketTimeoutException:
                    pass
        finally:
            self.ws.settimeout(30)

    def wait_event(self, name, timeout=20):
        for e in self.events:
            if e["method"] == name:
                return e
        end = time.time() + timeout
        self.ws.settimeout(1)
        try:
            while time.time() < end:
                try:
                    msg = json.loads(self.ws.recv())
                except websocket.WebSocketTimeoutException:
                    continue
                if "method" in msg:
                    self.events.append(msg)
                    if msg["method"] == name:
                        return msg
        finally:
            self.ws.settimeout(30)
        return None

    def eval(self, expr, await_promise=False):
        r = self.send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": await_promise})
        if "exceptionDetails" in r:
            raise RuntimeError(r["exceptionDetails"].get("text", "evaluate failed"))
        return r.get("result", {}).get("value")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


CHECK_JS = r"""
(() => {
  const imgs = [...document.images];
  const vis = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const cw = document.documentElement.clientWidth;
  const tag = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') +
    (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : '');
  return {
    title: document.title,
    height: document.documentElement.scrollHeight,
    sections: [...document.querySelectorAll('section[id], .hero, .tiles-section, .cta-band, footer')]
      .map(e => (e.id || e.className.split(' ')[0]) + '@' + Math.round(e.getBoundingClientRect().top + window.scrollY)),
    overflowX: document.documentElement.scrollWidth - cw,
    brokenImages: imgs.filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src')).map(i => i.getAttribute('src')).slice(0, 10),
    noAlt: imgs.filter(i => !i.hasAttribute('alt')).map(i => i.getAttribute('src')).slice(0, 10),
    emptyFromPrices: [...document.querySelectorAll('[data-from-price]')].filter(e => vis(e) && !e.textContent.trim()).length,
    wideElements: [...document.querySelectorAll('body *')]
      .filter(e => { const r = e.getBoundingClientRect(); return r.right > cw + 1 && r.width > 40; })
      .slice(0, 6).map(e => tag(e) + '@' + Math.round(e.getBoundingClientRect().right)),
  };
})()
"""

SCROLL_JS = r"""
new Promise(res => {
  const h = document.documentElement.scrollHeight; let y = 0;
  const step = () => { y += 700; window.scrollTo(0, y);
    if (y < h) setTimeout(step, 60); else { window.scrollTo(0, 0); setTimeout(res, 300); } };
  step();
})
"""

FONTS_JS = "document.fonts ? document.fonts.ready.then(() => 1) : 1"


def wait_http(url, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                return r.read()
        except Exception:
            time.sleep(0.2)
    raise SystemExit("timed out waiting for " + url)


def new_target(dbg_port):
    req = urllib.request.Request("http://127.0.0.1:%d/json/new?about:blank" % dbg_port, method="PUT")
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


def close_target(dbg_port, target_id):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/close/%s" % (dbg_port, target_id), timeout=5).read()
    except Exception:
        pass


def clip_box_js(selector):
    return ("(() => { const e = document.querySelector(%s); if (!e) return null;"
            " const r = e.getBoundingClientRect();"
            " return {x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: r.height}; })()"
            % json.dumps(selector))


def shoot(dbg_port, base, path, viewport, out_png, clip_sel=None, settle=2.0, no_scroll=False, debug_urls=None):
    """Capture one page in one viewport; returns the check report (dict)."""
    t = new_target(dbg_port)
    cdp = CDP(t["webSocketDebuggerUrl"])
    problems = {"console": [], "exceptions": [], "failedRequests": []}
    try:
        for d in ("Page", "Runtime", "Log", "Network"):
            cdp.send(d + ".enable")
        vp = dict(VIEWPORTS[viewport])
        cdp.send("Emulation.setDeviceMetricsOverride", vp)
        if vp["mobile"]:
            cdp.send("Emulation.setTouchEmulationEnabled", {"enabled": True})
        cdp.send("Page.navigate", {"url": base + path})
        cdp.wait_event("Page.loadEventFired", 30)
        if not no_scroll:
            cdp.eval(SCROLL_JS, await_promise=True)   # trigger lazy images
        cdp.pump(settle)                           # fonts, hero animation, iframes
        cdp.eval(FONTS_JS, await_promise=True)
        dsf = vp["deviceScaleFactor"]
        # grow the viewport to the whole document first, so every lazy image is in view before the checks
        h0 = cdp.eval("document.documentElement.scrollHeight")
        cdp.send("Emulation.setDeviceMetricsOverride", dict(vp, height=min(int(h0), MAX_PIXELS_TALL // dsf)))
        cdp.eval("window.scrollTo(0,0)")
        cdp.pump(1.0)
        info = cdp.eval(CHECK_JS)

        NOISE = ("cloudflareinsights", "static.cloudflareinsights.com")
        urls = {}
        for e in cdp.events:
            if e["method"] == "Network.requestWillBeSent":
                urls[e["params"]["requestId"]] = e["params"]["request"]["url"]
        info["debug"] = []
        for e in cdp.events:
            m, p = e["method"], e.get("params", {})
            url = urls.get(p.get("requestId"), "")
            if any(n in json.dumps(p) + url for n in NOISE):
                continue  # the analytics beacon refuses localhost origins; not a site bug
            if debug_urls and m.startswith("Network.") and any(d in url for d in debug_urls):
                info["debug"].append("%s %s %s" % (m.split(".")[1], url.rsplit("/", 1)[-1],
                                                    p.get("errorText") or p.get("response", {}).get("status") or ("canceled" if p.get("canceled") else "")))
            if m == "Runtime.exceptionThrown":
                d = p.get("exceptionDetails", {})
                problems["exceptions"].append((d.get("exception", {}).get("description") or d.get("text", ""))[:300])
            elif m == "Runtime.consoleAPICalled" and p.get("type") in ("error", "assert"):
                problems["console"].append(" ".join(str(a.get("value", a.get("description", ""))) for a in p.get("args", []))[:300])
            elif m == "Log.entryAdded" and p.get("entry", {}).get("level") == "error":
                en = p["entry"]
                problems["console"].append((en.get("text", "") + " " + en.get("url", ""))[:300])
            elif m == "Network.loadingFailed" and "ERR_ABORTED" not in p.get("errorText", "") and not p.get("blockedReason"):
                problems["failedRequests"].append((p.get("errorText", "") + " " + url).strip())
            elif m == "Network.responseReceived" and p.get("response", {}).get("status", 0) >= 400:
                problems["failedRequests"].append("%s %s" % (p["response"]["status"], p["response"]["url"]))

        if clip_sel:
            box = cdp.eval(clip_box_js(clip_sel))
            if not box:
                raise RuntimeError("clip selector not found: " + clip_sel)
            cdp.send("Emulation.setDeviceMetricsOverride", dict(vp, height=int(box["y"] + box["height"] + 20)))
            cdp.eval("window.scrollTo(0,0)")
            cdp.pump(0.6)
            shot = cdp.send("Page.captureScreenshot", {
                "format": "png", "captureBeyondViewport": True,
                "clip": {"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"], "scale": 1}})
        else:
            shot = cdp.send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
        with open(out_png, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        info.update(problems)
        return info
    finally:
        cdp.close()
        close_target(dbg_port, t["id"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=PAGES)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--port", type=int, default=8123)
    ap.add_argument("--dbg-port", type=int, default=9333)
    ap.add_argument("--only", choices=["desktop", "mobile"], help="one viewport only")
    ap.add_argument("--clip", nargs="+", help="CSS selector(s): capture just these elements")
    ap.add_argument("--settle", type=float, default=2.0, help="seconds to wait after load")
    ap.add_argument("--tag", default="", help="suffix for output file names")
    ap.add_argument("--scroll", action="store_true", help="scroll through the page before capturing (usually unnecessary: the viewport is grown to the full document first)")
    ap.add_argument("--debug-urls", nargs="*", help="print network events for requests whose URL contains any of these")
    ap.add_argument("--sections", action="store_true", help="print section offsets (to pick tiles)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    chrome = find_chrome()
    profile = tempfile.mkdtemp(prefix="vbnb-chrome-")
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(a.port), "--bind", "127.0.0.1"], cwd=REPO,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    chr_ = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % a.dbg_port,
                             "--user-data-dir=" + profile, "--no-first-run", "--no-default-browser-check",
                             "--hide-scrollbars", "--disable-gpu", "--window-size=1440,900", "--lang=en-CA", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = "http://127.0.0.1:%d" % a.port
    bad = 0
    try:
        wait_http(base + "/robots.txt")
        wait_http("http://127.0.0.1:%d/json/version" % a.dbg_port)
        views = [a.only] if a.only else (["desktop"] if a.clip else ["desktop", "mobile"])
        for path in a.paths:
            # accept "the-suite", "/the-suite/", or an MSYS-mangled "C:/Program Files/Git/the-suite/"
            path = re.sub(r"^.*?/Git(/|$)", "/", path.replace("\\", "/"))
            if not path.startswith("/"):
                path = "/" + path
            if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
                path += "/"
            slug = (path.strip("/").replace("/", "_") or "home").replace(".html", "")
            for v, sel in [(v, sel) for v in views for sel in (a.clip or [None])]:
                part = ("-" + re.sub(r"[^a-z0-9]+", "-", sel.lower()).strip("-")) if sel else ""
                name = "%s-%s%s%s.png" % (slug, v, ("-" + a.tag) if a.tag else "", part)
                out_png = os.path.join(a.out, name)
                try:
                    r = shoot(a.dbg_port, base, path, v, out_png, sel, a.settle, not a.scroll, a.debug_urls)
                except Exception as e:
                    print("[%s %s %s] FAILED: %s" % (path, v, sel or "", e))
                    bad += 1
                    continue
                issues = []
                if r["overflowX"] > 0:
                    issues.append("horizontal overflow %dpx: %s" % (r["overflowX"], ", ".join(r["wideElements"])))
                if r["brokenImages"]:
                    issues.append("broken images: " + ", ".join(r["brokenImages"]))
                if r["noAlt"]:
                    issues.append("images without alt: " + ", ".join(r["noAlt"]))
                if r["emptyFromPrices"]:
                    issues.append("%d empty from-price(s)" % r["emptyFromPrices"])
                for k in ("exceptions", "console", "failedRequests"):
                    for x in r[k]:
                        issues.append("%s: %s" % (k, x))
                if issues:
                    bad += 1
                print("%s[%s %s%s] %r h=%d -> %s" % ("OK " if not issues else "!! ", path, v, (" " + sel) if sel else "",
                                                     r["title"][:60], r["height"], os.path.relpath(out_png, REPO)))
                for i in issues:
                    print("     - " + i)
                for d in r.get("debug", []):
                    print("     ~ " + d)
                if a.sections:
                    print("     sections: " + "  ".join(r["sections"]))
    finally:
        chr_.terminate()
        srv.terminate()
        try:
            chr_.wait(5)
        except Exception:
            chr_.kill()
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
