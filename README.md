# ThrIVe Drip Spa — website redesign

Static marketing site for [ThrIVe Drip Spa](https://thrivedripspa.com) — IV therapy, NAD+, beauty & body
contouring and mobile IV across Houston, Dallas and Fort Worth.

- `build.py` — the whole site as a Python static generator → `docs/` (GitHub Pages)
- `docs/assets/css/main.css` — the "Clear Water" design system (Outfit · Figtree · Grotters brush accent)
- `docs/assets/js/chat.js` — the ThrIVe Concierge (Claude), key proxied by `serve.py`
- `content/` + `docs/admin/` — Sveltia CMS: blog, promotions, events, Site Text, visual editor
- `.github/workflows/build-deploy.yml` — rebuilds and deploys on every push

```bash
python3 build.py && python3 serve.py   # http://localhost:4183
```
See `CMS-SETUP.md` for the one-time login setup and how staff edit the site.
