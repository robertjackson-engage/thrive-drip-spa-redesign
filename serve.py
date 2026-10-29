#!/usr/bin/env python3
"""ThrIVe Drip Spa demo server: static site + server-side Anthropic proxy.

The browser calls POST /api/chat; this server forwards it to the Anthropic API
with the key from the ANTHROPIC_API_KEY environment variable, so the key never
appears in any committed file or in client-side code.

Provide the key either way:
  1. Export it:        ANTHROPIC_API_KEY=sk-ant-...  python3 serve.py
  2. Or drop a .env:   echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env  &&  python3 serve.py
The .env file is gitignored, so the key never reaches the repo.
"""
import gzip as _gzip
import http.server
import json
import os
import re
import subprocess
import threading
import time
import socketserver
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "docs")
PORT = int(os.environ.get("PORT", "4183"))
# Azure App Service (WEBSITE_SITE_NAME set) must bind all interfaces; local stays loopback.
HOST = os.environ.get("HOST", "0.0.0.0" if os.environ.get("WEBSITE_SITE_NAME") else "127.0.0.1")

# 301s for every old WordPress URL whose slug changed — SEO continuity at cutover.
# Old pages map to their replacement; retired blog posts go to the closest service
# page (search engines treat a relevant 301 as equity transfer; /blog.html is the floor).
REDIRECTS = {
    "/faqs": "/faq.html", "/booster": "/boosters.html",
    "/terms-and-conditions": "/terms.html", "/privacy-policy": "/privacy.html",
    "/infrared-sauna-therapy": "/infrared-sauna.html",
    "/emsculpt-neo-for-body-contouring": "/emsculpt-neo.html",
    "/book-now": "/book.html", "/certified-medical-drips": "/iv-therapy.html",
    "/concierge-services": "/mobile-iv.html", "/lp-drips": "/iv-therapy.html",
    "/home": "/", "/locations-2": "/locations.html",
    # Old drip product pages: each goes to its new drip page, not the blog index.
    "/drips": "/iv-therapy.html", "/drips/fit": "/fit-drip.html", "/drips/slim": "/slim-drip.html",
    "/drips/beauty": "/beauty-drip.html", "/drips/libido": "/libido-drip.html",
    "/drips/vitamin-c": "/high-c-drip.html", "/drips/immunity": "/immuno-drip.html",
    "/drips/hydration": "/hydrate-drip.html", "/drips/hangover-recovery": "/party-drip.html",
    # Old posts that have a rewritten version on the new blog.
    "/9-benefits-of-hydration-iv-therapy": "/blog/9-benefits-of-hydration-iv-therapy.html",
    "/abc13-news-anchor-reports-on-houston-beauty-drip-spa": "/blog/abc13-tries-thrive.html",
    "/breaking-down-the-science-of-a-myers-cocktail-iv-and-why-it-works": "/blog/myers-cocktail-science.html",
    "/glp-1-microdosing-a-smarter-approach-to-inflammation-metabolism-weight-support": "/blog/glp-1-microdosing.html",
    "/how-does-iv-infusion-work-what-to-expect-from-a-drip-spa": "/blog/first-iv-visit.html",
    "/what-to-expect-during-your-first-iv-drip-therapy-session": "/blog/first-iv-visit.html",
    "/how-long-does-iv-therapy-stay-in-your-system": "/blog/how-long-does-iv-therapy-last.html",
    "/is-a-wellness-infusion-right-for-you-heres-who-benefits-most": "/blog/who-benefits-from-a-wellness-infusion.html",
    "/what-are-the-benefits-of-nad-drips": "/blog/benefits-of-nad-drips.html",
    "/i-tried-nad-iv-therapy-does-it-actually-work": "/blog/benefits-of-nad-drips.html",
    "/what-is-iv-therapy-the-benefits-and-breakdown": "/blog/what-is-iv-therapy.html",
    "/how-iv-therapy-services-support-holistic-health": "/blog/what-is-iv-therapy.html",
    "/how-iv-drips-fit-into-todays-modern-wellness-lifestyle": "/blog/what-is-iv-therapy.html",
    # Retired posts whose topic has a clear service page the keyword map misses.
    "/how-do-zinc-glutathione-and-vitamin-c-benefit-you": "/immuno-drip.html",
    "/covid-19-primer-and-immunity-a-message-from-our-ceo": "/immuno-drip.html",
    "/top-non-invasive-solutions-for-jawline-and-skin-tightening": "/emface.html",
    "/facial-contouring-without-surgery-top-non-invasive-solutions-for-jawline-and-skin-tightening-2": "/emface.html",
    "/thrive-guide-to-looking-your-best-this-summer": "/beauty-drip.html",
    "/i-had-a-hangover-and-then-i-found-thrive-iv-therapy": "/party-drip.html",
    "/finding-the-right-balance-with-vitamin-d": "/shots.html",
    "/ultimate-self-care-checklist-for-west-houston": "/west-university.html",
}
# Retired blog posts: keyword → destination; anything else lands on the blog index.
BLOG_KEYWORD_MAP = [
    ("nad", "/nad.html"), ("emface", "/emface.html"), ("emsculpt", "/emsculpt-neo.html"),
    ("emtone", "/emtone.html"), ("glp-1", "/weight-loss.html"), ("weight", "/weight-loss.html"),
    ("mobile-iv", "/mobile-iv.html"), ("sauna", "/infrared-sauna.html"),
    ("migraine", "/migraine-drip.html"), ("myers", "/myers-drip.html"),
    ("hangover", "/iv-therapy.html"), ("booster", "/boosters.html"), ("biotin", "/shots.html"),
    ("detox", "/detox-drip.html"), ("immune", "/immuno-drip.html"), ("hydrat", "/iv-therapy.html"),
]


def legacy_redirect(path):
    p = path.split("?")[0].rstrip("/") or "/"
    if p in REDIRECTS:
        return REDIRECTS[p]
    # A WP-era slug with no extension that we don't serve: old posts lived at the root.
    slug = p.lstrip("/")
    if slug and "." not in slug and not os.path.exists(os.path.join(SITE, slug + ".html")) \
            and not os.path.isdir(os.path.join(SITE, slug)):
        for kw, dest in BLOG_KEYWORD_MAP:
            if kw in slug:
                return dest
        return "/blog.html"
    return None


def load_dotenv():
    """Populate os.environ from a local .env (KEY=value lines) if present.
    Real environment variables always win over .env values."""
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


load_dotenv()


BUILD_STATE = {"building": False, "last": 0, "ok": True, "log": ""}
_build_lock = threading.Lock()
_build_timer = None


def _run_build():
    with _build_lock:
        BUILD_STATE.update(building=True)
        r = subprocess.run(["python3", os.path.join(ROOT, "build.py")], capture_output=True, text=True, cwd=ROOT)
        BUILD_STATE.update(building=False, last=time.time(), ok=r.returncode == 0,
                           log=(r.stdout + r.stderr)[-2000:])


def schedule_build(delay=0.6):
    """Debounced: several quick saves trigger one rebuild."""
    global _build_timer
    if _build_timer:
        _build_timer.cancel()
    _build_timer = threading.Timer(delay, _run_build)
    _build_timer.daemon = True
    _build_timer.start()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE, **kwargs)

    def end_headers(self):
        # Cache policy: fingerprinted/static assets cache hard; HTML stays fresh so a
        # deploy shows up immediately. Plus baseline security headers on everything.
        p = self.path.split("?")[0]
        if p.startswith("/assets/"):
            self.send_header("Cache-Control", "public, max-age=31536000, immutable" if "?v=" in self.path
                             else "public, max-age=604800")
        elif p.endswith((".webp", ".jpg", ".png", ".gif", ".svg", ".ttf", ".woff2", ".ico")):
            self.send_header("Cache-Control", "public, max-age=604800")
        else:
            self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        # A designed 404 instead of the stock python page.
        if code == 404 and not self.path.startswith("/api/"):
            try:
                body = open(os.path.join(SITE, "404.html"), "rb").read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception:
                pass
        super().send_error(code, message, explain)

    def _maybe_gzip(self, path):
        """Serve text responses gzip-compressed when the client accepts it."""
        ctype = self.guess_type(path)
        if not any(t in ctype for t in ("text/", "javascript", "json", "svg", "xml")):
            return False
        if "gzip" not in (self.headers.get("Accept-Encoding") or ""):
            return False
        try:
            raw = open(path, "rb").read()
        except OSError:
            return False
        gz = _gzip.compress(raw, 6)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(gz)))
        self.send_header("Vary", "Accept-Encoding")
        self.end_headers()
        self.wfile.write(gz)
        return True

    def do_GET(self):
        if self.path == "/healthz":
            self._json(200, {"ok": True})
            return
        if self.path.startswith("/__copy/status"):
            self._json(200, BUILD_STATE)
            return
        dest = legacy_redirect(self.path)
        if dest:
            self.send_response(301)
            self.send_header("Location", dest)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        # Serve extensionless requests for pages we do have (clean URLs keep working).
        slug = self.path.split("?")[0].rstrip("/").lstrip("/")
        if slug and "." not in slug and os.path.exists(os.path.join(SITE, slug + ".html")):
            self.path = "/" + slug + ".html"
        clean = self.path.split("?")[0]
        target = os.path.join(SITE, clean.lstrip("/") or "index.html")
        if os.path.isdir(target):
            target = os.path.join(target, "index.html")
        if os.path.isfile(target) and self._maybe_gzip(target):
            return
        super().do_GET()

    def do_POST(self):
        # Visual text editor (docs/admin/edit.html) saving a page catalogue while working locally.
        # Writes content/copy/<scope>.json and rebuilds the site in the background.
        m = re.fullmatch(r"/__copy/([a-z0-9_-]+)", self.path)
        if m:
            length = int(self.headers.get("Content-Length", 0))
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                assert isinstance(data.get("items"), list) and data.get("page") == m.group(1)
            except Exception:
                self._json(400, {"error": "bad payload"})
                return
            path = os.path.join(ROOT, "content", "copy", m.group(1) + ".json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
            schedule_build()
            self._json(200, {"ok": True, "saved": os.path.relpath(path, ROOT)})
            return
        if self.path != "/api/chat":
            self.send_error(404)
            return
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            self._json(503, {"error": {"message": "Server has no ANTHROPIC_API_KEY. Restart with: ANTHROPIC_API_KEY=sk-ant-... python3 serve.py"}})
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "content-type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.end_headers()
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                        self.wfile.flush()
                    except BrokenPipeError:
                        break
        except urllib.error.HTTPError as e:
            self._raw(e.code, e.read())
        except Exception as e:  # noqa: BLE001 — surface anything to the widget
            self._json(502, {"error": {"message": str(e)}})

    def _raw(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status, obj):
        self._raw(status, json.dumps(obj).encode())

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as srv:
        has_key = "yes" if os.environ.get("ANTHROPIC_API_KEY") else "NO — chat will be disabled"
        print(f"ThrIVe Drip Spa site on http://localhost:{PORT}  (API key present: {has_key})")
        srv.serve_forever()
