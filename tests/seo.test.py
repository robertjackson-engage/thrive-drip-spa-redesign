#!/usr/bin/env python3
"""On-page SEO and page-speed rules for the built site (docs/).

These pin the things that were lost in the redesign and cost search traffic: keyword
headings and titles on the corporate lounge pages, local copy, short meta descriptions,
and a hero that paints without waiting for an intro animation.

Run after a build: python3 build.py && python3 tests/seo.test.py
"""
import os
import re
import subprocess
import sys
import tempfile
from html import unescape
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")
failures = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}: {got}" + ("" if ok else f"  (want {want})"))
    if not ok:
        failures.append(label)


def read(name):
    return open(os.path.join(SITE, name), encoding="utf-8").read()


def text_of(fragment):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def h1(html):
    return text_of(re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.S).group(1))


def title(html):
    return unescape(re.search(r"<title>(.*?)</title>", html, re.S).group(1))


def description(html):
    return unescape(re.search(r'<meta name="description" content="([^"]*)"', html).group(1))


def main_text(html):
    main = re.search(r"<main\b.*?</main>", html, re.S).group(0)
    return text_of(re.sub(r"<(script|style)\b.*?</\1>", " ", main, flags=re.S))


class Balance(HTMLParser):
    """Counts tags so a truncated or unbalanced page is caught."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.h1 = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.h1 += 1
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
        else:
            self.errors.append(tag)


CORPORATE = {
    "west-university.html": ("IV Therapy in West University, Houston", "West University"),
    "memorial.html": ("IV Therapy in Memorial, Houston", "Memorial"),
    "the-woodlands.html": ("IV Therapy in The Woodlands, TX", "The Woodlands"),
    "fort-worth.html": ("IV Therapy in Fort Worth, Texas", "Fort Worth"),
    "highland-park.html": ("IV Therapy in Highland Park, Dallas", "Highland Park"),
}

print("corporate lounge pages lead with the keyword and the neighbourhood")
for name, (want_h1, place) in CORPORATE.items():
    html = read(name)
    check(f"{name} h1", re.sub(r"\s+,", ",", h1(html)), want_h1)
    check(f"{name} title starts 'IV Therapy in {place}'", title(html).startswith(f"IV Therapy in {place}"), True)
    check(f"{name} description names {place}", place in description(html), True)
    uses = len(re.findall(r"iv therapy", main_text(html), re.I))
    check(f"{name} says 'IV therapy' 5 to 10 times in the page body ({uses})", 5 <= uses <= 10, True)
    about = re.search(r'About the [^<]+ lounge</p>.*?</section>', html, re.S)
    words = len(text_of(about.group(0)).split()) if about else 0
    check(f"{name} local copy section is 230 to 500 words ({words})", 230 <= words <= 500, True)

print("the homepage heading names the service and the cities, with the brand line under it")
home = read("index.html")
check("home h1", h1(home), "IV Therapy in Houston, Dallas & Fort Worth")
check("brand line kept as the sub-heading", text_of(re.search(r'<p class="hero__tagline">(.*?)</p>', home, re.S).group(1)), "Hydrate. Energize. Thrive.")

pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html") and not f.startswith("google"))
pages += sorted("blog/" + f for f in os.listdir(os.path.join(SITE, "blog")) if f.endswith(".html"))

print("every page: one h1, a short description, balanced markup, valid inline scripts")
long_desc, bad_h1, unbalanced, bad_js, lazy_hero, no_preload, preloader = [], [], [], [], [], [], []
for name in pages:
    html = read(name)
    if len(description(html)) > 155:
        long_desc.append(f"{name} ({len(description(html))})")
    parser = Balance()
    parser.feed(html)
    if parser.h1 != 1:
        bad_h1.append(f"{name} ({parser.h1})")
    if parser.errors or parser.stack or "</body>\n</html>" not in html[-200:]:
        unbalanced.append(f"{name} {parser.errors[:2]} {parser.stack[:2]}")
    for script in re.findall(r"<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>(.*?)</script>", html, re.S):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(script)
        if subprocess.run(["node", "--check", fh.name], capture_output=True).returncode:
            bad_js.append(name)
        os.unlink(fh.name)
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            __import__("json").loads(block)
        except ValueError:
            bad_js.append(name + " (json-ld)")
    hero = re.search(r'<img\b[^>]*fetchpriority="high"[^>]*>', html)
    if hero:
        if 'loading="lazy"' in hero.group(0):
            lazy_hero.append(name)
        src = re.search(r'\ssrc="([^"]*)"', hero.group(0)).group(1)
        preload = re.search(r'<link rel="preload" as="image" href="([^"]*)"', html)
        if not preload or preload.group(1) != src or html.index("<link rel=\"preload\" as=\"image\"") > html.index("</head>"):
            no_preload.append(name)
    if "preloader" in html:
        preloader.append(name)
check("meta descriptions over 155 characters", long_desc[:5] or 0, 0)
check("pages without exactly one h1", bad_h1[:5] or 0, 0)
check("pages with unbalanced markup", unbalanced[:5] or 0, 0)
check("pages with an inline script that does not parse", bad_js[:5] or 0, 0)
check("hero images marked lazy", lazy_hero[:5] or 0, 0)
check("hero images without a matching preload in <head>", no_preload[:5] or 0, 0)
check("pages that still ship the full-screen preloader", preloader[:5] or 0, 0)

print("the hero is revealed by the page itself, not after an intro")
check("inline reveal script is first in <body>", bool(re.search(r"<body>\s*<script>requestAnimationFrame", home)), True)
js = open(os.path.join(SITE, "assets", "js", "main.js"), encoding="utf-8").read()
check("main.js has no intro timer", "INTRO_MS" in js or "preloader" in js, False)

print("the brand script font is served compressed")
check("WOFF2 font is preloaded", '<link rel="preload" href="/assets/fonts/Grotters.woff2" as="font" type="font/woff2" crossorigin>' in home, True)
font_dir = os.path.join(SITE, "assets", "fonts")
check("WOFF2 is under half the size of the TTF", os.path.getsize(os.path.join(font_dir, "Grotters.woff2")) * 2 < os.path.getsize(os.path.join(font_dir, "Grotters.ttf")), True)
css = open(os.path.join(SITE, "assets", "css", "main.css"), encoding="utf-8").read()
check("stylesheet offers WOFF2 first, TTF as fallback", bool(re.search(r'Grotters\.woff2"\) format\("woff2"\), url\("\.\./fonts/Grotters\.ttf"\)', css)), True)

print("hero images are served at phone-friendly sizes")
home_hero = re.search(r'<img\b[^>]*fetchpriority="high"[^>]*>', home).group(0)
check("homepage hero has a srcset", "srcset=" in home_hero, True)
sizes = [os.path.getsize(os.path.join(SITE, p.lstrip("/"))) for p in re.findall(r"(/assets/img/[^ ,\"]+\.webp) \d+w", home_hero)]
check("largest homepage hero file is under 100 KB", bool(sizes) and max(sizes) < 100_000, True)
missing = [p for name in pages for p in re.findall(r"(/assets/img/[^ ,\"]+) \d+w", read(name)) if not os.path.isfile(os.path.join(SITE, p.lstrip("/")))]
check("srcset files that do not exist", missing[:5] or 0, 0)

print("the sitemap lists landing pages only")
sitemap = read("sitemap.xml")
check("thank-you page is not in the sitemap", "thank-you" in sitemap, False)
check("404 page is not in the sitemap", "/404" in sitemap, False)
check("lounge pages are in the sitemap", all(f"/{n[:-5]}/</loc>" in sitemap for n in CORPORATE), True)

print("the 'how long does IV therapy stay in your system' post is back to full length")
post = read("blog/how-long-does-iv-therapy-last.html")
words = len(text_of(re.search(r'<div class="post-body[^"]*">(.*?)</div>\s*<div class="reveal"', post, re.S).group(1)).split())
check(f"post body is at least 650 words ({words})", words >= 650, True)

print()
if failures:
    print(f"{len(failures)} FAILED: " + ", ".join(failures[:6]))
    sys.exit(1)
print("all SEO checks passed")
