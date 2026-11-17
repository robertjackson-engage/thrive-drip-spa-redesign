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
