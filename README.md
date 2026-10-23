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

## Hosting: Azure Static Web Apps (production)
`.github/workflows/azure-static-web-apps.yml` builds the site and deploys `docs/` to Azure on every push to `main`.
`build.py` also writes `docs/staticwebapp.config.json`: 301 redirects from every old WordPress address
(`OLD_URLS` in `build.py`) and the custom 404 page. The GitHub Pages copy is a preview and is marked `noindex`.

One-time setup:
1. Azure portal → **Create a resource → Static Web App** → plan **Free** (or Standard), deployment source **Other**.
2. On the new app: **Manage deployment token** → copy it → GitHub repo **Settings → Secrets and variables → Actions**
   → new secret `AZURE_STATIC_WEB_APPS_API_TOKEN`. Re-run the *Azure Static Web Apps* workflow.
3. Check the site on its `*.azurestaticapps.net` address, then **Custom domains** → add `thrivedripspa.com`
   and `www.thrivedripspa.com` and update DNS as Azure shows. HTTPS certificates are automatic.
4. After the domain points at Azure: submit `https://thrivedripspa.com/sitemap.xml` in Google Search Console
   and update each lounge's Google Business Profile website link to its new page.
