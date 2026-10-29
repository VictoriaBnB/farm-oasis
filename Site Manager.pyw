"""Farm Oasis — Site Manager
Double-click this file (or "Site Manager.bat") to open a small window where you can:
  - set each home to Open / Paused / Hidden
  - change nightly rates by season, long-stay discounts, monthly rate, cleaning fee
  - paste an analytics ID (optional)
  - Preview locally, then Publish (commits and pushes; the website redeploys itself in ~1 minute)
Nothing here needs editing. Settings live in assets/site-config.js.
"""
import json, os, re, sys, subprocess, threading, webbrowser, socket, datetime, traceback
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(ROOT, "assets", "site-config.js")
RENDER = os.path.join(ROOT, "tools", "render_static.py")
SITE_URL = "https://victoriabnb.ca"
PROPS = [("suite", "The Suite (2BR + loft)"), ("smarthome", "The Smart Home (4BR)")]
STATUS_LABELS = [("open", "Open — taking bookings"), ("paused", "Paused — shown as \"not taking bookings right now\""), ("hidden", "Hidden — removed from the home page, form and calendar")]
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
PY = sys.executable.replace("pythonw.exe", "python.exe")


# ── config file helpers ─────────────────────────────────────────────────────
def load_config():
    text = open(CONFIG, encoding="utf-8").read()
    m = re.search(r"(?:var|const|let) SITE_CONFIG = (\{.*\});\s*$", text, re.S)
    return json.loads(m.group(1)), text[: m.start(1)], text[m.end(1):]


def save_config(cfg, head, tail):
    cfg["updated"] = datetime.date.today().isoformat()
    with open(CONFIG, "w", encoding="utf-8", newline="\n") as f:
        f.write(head + json.dumps(cfg, indent=2, ensure_ascii=False) + tail)


def run(cmd, cwd=ROOT):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, creationflags=NO_WINDOW)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close(); return port


# ── UI ──────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Farm Oasis — Site Manager")
        self.geometry("920x860")
        self.minsize(820, 700)
        try:
            self.iconbitmap(os.path.join(ROOT, "favicon.ico"))
        except Exception:
            pass
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except Exception:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel", foreground="#555")
        style.configure("Go.TButton", font=("Segoe UI", 10, "bold"))

        self.cfg, self.head, self.tail = load_config()
        self.vars = {}
        self.server = None

        outer = ttk.Frame(self, padding=14)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Farm Oasis — Site Manager", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Change availability, rates and discounts, then press Publish. The website updates itself within a few minutes (up to 10 for visitors who were just on it).", style="Sub.TLabel").pack(anchor="w", pady=(0, 10))

        nb = ttk.Notebook(outer)
        nb.pack(fill="both", expand=True)
        self.build_availability(nb)
        for key, label in PROPS:
            self.build_rates(nb, key, label)
        self.build_analytics(nb)

        bar = ttk.Frame(outer, padding=(0, 10, 0, 0))
        bar.pack(fill="x")
        ttk.Button(bar, text="Save", command=self.save).pack(side="left")
        ttk.Button(bar, text="Preview in browser", command=self.preview).pack(side="left", padx=8)
        self.publish_btn = ttk.Button(bar, text="Publish to website", style="Go.TButton", command=self.publish)
        self.publish_btn.pack(side="left")
        ttk.Button(bar, text="Open victoriabnb.ca", command=lambda: webbrowser.open(SITE_URL)).pack(side="right")
        self.status = ttk.Label(outer, text="Loaded " + os.path.relpath(CONFIG, ROOT) + " (last published change: " + str(self.cfg.get("updated", "?")) + ")", style="Sub.TLabel")
        self.status.pack(anchor="w", pady=(6, 2))
        self.log = scrolledtext.ScrolledText(outer, height=7, font=("Consolas", 9), state="disabled")
        self.log.pack(fill="x")

    # ── tabs ───────────────────────────────────────────────────────────────
    def build_availability(self, nb):
        f = ttk.Frame(nb, padding=14); nb.add(f, text="Availability")
        ttk.Label(f, text="Which homes are taking bookings?", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        for key, label in PROPS:
            lf = ttk.LabelFrame(f, text=label, padding=12); lf.pack(fill="x", pady=6)
            v = tk.StringVar(value=self.cfg["properties"].get(key, {}).get("status", "open"))
            self.vars[f"{key}.status"] = v
            for val, text in STATUS_LABELS:
                ttk.Radiobutton(lf, text=text, value=val, variable=v).pack(anchor="w")
            row = ttk.Frame(lf); row.pack(fill="x", pady=(8, 0))
            ttk.Label(row, text="Note shown to guests (optional, e.g. \"Back from May 2027\"):").pack(side="left")
            n = tk.StringVar(value=self.cfg["properties"].get(key, {}).get("note", ""))
            self.vars[f"{key}.note"] = n
            ttk.Entry(row, textvariable=n, width=48).pack(side="left", padx=8, fill="x", expand=True)
        ttk.Label(f, text="Paused keeps the home visible (photos, details) but marks it as not bookable; Hidden removes it from the home page, the booking form and the calendar. Its own page stays online with a notice.", style="Sub.TLabel", wraplength=820, justify="left").pack(anchor="w", pady=(10, 0))

    def build_rates(self, nb, key, label):
        f = ttk.Frame(nb, padding=14); nb.add(f, text="Rates — " + label.split(" (")[0])
        c = self.cfg["pricing"][key]
        top = ttk.Frame(f); top.pack(fill="x")
        for i, (field, text) in enumerate([("cleaningFee", "Cleaning fee ($)"), ("maxGuests", "Max guests"), ("defaultNightly", "Nightly rate when no season matches ($)")]):
            ttk.Label(top, text=text).grid(row=0, column=2 * i, sticky="w", padx=(0, 4))
            v = tk.StringVar(value=str(c.get(field, "")))
            self.vars[f"{key}.{field}"] = v
            ttk.Entry(top, textvariable=v, width=8).grid(row=0, column=2 * i + 1, padx=(0, 18))

        sf = ttk.LabelFrame(f, text="Nightly rate by season (dates are MM-DD, inclusive; a range may wrap the year end; leave a row blank to remove it)", padding=10)
        sf.pack(fill="x", pady=(12, 6))
        for j, h in enumerate(["Season name", "From", "To", "$ / night"]):
            ttk.Label(sf, text=h, font=("Segoe UI", 9, "bold")).grid(row=0, column=j, sticky="w", padx=4)
        seasons = list(c.get("seasons", []))
        while len(seasons) < 8:
            seasons.append({})
        for i, s in enumerate(seasons, start=1):
            for j, (field, width) in enumerate([("name", 24), ("from", 7), ("to", 7), ("nightly", 8)]):
                v = tk.StringVar(value=str(s.get(field, "")))
                self.vars[f"{key}.season.{i}.{field}"] = v
                ttk.Entry(sf, textvariable=v, width=width).grid(row=i, column=j, padx=4, pady=2, sticky="w")

        df = ttk.LabelFrame(f, text="Long-stay discounts (% off the nightly subtotal; biggest applicable tier wins)", padding=10)
        df.pack(fill="x", pady=6)
        ttk.Label(df, text="Minimum nights", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=4, sticky="w")
        ttk.Label(df, text="% off", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, padx=4, sticky="w")
        discounts = list(c.get("discounts", []))
        while len(discounts) < 3:
            discounts.append({})
        for i, d in enumerate(discounts, start=1):
            for j, field in enumerate(["minNights", "pct"]):
                v = tk.StringVar(value=str(d.get(field, "")))
                self.vars[f"{key}.discount.{i}.{field}"] = v
                ttk.Entry(df, textvariable=v, width=8).grid(row=i, column=j, padx=4, pady=2, sticky="w")

        mf = ttk.LabelFrame(f, text="Monthly rate (a flat price for the first N nights; applies to stays of the minimum or longer)", padding=10)
        mf.pack(fill="x", pady=6)
        m = c.get("monthly", {})
        for j, (field, text) in enumerate([("minNights", "Minimum nights"), ("perNights", "Nights the price covers"), ("total", "Price for those nights ($)")]):
            ttk.Label(mf, text=text).grid(row=0, column=2 * j, sticky="w", padx=(0, 4))
            v = tk.StringVar(value=str(m.get(field, "")))
            self.vars[f"{key}.monthly.{field}"] = v
            ttk.Entry(mf, textvariable=v, width=9).grid(row=0, column=2 * j + 1, padx=(0, 18))
        ttk.Label(f, text="Tip: keep the direct nightly rate at or below your Airbnb nightly rate, and the monthly total below Airbnb's monthly total — the site promises guests that direct is cheaper.", style="Sub.TLabel", wraplength=820, justify="left").pack(anchor="w", pady=(8, 0))

    def build_analytics(self, nb):
        f = ttk.Frame(nb, padding=14); nb.add(f, text="Analytics")
        a = self.cfg.get("analytics", {})
        ttk.Label(f, text="Optional. Leave blank for no tracking.", style="Sub.TLabel").pack(anchor="w", pady=(0, 8))
        for field, text, hint in [("goatcounter", "GoatCounter code", "Sign up free at goatcounter.com, choose a code such as \"victoriabnb\" and paste just the code here. No cookie banner needed."),
                                  ("ga4", "Google Analytics 4 measurement ID", "Looks like G-XXXXXXXXXX. Create a property at analytics.google.com.")]:
            lf = ttk.LabelFrame(f, text=text, padding=10); lf.pack(fill="x", pady=6)
            v = tk.StringVar(value=a.get(field, "")); self.vars[f"analytics.{field}"] = v
            ttk.Entry(lf, textvariable=v, width=40).pack(anchor="w")
            ttk.Label(lf, text=hint, style="Sub.TLabel", wraplength=800, justify="left").pack(anchor="w", pady=(4, 0))

    # ── collect + validate ─────────────────────────────────────────────────
    def collect(self):
        cfg = json.loads(json.dumps(self.cfg))
        def num(v, what, integer=False):
            s = v.get().strip()
            if s == "":
                raise ValueError(f"{what} is empty")
            try:
                n = float(s.replace(",", "").replace("$", ""))
            except ValueError:
                raise ValueError(f"{what}: '{s}' is not a number")
            if integer:
                if n != int(n):
                    raise ValueError(f"{what} must be a whole number")
                return int(n)
            return int(n) if n == int(n) else n
        for key, _ in PROPS:
            cfg["properties"][key] = {"status": self.vars[f"{key}.status"].get(), "note": self.vars[f"{key}.note"].get().strip()}
            c = cfg["pricing"][key]
            c["cleaningFee"] = num(self.vars[f"{key}.cleaningFee"], f"{key} cleaning fee")
            c["maxGuests"] = num(self.vars[f"{key}.maxGuests"], f"{key} max guests", integer=True)
            c["defaultNightly"] = num(self.vars[f"{key}.defaultNightly"], f"{key} default nightly")
            seasons = []
            for i in range(1, 9):
                name = self.vars[f"{key}.season.{i}.name"].get().strip()
                fr = self.vars[f"{key}.season.{i}.from"].get().strip()
                to = self.vars[f"{key}.season.{i}.to"].get().strip()
                ni = self.vars[f"{key}.season.{i}.nightly"].get().strip()
                if not (name or fr or to or ni):
                    continue
                for v in (fr, to):
                    if not re.fullmatch(r"(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])", v):
                        raise ValueError(f"{key} season '{name}': dates must be MM-DD (got '{v}')")
                seasons.append({"name": name or "Season", "from": fr, "to": to, "nightly": num(self.vars[f"{key}.season.{i}.nightly"], f"{key} season '{name}' nightly")})
            c["seasons"] = seasons
            discounts = []
            for i in range(1, 4):
                mn = self.vars[f"{key}.discount.{i}.minNights"].get().strip()
                pc = self.vars[f"{key}.discount.{i}.pct"].get().strip()
                if not (mn or pc):
                    continue
                discounts.append({"minNights": num(self.vars[f"{key}.discount.{i}.minNights"], f"{key} discount min nights", integer=True),
                                  "pct": num(self.vars[f"{key}.discount.{i}.pct"], f"{key} discount %")})
            c["discounts"] = discounts
            c["monthly"] = {"minNights": num(self.vars[f"{key}.monthly.minNights"], f"{key} monthly minimum nights", integer=True),
                            "perNights": num(self.vars[f"{key}.monthly.perNights"], f"{key} monthly nights covered", integer=True),
                            "total": num(self.vars[f"{key}.monthly.total"], f"{key} monthly price")}
        cfg["analytics"] = {"goatcounter": self.vars["analytics.goatcounter"].get().strip().replace("https://", "").split(".")[0],
                            "ga4": self.vars["analytics.ga4"].get().strip()}
        return cfg

    # ── actions ────────────────────────────────────────────────────────────
    def logln(self, s):
        self.log.configure(state="normal"); self.log.insert("end", s.rstrip() + "\n"); self.log.see("end"); self.log.configure(state="disabled"); self.update_idletasks()

    def save(self, quiet=False):
        try:
            cfg = self.collect()
        except ValueError as e:
            messagebox.showerror("Please check a value", str(e)); return False
        save_config(cfg, self.head, self.tail)
        self.cfg = cfg
        code, out = run([PY, RENDER])
        self.logln(out)
        if code != 0:
            messagebox.showerror("Config problem", out); return False
        self.status.configure(text="Saved. Not published yet — press Publish to put it on the website.")
        if not quiet:
            self.logln("Saved " + os.path.relpath(CONFIG, ROOT))
        return True

    def preview(self):
        if not self.save(quiet=True):
            return
        if not self.server:
            port = free_port()
            self.server = subprocess.Popen([PY, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=ROOT, creationflags=NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.server_port = port
        webbrowser.open(f"http://127.0.0.1:{self.server_port}/")
        self.logln(f"Preview server running at http://127.0.0.1:{self.server_port}/ (closes when this window closes)")

    def publish(self):
        if not self.save(quiet=True):
            return
        if not messagebox.askyesno("Publish", "Publish these settings to victoriabnb.ca now?"):
            return
        self.publish_btn.configure(state="disabled")
        threading.Thread(target=self._publish_worker, daemon=True).start()

    def _publish_worker(self):
        steps = [
            (["git", "pull", "--rebase", "--autostash", "origin", "main"], "Fetching the latest site files"),
            (["git", "add", "-A"], "Staging changes"),
            (["git", "commit", "-m", "Site Manager: update availability / rates"], "Saving a version"),
            (["git", "push", "origin", "main"], "Publishing"),
        ]
        ok = True
        for cmd, label in steps:
            self.logln(f"> {label} …")
            code, out = run(cmd)
            if out.strip():
                self.logln(out)
            if code != 0:
                if cmd[1] == "commit" and "nothing to commit" in out:
                    self.logln("Nothing changed since the last publish.")
                    continue
                ok = False
                self.logln(f"!! {label} failed. Nothing further was done.")
                break
        if ok:
            self.logln(f"Published. The website rebuilds itself in about a minute; visitors see the change within 10 minutes: {SITE_URL}")
            self.after(0, lambda: self.status.configure(text="Published — live within a few minutes."))
            self.after(0, lambda: messagebox.showinfo("Published", f"Done. {SITE_URL} will show the changes within a few minutes (up to 10 if the page was cached).\n\nTo double-check, open the site in a private window after a couple of minutes."))
        else:
            self.after(0, lambda: messagebox.showerror("Publish failed", "Something went wrong — see the log at the bottom of the window. Your settings are saved locally; try Publish again, or ask for help with the message shown."))
        self.after(0, lambda: self.publish_btn.configure(state="normal"))

    def destroy(self):
        if self.server:
            try:
                self.server.terminate()
            except Exception:
                pass
        super().destroy()


if __name__ == "__main__":
    try:
        App().mainloop()
    except Exception:
        try:
            tk.Tk().withdraw()
            messagebox.showerror("Site Manager could not start", traceback.format_exc())
        except Exception:
            raise
