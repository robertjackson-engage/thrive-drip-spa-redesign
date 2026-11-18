/* ThrIVe website forms. Each form posts to its published Wellgentic CRM form and shows
   "sent" only after the CRM confirms the receipt. On any failure the visitor keeps what
   they typed and is given a phone number. Nothing is ever reported as sent when it was not. */
(() => {
  'use strict';
  const API = 'https://api.wellgentic.ai/f/';
  const MAIN_PHONE = '844-820-1713';
  const TIMEOUT_MS = 20000;
  const SENT = {
    contact: 'Thank you — your message is with our team. We’ll be in touch within one business day.',
    franchise: 'Thank you — your request is with our franchise team. We’ll follow up with the next steps.',
    newsletter: 'You’re on the list. Thank you for joining.',
  };
  const uuid = () => {
    if (crypto.randomUUID) return crypto.randomUUID();
    const b = crypto.getRandomValues(new Uint8Array(16));
    b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
    const h = [...b].map(v => v.toString(16).padStart(2, '0')).join('');
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
  };
  const value = (form, name) => { const el = form.elements[name]; return el && typeof el.value === 'string' ? el.value.trim() : ''; };
  // The same campaign and consent record the chat sends; the CRM drops identifiers the visitor has not allowed.
  const attribution = () => {
    try { if (window.THRIVE_CRM && typeof window.THRIVE_CRM.attribution === 'function') return window.THRIVE_CRM.attribution(); } catch {}
    return { landingPage: location.origin + location.pathname, consentState: { analytics: 'denied', ads: 'denied', personalization: 'denied' } };
  };

  /* What each form sends. Keys are the field keys of the CRM form (content/crm-forms.spec.json). */
  const answers = (form, kind) => {
    if (kind === 'newsletter') return { email: value(form, 'email'), emailConsent: 'yes' };
    const data = { firstName: value(form, 'firstName'), lastName: value(form, 'lastName'), email: value(form, 'email'), phone: value(form, 'phone') };
    if (kind === 'franchise') return { ...data, background: value(form, 'interest'), city: value(form, 'city'), message: value(form, 'message') };
    // Extra inputs on a contact-style form (mobile IV: address, date and time) travel inside the message, labelled.
    const extra = [...form.querySelectorAll('[data-label]')].filter(el => el.value.trim()).map(el => `${el.dataset.label}: ${el.value.trim()}`);
    return { ...data, location: value(form, 'location'), interest: value(form, 'interest'),
      message: [...extra, value(form, 'message')].filter(Boolean).join('\n'), formName: form.dataset.formName || '' };
  };

  const bind = form => {
    const kind = form.dataset.crmForm;
    const button = form.querySelector('button[type="submit"]');
    const status = form.querySelector('.form-status') || (form.nextElementSibling && form.nextElementSibling.classList.contains('form-status') ? form.nextElementSibling : null);
    let sending = false, requestId = null;

    const show = (text, state) => {
      if (!status) return;
      status.textContent = text; status.hidden = !text;
      status.classList.toggle('is-ok', state === 'ok'); status.classList.toggle('is-error', state === 'error');
      // The result must be seen: on a phone it can sit below the fold or behind the booking bar.
      if (state && typeof status.scrollIntoView === 'function') status.scrollIntoView({ block: 'center', behavior: 'smooth' });
    };
    const fail = (reason, retry = true) => {
      const phone = form.dataset.phone || MAIN_PHONE;
      const call = `call us on ${phone}${phone === MAIN_PHONE ? '' : ' or ' + MAIN_PHONE}.`;
      show(`${reason || 'Sorry — we couldn’t send this just now.'} ${retry ? 'Your details are still here: please try again, or ' + call : 'Please ' + call}`, 'error');
    };
    const busy = on => {
      sending = on; form.setAttribute('aria-busy', on ? 'true' : 'false');
      if (button) button.disabled = on;
    };
    // An edited form is a new submission; an unchanged retry reuses its id so the CRM cannot save it twice.
    form.addEventListener('input', () => { requestId = null; });
    form.addEventListener('change', () => { requestId = null; });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (sending) return;
      if (typeof form.reportValidity === 'function' && !form.reportValidity()) return;
      // Filled only by bots: nothing is sent, and nothing claims it was.
      if (value(form, 'company_website')) return fail();
      const slug = form.dataset.formSlug;
      if (!slug) return fail('Online messages are not switched on yet.', false);
      requestId = requestId || uuid();
      const body = { ...answers(form, kind), _meta: { ...attribution(), requestId } };
      for (const key of Object.keys(body)) if (body[key] === '') delete body[key];
      busy(true); show('Sending…');
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
      try {
        const response = await fetch(API + encodeURIComponent(slug) + '/submit', {
          method: 'POST', credentials: 'omit', signal: controller.signal,
          headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
        });
        const result = await response.json().catch(() => ({}));
        // The CRM returns an eventId only when it has saved this submission.
        if (response.ok && result.success === true && typeof result.eventId === 'string' && result.eventId) {
          requestId = null;
          form.reset();
          form.querySelectorAll('.field select').forEach(select => select.closest('.field').classList.toggle('has-value', !!select.value));
          show(SENT[kind] || SENT.contact, 'ok');
          form.dispatchEvent(new CustomEvent('thrive:form-success', { bubbles: true, detail: { formId: form.dataset.formId || kind, formName: form.dataset.formName || kind } }));
        } else {
          // A 400 carries a plain reason from the CRM ("Please enter a valid phone number.").
          fail(response.status === 400 && typeof result.error === 'string' && result.error.length < 160 ? result.error : '');
        }
      } catch {
        fail();
      } finally {
        clearTimeout(timer); busy(false);
      }
    });
  };

  const start = () => document.querySelectorAll('form[data-crm-form]').forEach(bind);
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', start, { once: true }) : start();
})();
