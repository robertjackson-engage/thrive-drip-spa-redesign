# Content Manager (CMS) — Setup & How-To

This site has a built-in **visual content manager** so non-technical staff can write blog
posts, post promotions and events, and change any text on any page — no code needed.

- **Editor:** [Sveltia CMS](https://github.com/sveltia/sveltia-cms) (free, open-source)
- **Where staff go:** `https://<your-site>/admin/`
- **What they can edit:** Blog Posts · Promotions & Specials · Events · Site Text (every sentence on every page)
- **How publishing works:** Saving in `/admin` commits to this repo → a GitHub Action
  rebuilds the site and redeploys it live in ~1 minute. No servers to babysit, $0 hosting.

## Content lives in the repo
```
content/
  blog/        *.md   — blog posts (title, date, author, cover image, excerpt, category, body)
  promotions/  *.md   — specials (name, price/offer, valid-through, image, link, featured, details)
  events/      *.md   — events (name, date, location, image, link, description)
  copy/        *.json — Site Text catalogues, one per page (+ _site.json for header/menu/footer)
```
`build.py` reads these to generate `/blog`, the Promotions and Events pages and the home-page cards.
Uploaded images land in `docs/assets/img/` automatically.

## One-time setup: enable staff login (≈5 minutes, repo owner)
The CMS edits via GitHub, so it needs a GitHub OAuth app to let editors sign in.

1. **Create an OAuth app:** GitHub → Settings → Developer settings → **OAuth Apps** → *New*.
   - Application name: `ThrIVe Drip Spa CMS`
   - Homepage URL: your site URL
   - Authorization callback URL: `https://YOUR-AUTH-WORKER/callback` (from step 2)
   - Save the **Client ID** and generate a **Client Secret**.
2. **Deploy the free auth worker** (Cloudflare Workers, free tier):
   `https://github.com/sveltia/sveltia-cms-auth` — paste the Client ID/Secret as
   the worker's `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` env vars.
3. **Point the CMS at it:** in `docs/admin/config.yml`, under `backend:` add
   `base_url: https://YOUR-AUTH-WORKER`.
4. **Invite editors:** add each staff member as a repo collaborator (Settings → Collaborators).
   They log in at `/admin` with their GitHub account — that's the only account they need.

> Prefer email/password logins with zero GitHub accounts? Host the same site on
> **Netlify** (also free) and use Netlify Identity + Git Gateway — the `/admin` and
> `content/` work unchanged; only the `backend:` block in config.yml changes.

## Daily use (staff)
1. Go to `/admin`, sign in.
2. Pick a collection (e.g. **Promotions & Specials**) → **New**.
3. Fill the friendly fields, drag in an image, write the copy.
4. **Publish.** The site updates itself within a minute.

## Site Text — edit any text on any page
- In the CMS sidebar open **Site Text**. One entry per page (`index`, `memberships`, `katy`, …)
  plus **`_site`**, which holds the header, menus and footer shared by every page.
- Each page lists its text in page order. **Where** tells you the element and the heading it sits
  under; **Original** is what the design started with; change **Text** and save.
- Blog posts, promotions and events are edited in their own collections.

How it works: `copy_layer.py` runs inside `build.py`. After a page renders, it catalogues each text
node into the page's JSON (stable ids from the text and its position), then swaps in any entry whose
Text differs from Original. Running `python3 build.py` also refreshes the catalogues.

## Visual text editor — click any text on the page to change it
Open **/admin/edit.html** (there is also a button on the /admin login screen).
- Pick a page. The live page loads in the preview; hover any text and it outlines.
- **Click** a sentence, heading, button or menu item → edit it in the side panel; the preview updates live.
- **Save & publish** writes the change to GitHub; the site rebuilds in about a minute. The first time
  it asks for a GitHub access token with write access (fine-grained token, *Contents: Read and write*).
- Working locally (`python3 serve.py`), Save writes straight to `content/copy/` and rebuilds.

## Local preview (developers)
```bash
python3 build.py && python3 serve.py      # → http://localhost:4183  (+ /admin/, /admin/edit.html)
npx @sveltia/cms-proxy-server             # optional: lets /admin edit local files without GitHub
```
The AI concierge needs `ANTHROPIC_API_KEY` in `.env` (gitignored); serve.py proxies it server-side.
