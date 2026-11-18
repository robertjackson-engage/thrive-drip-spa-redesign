#!/usr/bin/env python3
"""Public-URL routing rules.

The site is served at the URLs Google has indexed for years — /fort-worth/ — and the
.html file behind each one is an implementation detail. These tests pin that contract,
because the previous arrangement (redirecting /fort-worth/ away to /fort-worth.html)
handed Google a second URL for every page and cost about 59% of non-branded
impressions in four weeks.

Run: python3 tests/routing.test.py
"""
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")
PORT = 4321
BASE = f"http://127.0.0.1:{PORT}"

failures = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}: {got}" + ("" if ok else f"  (want {want})"))
    if not ok:
        failures.append(label)


def body(path):
    """(status, body text) of a GET, including error responses."""
    try:
        r = urllib.request.urlopen(BASE + path, timeout=10)
        return r.getcode(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def head(path):
    """(status, Location) without following the redirect."""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(BASE + path, method="GET")
    try:
        r = opener.open(req, timeout=10)
        return r.getcode(), r.headers.get("Location")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")


def main():
    srv = subprocess.Popen([sys.executable, os.path.join(ROOT, "serve.py")],
                           env={**os.environ, "PORT": str(PORT)},
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(BASE + "/healthz", timeout=1)
                break
            except Exception:
                time.sleep(0.25)

        print("public URLs serve the page")
        for p in ("/", "/fort-worth/", "/katy/", "/clear-lake/", "/west-university/",
                  "/iv-therapy/", "/locations/", "/blog/", "/blog/what-is-iv-therapy/"):
            check(p, head(p)[0], 200)

        print("every other spelling 301s to the public URL")
        for src, dst in (("/fort-worth.html", "/fort-worth/"), ("/fort-worth", "/fort-worth/"),
                         ("/katy.html", "/katy/"), ("/index.html", "/"),
                         ("/blog.html", "/blog/"),
                         ("/blog/what-is-iv-therapy.html", "/blog/what-is-iv-therapy/")):
            code, loc = head(src)
            check(f"{src} -> {dst}", (code, loc), (301, dst))

        print("legacy WordPress URLs and retired aliases still land correctly")
        for src, dst in (("/faqs", "/faq/"), ("/certified-medical-drips", "/iv-therapy/"),
                         ("/drips/hydration", "/hydrate-drip/"), ("/book-now", "/book/"),
                         ("/emsculpt", "/emsculpt-neo/"), ("/normatec", "/body-contouring/")):
            code, loc = head(src)
            check(f"{src} -> {dst}", (code, loc), (301, dst))

        print("old URLs that used to fall through to a catch-all still land where they did")
        for src, dst in (("/drips/nad/", "/nad/"), ("/drips/detoxing/", "/detox-drip/"),
                         ("/biotin/", "/shots/"), ("/beat-the-summer-heat/", "/blog/"),
                         ("/7-wellness-boosters-that-support-energy-levels/", "/boosters/"),
                         ("/how-long-does-iv-therapy-stay-in-your-system/", "/blog/how-long-does-iv-therapy-last/"),
                         ("/iv-drip-therapy-in-fort-worth-texas/", "/fort-worth/")):
            code, loc = head(src)
            check(f"{src} -> {dst}", (code, loc), (301, dst))

        print("an address that was never a page is a real 404 with the designed page")
        for p in ("/this-page-does-not-exist/", "/no-such-page", "/fort-worth/extra/",
                  "/blog/no-such-post/", "/wp-login.php", "/assets/img/", "/nad-typo/"):
            code, loc = head(p)
            check(f"{p} is 404, not a redirect", (code, loc), (404, None))
        code, html = body("/this-page-does-not-exist/")
        check("404 response shows the 404 page", (code, "page not found" in html.lower()), (404, True))

        print("every listed redirect ends on a live page in one hop")
        sys.path.insert(0, ROOT)
        import serve
        broken = [f"{src} -> {dst}" for src, dst in sorted(serve.REDIRECTS.items()) if head(dst)[0] != 200]
        check("redirect targets that are not a 200", broken[:5] or 0, 0)
        shadowed = [src for src in serve.REDIRECTS if serve.page_file(src.strip("/"))]
        check("redirects that would hide a real page", shadowed[:5] or 0, 0)

        print("a redirect never points at another redirect")
        for src in ("/faqs", "/certified-medical-drips", "/fort-worth.html", "/emsculpt"):
            dst = head(src)[1]
            check(f"{src} -> {dst} is final", head(dst)[0], 200)

        print("query strings survive the redirect")
        check("/fort-worth.html?utm_source=gbp",
              head("/fort-worth.html?utm_source=gbp")[1], "/fort-worth/?utm_source=gbp")

        print("assets are untouched")
        for p in ("/assets/css/main.css", "/sitemap.xml", "/robots.txt"):
            check(p, head(p)[0], 200)
    finally:
        srv.terminate()

    print("built pages advertise only public URLs")
    pages = [os.path.join(SITE, f) for f in os.listdir(SITE) if f.endswith(".html")]
    blog = os.path.join(SITE, "blog")
    if os.path.isdir(blog):
        pages += [os.path.join(blog, f) for f in os.listdir(blog) if f.endswith(".html")]
    leaked = []
    for f in pages:
        html = open(f, encoding="utf-8").read()
        for m in re.finditer(r'(?:href|src)="([^"]*\.html[^"]*)"', html):
            if not m.group(1).startswith(("http://", "https://")):
                leaked.append(f"{os.path.relpath(f, SITE)} -> {m.group(1)}")
    check("no internal .html links", leaked[:5] or 0, 0)

    canon = re.search(r'<link rel="canonical" href="([^"]+)"',
                      open(os.path.join(SITE, "fort-worth.html"), encoding="utf-8").read())
    check("canonical is the public URL", canon and canon.group(1),
          "https://thrivedripspa.com/fort-worth/")

    sm = open(os.path.join(SITE, "sitemap.xml"), encoding="utf-8").read()
    check("sitemap has no .html", ".html" in sm, False)
    check("sitemap lists /fort-worth/", "https://thrivedripspa.com/fort-worth/" in sm, True)

    print()
    if failures:
        print(f"{len(failures)} FAILED: " + ", ".join(failures[:6]))
        sys.exit(1)
    print("all routing checks passed")


if __name__ == "__main__":
    main()
