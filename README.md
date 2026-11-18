# ThrIVe Drip Spa — website redesign

Static marketing site for [ThrIVe Drip Spa](https://thrivedripspa.com) — IV therapy, NAD+, beauty & body
contouring and mobile IV across Houston, Dallas and Fort Worth.

- `build.py` — the whole site as a Python static generator → `docs/` (GitHub Pages)
- `docs/assets/css/main.css` — the "Clear Water" design system (Outfit · Figtree · Grotters brush accent)
- `docs/assets/js/chat.js` — the ThrIVe Concierge, using the published Wellgentic CRM website agent
- `content/` + `docs/admin/` — Sveltia CMS: blog, promotions, events, Site Text, visual editor
- `.github/workflows/build-deploy.yml` — rebuilds and deploys on every push

```bash
python3 build.py && python3 serve.py   # http://localhost:4183
```
See `CMS-SETUP.md` for the one-time login setup and how staff edit the site.

## Checks

```bash
python3 build.py                 # SITE_URL=https://thrivedripspa.com/ for the production build
python3 tests/routing.test.py    # public URLs, old-site redirects, real 404s
python3 tests/seo.test.py        # headings, titles, descriptions, hero loading, inline scripts
node --test tests/*.mjs          # consent and tracking
python3 tools/hero_images.py     # after adding or replacing a hero photo (needs Pillow)
```

An address that is not a page and is not listed in `REDIRECTS` in `serve.py` returns the 404 page with a 404 status. To retire a page, add its old URL to `REDIRECTS`.

## Website chat and tracking

See [THRIVE-CRM-SETUP.md](THRIVE-CRM-SETUP.md) for the installed agent, consent and booking attribution handoff.
