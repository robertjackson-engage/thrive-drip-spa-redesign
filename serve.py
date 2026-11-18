#!/usr/bin/env python3
"""ThrIVe static preview server. Website chat is served by Wellgentic CRM."""
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
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "docs")
PORT = int(os.environ.get("PORT", "4183"))
# Azure App Service (WEBSITE_SITE_NAME set) must bind all interfaces; local stays loopback.
HOST = os.environ.get("HOST", "0.0.0.0" if os.environ.get("WEBSITE_SITE_NAME") else "127.0.0.1")
IS_HOSTED = bool(os.environ.get("WEBSITE_SITE_NAME"))
CANONICAL_HOST = "thrivedripspa.com"

# 301s for every old WordPress URL whose slug changed — SEO continuity at cutover.
# Old pages map to their replacement; retired blog posts go to the closest service
# page (search engines treat a relevant 301 as equity transfer). A URL that is not
# listed here and is not a page returns 404.
REDIRECTS = {
    "/faqs": "/faq/", "/booster": "/boosters/",
    "/terms-and-conditions": "/terms/", "/privacy-policy": "/privacy/",
    "/infrared-sauna-therapy": "/infrared-sauna/",
    "/emsculpt-neo-for-body-contouring": "/emsculpt-neo/",
    "/book-now": "/book/", "/certified-medical-drips": "/iv-therapy/",
    "/concierge-services": "/mobile-iv/", "/lp-drips": "/iv-therapy/",
    "/home": "/", "/locations-2": "/locations/",
    # Old drip product pages: each goes to its new drip page, not the blog index.
    "/drips": "/iv-therapy/", "/drips/fit": "/fit-drip/", "/drips/slim": "/slim-drip/",
    "/drips/beauty": "/beauty-drip/", "/drips/libido": "/libido-drip/",
    "/drips/vitamin-c": "/high-c-drip/", "/drips/immunity": "/immuno-drip/",
    "/drips/hydration": "/hydrate-drip/", "/drips/hangover-recovery": "/party-drip/",
    # Old posts that have a rewritten version on the new blog.
    "/9-benefits-of-hydration-iv-therapy": "/blog/9-benefits-of-hydration-iv-therapy/",
    "/abc13-news-anchor-reports-on-houston-beauty-drip-spa": "/blog/abc13-tries-thrive/",
    "/breaking-down-the-science-of-a-myers-cocktail-iv-and-why-it-works": "/blog/myers-cocktail-science/",
    "/glp-1-microdosing-a-smarter-approach-to-inflammation-metabolism-weight-support": "/blog/glp-1-microdosing/",
    "/how-does-iv-infusion-work-what-to-expect-from-a-drip-spa": "/blog/first-iv-visit/",
    "/what-to-expect-during-your-first-iv-drip-therapy-session": "/blog/first-iv-visit/",
    "/how-long-does-iv-therapy-stay-in-your-system": "/blog/how-long-does-iv-therapy-last/",
    "/is-a-wellness-infusion-right-for-you-heres-who-benefits-most": "/blog/who-benefits-from-a-wellness-infusion/",
    "/what-are-the-benefits-of-nad-drips": "/blog/benefits-of-nad-drips/",
    "/i-tried-nad-iv-therapy-does-it-actually-work": "/blog/benefits-of-nad-drips/",
    "/what-is-iv-therapy-the-benefits-and-breakdown": "/blog/what-is-iv-therapy/",
    "/how-iv-therapy-services-support-holistic-health": "/blog/what-is-iv-therapy/",
    "/how-iv-drips-fit-into-todays-modern-wellness-lifestyle": "/blog/what-is-iv-therapy/",
    # Retired posts whose topic has a clear service page the keyword map misses.
    "/how-do-zinc-glutathione-and-vitamin-c-benefit-you": "/immuno-drip/",
    "/covid-19-primer-and-immunity-a-message-from-our-ceo": "/immuno-drip/",
    "/top-non-invasive-solutions-for-jawline-and-skin-tightening": "/emface/",
    "/facial-contouring-without-surgery-top-non-invasive-solutions-for-jawline-and-skin-tightening-2": "/emface/",
    "/thrive-guide-to-looking-your-best-this-summer": "/beauty-drip/",
    "/i-had-a-hangover-and-then-i-found-thrive-iv-therapy": "/party-drip/",
    "/finding-the-right-balance-with-vitamin-d": "/shots/",
    "/ultimate-self-care-checklist-for-west-houston": "/west-university/",
    "/emsculpt": "/emsculpt-neo/", "/normatec": "/body-contouring/",
    # Every other old WordPress URL that existed (pre-launch crawl plus URLs with Search
    # Console impressions since May 2026), each sent to its closest page. These used to be
    # caught by a catch-all that redirected ANY unknown address; now only listed URLs move.
    "/7-wellness-boosters-that-support-energy-levels": "/boosters/",
    "/an-iv-med-spa-is-the-ultimate-destination-for-hydration-health-and-beauty": "/iv-therapy/",
    "/beyond-the-finish-line-the-importance-of-hydration-performance-recovery-this-halloween-weekend": "/iv-therapy/",
    "/biotin": "/shots/",
    "/blogs/news/how-long-does-iv-therapy-last-in-your-system": "/blog/how-long-does-iv-therapy-last/",
    "/drips/detoxing": "/detox-drip/",
    "/drips/migraine": "/migraine-drip/",
    "/drips/myers": "/myers-drip/",
    "/drips/nad": "/nad/",
    "/emface-at-thrive-drip-spa-a-revolutionary-approach-to-preventing-facial-aging-and-boosting-collagen": "/emface/",
    "/emface-for-noninvasive-facial-contouring-welcome-to-the-future": "/emface/",
    "/experience-the-benefits-of-ultimate-detox-with-iv-therapy": "/detox-drip/",
    "/fort-orth": "/fort-worth/",
    "/glp-1-weight-loss-therapy": "/weight-loss/",
    "/how-does-an-iv-drip-support-your-holistic-weight-loss-program": "/weight-loss/",
    "/how-infrared-sauna-therapy-supports-muscle-recovery-and-pain-relief": "/infrared-sauna/",
    "/how-long-do-iv-therapy-stay-in-your-system": "/blog/how-long-does-iv-therapy-last/",
    "/how-long-does-iv-therapy-stay-in-system": "/blog/how-long-does-iv-therapy-last/",
    "/how-to-prevent-back-to-school-illness-with-immune-iv-therapy": "/immuno-drip/",
    "/how-to-support-weight-loss-while-using-glp-1-medications": "/weight-loss/",
    "/hydrate-drip-houston-texas": "/hydrate-drip/",
    "/introducing-thrive-migraine-drip": "/migraine-drip/",
    "/iv-drip-therapy-in-fort-worth-texas": "/fort-worth/",
    "/iv-infusion-houston-beat-dehydration": "/iv-therapy/",
    "/iv-therapy-in-houston-heights": "/the-heights/",
    "/migraine-drip-houston-texas": "/migraine-drip/",
    "/mobile-iv-drip-dont-come-to-us-well-come-to-you": "/mobile-iv/",
    "/myers-iv-therapy-recovery-made-simple": "/myers-drip/",
    "/nad-drip-houston-texas": "/nad/",
    "/nad-therapy-for-mental-health-stress-addiction-support": "/nad/",
    "/the-benefits-of-a-detox-drip": "/detox-drip/",
    "/the-benefits-of-emtone-for-skin-firming-and-muscle-toning-treatment": "/emtone/",
    "/top-tips-for-staying-hydrated-in-houston": "/iv-therapy/",
    "/what-is-emsculpt-neo-and-how-does-it-work": "/emsculpt-neo/",
    "/what-is-nad-and-how-will-it-help-you-improve-your-neuro-function-and-general-wellness-with-nad-today": "/nad/",
    "/whats-better-than-a-tall-glass-of-water-a-visit-to-a-hydration-spa-of-course": "/iv-therapy/",
    "/youve-lost-the-weight-now-lose-the-flab": "/weight-loss/",
    # Old posts and pages with no close equivalent: the blog index.
    "/beat-the-summer-heat": "/blog/",
    "/category/uncategorized": "/blog/",
    "/cryotherapy": "/blog/",
    "/dont-miss-a-beat-on-your-houston-trip-iv-therapy-for-jetlag-recovery": "/blog/",
    "/health-benefits/strained-muscles": "/blog/",
    "/how-thrive-services-help-kickstart-a-healthier-lifestyle": "/blog/",
    "/iv-drip-therapy-in-santa-clara-and-st-george-utah": "/blog/",
    "/sitemap": "/blog/",
    "/the-pros-and-cons-of-botox-houston-thrive": "/blog/",
    "/tips-for-making-wellness-iv-drip-therapy-part-of-your-healthy-lifestyle": "/blog/",
}


def legacy_redirect(path):
    """The 301 target for an old WordPress URL, or None.

    Only the URLs listed in REDIRECTS move. An address that was never a page gets a real
    404 from the normal file handling below, not a redirect to the blog: redirecting every
    unknown URL made typos and junk links look like live pages to search engines.
    """
    p = path.split("?")[0].rstrip("/") or "/"
    return REDIRECTS.get(p)


def page_file(slug):
    """The built file that backs a public page URL, or None.

    /blog/ is served by docs/blog.html while /blog/what-is-iv-therapy/ is served by
    docs/blog/what-is-iv-therapy.html, so the flat file wins before the directory.
    """
    if not slug or slug.startswith(("assets/", "api/")) or ".." in slug:
        return None
    for candidate in (slug + ".html", os.path.join(slug, "index.html")):
        full = os.path.join(SITE, candidate)
        if os.path.isfile(full):
            return full
    return None


def canonical_redirect(path):
    """Send every other spelling of a page to its public URL: /fort-worth/.

    Google has indexed the trailing-slash form of these pages for years, so that form
    is the destination, not the thing being redirected away. /fort-worth.html and
    /fort-worth both 301 to it, which leaves exactly one indexable URL per page.
    """
    p = path.split("?")[0]
    if p in ("/", "/index.html"):
        return "/" if p == "/index.html" else None
    if p.endswith(".html"):
        slug = p[1:-len(".html")]
        return "/" + slug + "/" if page_file(slug) else None
    if not p.endswith("/"):
        slug = p.lstrip("/")
        return "/" + slug + "/" if page_file(slug) else None
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
        # The Azure build is indexable on its production domain only. Keep the
        # direct Azure preview out of search even after the production build ships.
        if self.headers.get("Host", "").split(":", 1)[0].lower() != CANONICAL_HOST:
            self.send_header("X-Robots-Tag", "noindex, nofollow")
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
                if self.command != "HEAD":
                    self.wfile.write(body)
                return
            except Exception:
                pass
        super().send_error(code, message, explain)

    def list_directory(self, path):
        # A folder without an index page is not a page: 404, never a file listing.
        self.send_error(404)
        return None

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
        if self.headers.get("Host", "").split(":", 1)[0].lower() == "www." + CANONICAL_HOST:
            self.send_response(301)
            self.send_header("Location", "https://" + CANONICAL_HOST + self.path)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path == "/healthz":
            self._json(200, {"ok": True})
            return
        if self.path.startswith("/__copy/status"):
            if IS_HOSTED:
                self.send_error(404)
                return
            self._json(200, BUILD_STATE)
            return
        dest = legacy_redirect(self.path) or canonical_redirect(self.path)
        if dest:
            self.send_response(301)
            query = urlsplit(self.path).query
            self.send_header("Location", dest + ("?" + query if query else ""))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        # /fort-worth/ is the public URL; docs/fort-worth.html is what backs it.
        clean = self.path.split("?")[0]
        target = page_file(clean.strip("/")) if clean != "/" else os.path.join(SITE, "index.html")
        if target is None:
            target = os.path.join(SITE, clean.lstrip("/"))
        if os.path.isfile(target):
            self.path = "/" + os.path.relpath(target, SITE)
            if self._maybe_gzip(target):
                return
        super().do_GET()

    def do_HEAD(self):
        # HEAD must mirror GET's routing (www canonical, legacy 301s, clean URLs) —
        # SimpleHTTPRequestHandler's default bypasses do_GET, so crawlers and uptime
        # monitors that probe with HEAD were seeing 404s for pages GET serves fine.
        if self.headers.get("Host", "").split(":", 1)[0].lower() == "www." + CANONICAL_HOST:
            self.send_response(301)
            self.send_header("Location", "https://" + CANONICAL_HOST + self.path)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        dest = legacy_redirect(self.path) or canonical_redirect(self.path)
        if dest:
            self.send_response(301)
            query = urlsplit(self.path).query
            self.send_header("Location", dest + ("?" + query if query else ""))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        clean = self.path.split("?")[0]
        target = page_file(clean.strip("/")) if clean != "/" else None
        if target:
            self.path = "/" + os.path.relpath(target, SITE)
        super().do_HEAD()

    def do_POST(self):
        # Visual text editor (docs/admin/edit.html) saving a page catalogue while working locally.
        # Writes content/copy/<scope>.json and rebuilds the site in the background.
        m = re.fullmatch(r"/__copy/([a-z0-9_-]+)", self.path)
        if m:
            # The copy editor is a local authoring tool. Public hosting must never
            # accept unauthenticated content writes or trigger rebuilds.
            if IS_HOSTED:
                self.send_error(404)
                return
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
        self.send_error(404)

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
        print(f"ThrIVe Drip Spa site on http://localhost:{PORT}")
        srv.serve_forever()
