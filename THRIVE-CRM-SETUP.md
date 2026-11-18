# Thrive website CRM installation

The custom Clear Water chat UI uses published Wellgentic website agent **135** in the **Thrive workspace (5)**. Edit its instructions and publish in [CRM](https://crm.wellgentic.ai/agents/website/135). The publishable, origin-restricted installation ID/key live in `content/website-concierge.json`; no model provider credentials belong in the website. `serve.py` no longer exposes a model proxy.

Visitors select member/returning guest or new, then provide name and email or phone before chat. Optional SMS/email permissions remain unchecked. The CRM's existing website intake handles new leads, returning prospects, identity review, idempotency and the action ledger. Chat source is distinct from campaign attribution. The agent cannot book or access private account records; appointment links go to the existing booking app.

Allowed origins are the Azure review host, GitHub Pages, and the two official Thrive domain variants. Only the redesigned site's custom widget is installed; do not additionally paste the standard widget snippet or it will create a second UI.

## Tracking

`docs/assets/js/tracking.js` loads the supplied `wg_trk_33fd34b9794482e2ab37a1fff32de468cf6a` CRM tracking script and existing `GTM-WCDPC5KK` container by default (opt-out model, adopted 2026-11): tracking is off only when the visitor chose Decline on the cookie notice (stored in `tds_privacy_v1`) or the browser sends Global Privacy Control / Do Not Track. Google Consent Mode defaults follow the same rule. Declining clears the tracking cookies and reloads the page. The supplied public CRM client is preserved in `docs/assets/js/wellgentic-tracking.js` with one Thrive-scoped transport fix: credentialless `fetch` with keepalive instead of credentialed Beacon. The public API allows wildcard CORS, which rejects Beacon’s credentials mode. It retains the supplied tracking key, cookie, consent, attribution and form-ignore behavior. Loading this client locally also avoids the API script’s same-origin resource header. Do not load the original script a second time. This requires no shared API deployment. Visitors who decline can still chat and book. Browser privacy signals override acceptance. Generic tracker form capture is disabled for forms with their own submission flow to avoid attempted/duplicate leads.

Booking links preserve their route, offer and location parameters, and carry campaign dimensions, the CRM visitor UUID, click identifiers when permitted, and `wg_consent`. The booking repository's `public/website-attribution.js` consumes the handoff before tags initialize. No marketing-platform changes or conversion jobs are needed for this bridge. Existing legacy booking visitors keep the booking app's previous behavior; the explicit website choice is honored when present.

The CRM receives chatbot attribution with the confirmed lead. The booking app receives the same visitor ID and campaign, and sends its existing authoritative lead event. The browser emits `wellgentic_chat_lead` only after a confirmed new-visitor CRM receipt, with a receipt ID and no contact details. This does not create or publish new GTM conversion tags; existing tag configuration remains independently managed.

### Site events (dataLayer)

`tracking.js` pushes these events for GTM, only while tracking is allowed, and never with a phone number, email address or query string:

| Event | When | Parameters |
| --- | --- | --- |
| `booking_click` | Click on a link to `book.thrivedripspa.com` or a `meevo.com` customer portal (including the member login) | `link_url` (origin + path), `link_text`, `lounge`, `cta_position` |
| `click_to_call` | Click on a `tel:` link | `lounge` (location pages only), `cta_position` |
| `contact_link_click` | Click on a `mailto:` link | `link_type` (`email`), `lounge`, `cta_position` |
| `form_submit` | Confirmed form submission | `form_id`, `form_name` |
| `wellgentic_chat_lead` | Confirmed new-visitor chat lead (unchanged) | `event_id`, `form_source`, `agent_id` |

`lounge` is a location slug (`fort-worth`), taken from the link's `loc` / `locationId` or the location page being viewed. `cta_position` is `header`, `hero`, `body`, `footer`, `sticky` or `chat`. `form_submit` fires for the concierge contact form on its confirmed CRM receipt. The contact, franchise and newsletter forms fire it from `forms.js` on their confirmed CRM receipt (see "Website forms" below).

## Website forms

The contact forms (contact page, every lounge page, mobile IV page), the franchise form and the footer newsletter form post to **published Wellgentic CRM forms** from `docs/assets/js/forms.js`:

`POST https://api.wellgentic.ai/f/<slug>/submit` with a JSON body of the form's field keys plus `_meta` (the same attribution object the chat sends, and a `requestId`). The endpoint is public (the slug is the address), allows any origin, and needs no key. This is the CRM's own website-form intake (`routes/crm-forms-public.ts`, `services/crmFormService.ts` in the CRM server). The chat's `/api/widget/leads` endpoint is **not** used for forms: it needs an open chat conversation, has no message or lounge field, insists on a first and last name (so an email-only newsletter signup is refused), and files every entry as a chat lead.

**Setup (once):** create the three forms defined in `content/crm-forms.spec.json` in the CRM (Thrive workspace), review and publish each, and paste the three slugs into `content/website-forms.json`. Until a slug is there, that form does not pretend: it tells the visitor to call.

| Website form | CRM form | CRM purpose | What is saved |
| --- | --- | --- | --- |
| Contact, lounge pages, mobile IV | Website contact form | `lead` | name, email, phone, lounge (as the CRM location), interest, message, which website form |
| Franchise | Website franchise enquiry | `service_request` (kept out of the client lead pipeline) | name, email, phone, background, city or state, message |
| Footer newsletter | Website newsletter signup | `newsletter` | email, email opt-in with the wording shown under the field |

Rules the code keeps:

- **"Sent" means confirmed.** The CRM returns an `eventId` only when it has saved the submission. Without it (any error, a timeout, a reply with no `eventId`) the visitor sees an error with the lounge's phone number and 844-820-1713, and everything they typed stays in the form.
- **No double saves.** A retry of an unchanged form reuses its `requestId`, which the CRM treats as the same submission. The button is disabled while sending.
- **Bots.** A hidden `company_website` field (the CRM's own honeypot name) must stay empty; if it is filled nothing is sent.
- **Consent.** No form sends a text-message opt-in: there is no text-consent checkbox on the site, so none is recorded. The newsletter form sends an email opt-in, because joining the newsletter is the request; the wording under the field (`NEWSLETTER_CONSENT` in `build.py`) must stay identical to the label of the `emailConsent` field in the CRM form, which is what the CRM stores as the disclosure. Contact and franchise forms record no marketing opt-in.
- **Lounge.** The lounge select sends the lounge name; the CRM form maps each name to its location number (`settings.website.locations`), so corporate and franchise enquiries are filed under the right lounge. If a lounge is added or renamed in `build.py`, update the CRM form's options and map too (`tests/forms.test.mjs` fails until the spec file matches). A lounge the CRM form does not know is refused by the CRM and the visitor gets the error with the phone number.
- **Analytics.** Each confirmed receipt dispatches `thrive:form-success`, which `tracking.js` turns into the `form_submit` dataLayer event (form id and name only).
- The CRM forms are created with `automationMode: "manual"`: the enquiry is saved and appears on the contact, but no automatic text, email or cadence starts. Switch the contact form to `automatic` in the CRM when the team wants new-lead automations to run for website enquiries.

External Meevo/franchise portals retain their own consent and tracking behavior. This change does not claim to control those external pages.

## Verification and release

Run `python3 build.py`, `node --check docs/assets/js/chat.js`, `node --test tests/*.mjs`, and `python3 tests/forms.test.py` (after the build). Test actual desktop/mobile prechat, live reply, returning identity, and cookie/booking handoff on the Azure review host. Booking changes have their own automated tests and manual production deployment workflow.

Main publishes to Azure App Service and the GitHub Pages review copy. Azure builds with `SITE_URL=https://thrivedripspa.com/` so the production domain has indexable pages and a production sitemap. The server sends `X-Robots-Tag: noindex, nofollow` on the Azure preview hostname; GitHub Pages retains its noindex build. `www.thrivedripspa.com` redirects to the canonical root domain, preserving paths and query parameters. The local copy editor is disabled on Azure hosting.

DNS cutover requires the `asuid` and `asuid.www` TXT values from Azure's `customDomainVerificationId`, custom hostname bindings and HTTPS certificates for both domain variants, an apex A record pointing to Azure's verified inbound IP, and a `www` CNAME to `thrive-site.azurewebsites.net`. Preserve email, booking, other subdomains and verification records. Publishing this code does not itself change DNS.
