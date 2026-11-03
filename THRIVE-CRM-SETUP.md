# Thrive website CRM installation

The custom Clear Water chat UI uses published Wellgentic website agent **135** in the **Thrive workspace (5)**. Edit its instructions and publish in [CRM](https://crm.wellgentic.ai/agents/website/135). The publishable, origin-restricted installation ID/key live in `content/website-concierge.json`; no model provider credentials belong in the website. `serve.py` no longer exposes a model proxy.

Visitors select member/returning guest or new, then provide name and email or phone before chat. Optional SMS/email permissions remain unchecked. The CRM's existing website intake handles new leads, returning prospects, identity review, idempotency and the action ledger. Chat source is distinct from campaign attribution. The agent cannot book or access private account records; appointment links go to the existing booking app.

Allowed origins are the Azure review host, GitHub Pages, and the two official Thrive domain variants. Only the redesigned site's custom widget is installed; do not additionally paste the standard widget snippet or it will create a second UI.

## Tracking

`docs/assets/js/tracking.js` loads the supplied `wg_trk_33fd34b9794482e2ab37a1fff32de468cf6a` CRM tracking script and existing `GTM-WCDPC5KK` container after optional-cookie acceptance. The supplied public CRM client is preserved in `docs/assets/js/wellgentic-tracking.js` with one Thrive-scoped transport fix: credentialless `fetch` with keepalive instead of credentialed Beacon. The public API allows wildcard CORS, which rejects Beacon’s credentials mode. It retains the supplied tracking key, cookie, consent, attribution and form-ignore behavior. Loading this client locally also avoids the API script’s same-origin resource header. Do not load the original script a second time. This requires no shared API deployment. Essential-only visitors can still chat and book. Browser privacy signals override acceptance. Generic tracker form capture is disabled for forms with their own submission flow to avoid attempted/duplicate leads.

Booking links preserve their route, offer and location parameters, and carry campaign dimensions, the CRM visitor UUID, click identifiers when permitted, and `wg_consent`. The booking repository's `public/website-attribution.js` consumes the handoff before tags initialize. No marketing-platform changes or conversion jobs are needed for this bridge. Existing legacy booking visitors keep the booking app's previous behavior; the explicit website choice is honored when present.

The CRM receives chatbot attribution with the confirmed lead. The booking app receives the same visitor ID and campaign, and sends its existing authoritative lead event. The browser emits `wellgentic_chat_lead` only after a confirmed new-visitor CRM receipt, with a receipt ID and no contact details. This does not create or publish new GTM conversion tags; existing tag configuration remains independently managed.

External Meevo/franchise portals retain their own consent and tracking behavior. This change does not claim to control those external pages.

## Verification and release

Run `python3 build.py`, `node --check docs/assets/js/chat.js`, and `node --test tests/tracking.test.mjs`. Test actual desktop/mobile prechat, live reply, returning identity, and cookie/booking handoff on the Azure review host. Booking changes have their own automated tests and manual production deployment workflow.

Main publishes the review copies at https://thrive-site.azurewebsites.net/ and https://robertjackson-engage.github.io/thrive-drip-spa-redesign/. The public-domain DNS cutover is separate. Review pages remain noindex.
