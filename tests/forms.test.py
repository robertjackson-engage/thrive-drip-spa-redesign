#!/usr/bin/env python3
"""The built pages' forms against the CRM form definitions.

The site's forms used to show "Got it" and throw the entry away. These checks pin the
markup forms.js relies on, and that what a page can send is what the CRM forms in
content/crm-forms.spec.json accept, so an enquiry cannot be refused over a renamed field
or a lounge the CRM form does not list.

Run after a build: python3 build.py && python3 tests/forms.test.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")
SPEC = json.load(open(os.path.join(ROOT, "content", "crm-forms.spec.json"), encoding="utf-8"))
SLUGS = json.load(open(os.path.join(ROOT, "content", "website-forms.json"), encoding="utf-8"))
failures = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}: {got}" + ("" if ok else f"  (want {want})"))
    if not ok:
        failures.append(label)


pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html") and not f.startswith("google"))
pages += sorted("blog/" + f for f in os.listdir(os.path.join(SITE, "blog")) if f.endswith(".html"))
# Full pages only: a redirect stub has no footer and no forms.
pages = [p for p in pages if "site-footer" in open(os.path.join(SITE, p), encoding="utf-8").read()]
forms = []          # (page, attributes, inner html)
for name in pages:
    html = open(os.path.join(SITE, name), encoding="utf-8").read()
    for m in re.finditer(r"<form\b([^>]*)>(.*?)</form>", html, re.S):
        forms.append((name, dict(re.findall(r'([a-z-]+)="([^"]*)"', m.group(1))), m.group(2), html[m.end():m.end() + 200]))

print("every form on the site is wired to the CRM, none is a demo")
check("at least 50 full pages checked", len(pages) >= 50, True)
check("forms found (one newsletter form per page, 12 contact forms, 1 franchise form)", len(forms), len(pages) + 13)
check("demo forms left", sum("data-demo" in " ".join(a) or "data-demo" in inner for _, a, inner, _ in forms), 0)
check("forms without a CRM form kind", [p for p, a, _, _ in forms if a.get("data-crm-form") not in SPEC][:3] or 0, 0)
check("forms without the honeypot", [p for p, _, inner, _ in forms if 'name="company_website"' not in inner][:3] or 0, 0)
check("forms without a result line", [p for p, _, inner, after in forms if 'class="form-status' not in inner + after][:3] or 0, 0)
check("forms the CRM tracker could capture a second time", [p for p, a, _, _ in forms if a.get("data-wg-ignore") != "true"][:3] or 0, 0)
missing_script = [p for p in pages if not re.search(r'<script src="[^"]*assets/js/forms\.js\?v=\d+" defer></script>', open(os.path.join(SITE, p), encoding="utf-8").read())]
check("pages that do not load forms.js", missing_script[:3] or 0, 0)
kinds = {}
for _, a, _, _ in forms:
    kinds[a["data-crm-form"]] = kinds.get(a["data-crm-form"], 0) + 1
check("forms by kind", kinds, {"contact": 12, "franchise": 1, "newsletter": len(pages)})
for kind in SPEC:
    if kind == "description":
        continue
    slug = SLUGS[kind]["slug"]
    built = {a.get("data-form-slug", "") for _, a, _, _ in forms if a["data-crm-form"] == kind}
    check(f"{kind} forms carry the configured slug ({slug or 'not connected yet'})", built, {slug})

print("what a page can send is what the CRM form accepts")
# input name -> CRM field key, as forms.js maps them
SENT_AS = {"contact": {"firstName": "firstName", "lastName": "lastName", "email": "email", "phone": "phone", "location": "location",
                       "interest": "interest", "message": "message", "address": "message", "when": "message"},
           "franchise": {"firstName": "firstName", "lastName": "lastName", "email": "email", "phone": "phone",
                         "interest": "background", "city": "city", "message": "message"},
           "newsletter": {"email": "email"}}
ALWAYS = {"contact": {"formName"}, "franchise": set(), "newsletter": {"emailConsent"}}
for page, a, inner, _ in forms:
    kind = a["data-crm-form"]
    names = set(re.findall(r'<(?:input|select|textarea)\b[^>]*\bname="([^"]+)"', inner)) - {"company_website"}
    keys = {f["key"] for f in SPEC[kind]["fields"]}
    unknown = names - set(SENT_AS[kind])
    sent = {SENT_AS[kind][n] for n in names if n in SENT_AS[kind]} | ALWAYS[kind]
    required = {f["key"] for f in SPEC[kind]["fields"] if f.get("required")}
    required_inputs = set(re.findall(r'<(?:input|select|textarea)\b[^>]*\bname="([^"]+)"[^>]*\brequired\b', inner))
    problem = None
    if unknown:
        problem = f"inputs forms.js does not send: {sorted(unknown)}"
    elif sent - keys:
        problem = f"keys the CRM form lacks: {sorted(sent - keys)}"
    elif required - sent:
        problem = f"required CRM fields the page cannot send: {sorted(required - sent)}"
    elif {k for k in required if k not in ALWAYS[kind]} - {SENT_AS[kind][n] for n in required_inputs}:
        problem = "a field the CRM requires is optional on the page"
    if problem:
        check(f"{page} {a.get('data-form-id')}", problem, None)
check("forms whose fields do not match their CRM form", len([f for f in failures if ".html" in f]), 0)
extras = sorted(set(re.findall(r'name="(address|when)"[^>]*data-label="([^"]+)"', "".join(inner for _, _, inner, _ in forms))))
check("extra inputs travel in the message with a label", extras, [("address", "Address"), ("when", "Date and time")])

print("lounges: every page offers exactly the lounges the CRM form maps, and its own is preselected")
website = SPEC["contact"]["settings"]["website"]
allowed = [f for f in SPEC["contact"]["fields"] if f["key"] == website["locationField"]][0]["options"]
check("CRM maps every lounge option to a location number", sorted(website["locations"]), sorted(allowed))
wrong_options, wrong_selected = [], []
build_src = open(os.path.join(ROOT, "build.py"), encoding="utf-8").read()
label_by_slug = dict(re.findall(r'dict\(slug="([^"]+)", label="([^"]+)"', build_src[build_src.index("LOCATIONS = ["):build_src.index("LOC_BY")]))
for page, a, inner, _ in forms:
    if a["data-crm-form"] != "contact":
        continue
    select = re.search(r'<select name="location"[^>]*>(.*?)</select>', inner, re.S)
    values = re.findall(r'<option value="([^"]+)"', select.group(1))
    if values != allowed or "required" not in select.group(0)[:200]:
        wrong_options.append(page)
    selected = re.findall(r'<option value="([^"]+)" selected', select.group(1))
    expected = [label_by_slug[page[:-5]]] if page[:-5] in label_by_slug else (["Mobile / Concierge"] if page == "mobile-iv.html" else [])
    if selected != expected:
        wrong_selected.append(f"{page}: {selected}")
    phone = a.get("data-phone")
    if page[:-5] in label_by_slug and phone == "844-820-1713":
        wrong_selected.append(f"{page}: lounge phone missing")
check("contact forms whose lounge list differs from the CRM form", wrong_options[:3] or 0, 0)
check("contact forms with the wrong lounge preselected or the wrong fallback phone", wrong_selected[:3] or 0, 0)
check("lounge pages with a contact form (corporate and franchise)", sorted(p[:-5] for p, a, _, _ in forms if a["data-crm-form"] == "contact" and p[:-5] in label_by_slug), sorted(label_by_slug))
franchise = [inner for _, a, inner, _ in forms if a["data-crm-form"] == "franchise"][0]
check("franchise enquiry has no lounge field", 'name="location"' in franchise, False)

print("consent: nothing is ticked or implied on the visitor's behalf")
all_inner = "".join(inner for _, _, inner, _ in forms)
check("checkboxes on any form", len(re.findall(r'type="checkbox"', all_inner)), 0)
note = re.search(r'<p class="news-form__note">(.*?)</p>', open(os.path.join(SITE, "index.html"), encoding="utf-8").read()).group(1)
consent = [f for f in SPEC["newsletter"]["fields"] if f["key"] == SPEC["newsletter"]["settings"]["website"]["emailConsentField"]][0]
check("newsletter consent wording on the page is the wording saved in the CRM", note, consent["label"])
check("no CRM form records text-message consent", [k for k in ("contact", "franchise", "newsletter") if "smsConsentField" in SPEC[k]["settings"]["website"]], [])

js = open(os.path.join(SITE, "assets", "js", "main.js"), encoding="utf-8").read()
check("main.js no longer fakes a success", "Got it" in js or "data-demo" in js, False)

print()
if failures:
    print(f"{len(failures)} FAILED: " + ", ".join(failures[:6]))
    sys.exit(1)
print("all form checks passed")
