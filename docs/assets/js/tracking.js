/* Thrive's consent and attribution bridge. CRM lead writes stay with chat/booking. */
(() => {
  'use strict';
  const LOCAL_TRACKER = new URL('wellgentic-tracking.js?v=20261103-transport1', document.currentScript.src).href;
  const PRIVACY_PAGE = new URL('../../privacy.html', document.currentScript.src).href;
  const TRACKER = 'https://api.wellgentic.ai/api/crm-tracking/script/wg_trk_33fd34b9794482e2ab37a1fff32de468cf6a';
  const CAMPAIGN = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','utm_id','utm_source_platform'];
  const ADS = ['gclid','gbraid','wbraid','fbclid','fb_ad_id'];
  const ALL = [...CAMPAIGN, ...ADS];
  const query = new URLSearchParams(location.search);
  const limited = v => typeof v === 'string' ? v.slice(0, 255) : '';
  const read = key => { try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch { return null; } };
  const write = (key, value) => { try { value === null ? localStorage.removeItem(key) : localStorage.setItem(key, JSON.stringify(value)); } catch {} };
  const privacySignal = navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true;
  let preference = read('tds_privacy_v1');
  if (privacySignal) preference = { allowed: false };
  // Opt-out model: measurement is on unless the visitor declined or the browser sends GPC / Do Not Track.
  let allowed = preference?.allowed !== false;
  let stored = read('tds_attr');
  if (!stored || Date.now() - stored.at > 90 * 864e5) stored = null;
  const landing = {};
  ALL.forEach(k => { if (query.get(k)) landing[k] = limited(query.get(k)); });
  // A new campaign is one complete touch: never mix yesterday's click ID with today's UTM.
  let current = Object.keys(landing).length ? landing : (allowed && stored?.p || {});
  let landingPage = location.origin + location.pathname;
  let referrer = '';
  try { const r = new URL(document.referrer); referrer = r.origin + r.pathname; } catch {}
  if (allowed && stored && !Object.keys(landing).length) {
    landingPage = stored.landingPage || landingPage; referrer = stored.referrer || referrer;
  }
  const consent = () => ({ analytics: allowed ? 'granted' : 'denied', ads: allowed ? 'granted' : 'denied', personalization: 'denied', source: privacySignal ? 'browser_privacy_signal' : 'thrive_cookie_preferences', updatedAt: new Date().toISOString() });
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  const googleConsent = () => ({ analytics_storage: allowed ? 'granted' : 'denied', ad_storage: allowed ? 'granted' : 'denied', ad_user_data: allowed ? 'granted' : 'denied', ad_personalization: allowed ? 'granted' : 'denied', functionality_storage:'granted', security_storage:'granted' });
  gtag('consent', 'default', googleConsent());
  window.__wgConsent = consent();
  const saveTouch = () => {
    if (!allowed) return;
    const touch = { at: Date.now(), p: current, landingPage, referrer };
    stored = { ...touch, first: stored?.first || touch };
    write('tds_attr', stored);
  };
  const cookie = name => { try { const p = document.cookie.split('; ').find(v => v.startsWith(name+'=')); return p ? decodeURIComponent(p.slice(name.length+1)) : ''; } catch { return ''; } };
  const visitorKey = () => {
    if (!allowed) return '';
    try { return window.__wg_tracking?.getTrackingId() || JSON.parse(cookie('_wg_track') || '{}').id || ''; } catch { return ''; }
  };
  const attribution = () => {
    const result = { landingPage, referrer, consentState: consent() };
    CAMPAIGN.forEach(k => { if (current[k]) result[k.replace(/_([a-z])/g, (_,c) => c.toUpperCase())] = current[k]; });
    if (allowed) {
      ADS.filter(k => k !== 'fb_ad_id').forEach(k => { if(current[k]) result[k] = current[k]; });
      result.visitorKey = visitorKey();
      const tracked = window.__wg_tracking?.getAttribution() || {};
      for (const k of ['gaClientId','gaSessionId','fbp']) if(tracked[k]) result[k]=tracked[k];
      // Only use an fbc for this touch, never one from a different campaign.
      if (current.fbclid) result.fbc = tracked.fbc?.endsWith('.'+current.fbclid) ? tracked.fbc : 'fb.1.' + (stored?.at || Date.now()) + '.' + current.fbclid;
    }
    return result;
  };
  const decorate = value => {
    const url = new URL(value, document.baseURI);
    if (url.origin !== 'https://book.thrivedripspa.com') return url.href;
    if (allowed) {
      ALL.forEach(k => { if(current[k] && !url.searchParams.has(k)) url.searchParams.set(k,current[k]); });
      if(visitorKey()) url.searchParams.set('wg_uuid',visitorKey());
    } else {
      ADS.forEach(k => url.searchParams.delete(k)); url.searchParams.delete('wg_uuid');
      CAMPAIGN.forEach(k => { if(current[k] && !url.searchParams.has(k)) url.searchParams.set(k,current[k]); });
    }
    url.searchParams.set('wg_consent',allowed ? 'granted' : 'denied');
    return url.href;
  };
  window.THRIVE_CRM = Object.freeze({ attribution, decorateBookingUrl: decorate });
  // Site events for GTM. Never a phone number, email address or query string; nothing when declined.
  // Every key is always set (undefined when unknown) so GTM cannot reuse a value from an earlier event.
  const LOUNGES = { 201102:'memorial', 202035:'memorial-green', 203017:'the-heights', 201104:'west-university', 203330:'vintage-park', 203033:'katy', 201319:'the-woodlands', 203215:'clear-lake', 203321:'highland-park', 203322:'fort-worth' };
  const pageLounge = () => { const slug = location.pathname.replace(/\/+$/,'').split('/').pop().replace(/\.html$/,''); return Object.values(LOUNGES).includes(slug) ? slug : undefined; };
  const position = anchor => {
    if (anchor.getRootNode && anchor.getRootNode() !== document) return 'chat';
    for (const [selector, name] of [['header, .menu-overlay','header'],['footer','footer'],['.sticky-cta','sticky'],['.hero','hero'],['main','body']]) if (anchor.closest(selector)) return name;
  };
  const track = (event, params) => { if (allowed) window.dataLayer.push({ event, ...params }); };
  const trackLink = anchor => {
    const url = new URL(anchor.href, document.baseURI);
    const cta_position = position(anchor);
    if (url.protocol === 'tel:') return track('click_to_call', { lounge: pageLounge(), cta_position });
    if (url.protocol === 'mailto:') return track('contact_link_click', { link_type: 'email', lounge: pageLounge(), cta_position });
    const booking = url.origin === 'https://book.thrivedripspa.com' || (/(^|\.)meevo\.com$/.test(url.hostname) && /^\/customerportal\//i.test(url.pathname));
    if (!booking) return;
    const loc = url.searchParams.get('loc') || url.searchParams.get('locationId');
    const text = (anchor.textContent || '').replace(/[→↗]/g,'').replace(/\s+/g,' ').trim().slice(0,80);
    track('booking_click', { link_url: url.origin + url.pathname, link_text: /@|\d{3}\D?\d{4}/.test(text) ? undefined : text || undefined, lounge: LOUNGES[loc] || (/^\d{1,10}$/.test(loc || '') ? loc : pageLounge()), cta_position });
  };
  const onLink = event => {
    const anchor = event.composedPath().find(node => node?.tagName === 'A' && node.href);
    if (!anchor) return;
    try { anchor.href = decorate(anchor.href); } catch {}
    // auxclick also fires for the right button; only a middle click opens the link.
    if (event.type === 'auxclick' && event.button !== 1) return;
    try { trackLink(anchor); } catch {}
  };
  document.addEventListener('click',onLink,true);
  document.addEventListener('auxclick',onLink,true);
  let loaded = false;
  const loadTracking = () => {
    if (!allowed || loaded) return;
    loaded = true;
    // These forms already have authoritative submission handlers. Never capture
    // an attempted submit a second time through the generic tracking endpoint.
    document.querySelectorAll('form').forEach(form => form.setAttribute('data-wg-ignore','true'));
    const crm = document.createElement('script'); crm.async = true; crm.crossOrigin = 'anonymous'; crm.src = LOCAL_TRACKER; crm.dataset.source = TRACKER; crm.dataset.thriveTracking = 'true'; document.head.append(crm);
    window.dataLayer.push({'gtm.start':Date.now(), event:'gtm.js'});
    const gtm = document.createElement('script'); gtm.async = true; gtm.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-WCDPC5KK'; document.head.append(gtm);
  };
  const clearTracking = () => {
    write('tds_attr',null);
    // The GTM container's own site identity tag keeps wg_uuid and wg_<campaign key> copies; remove those too.
    for (const key of ['wg_uuid', ...ALL.map(k => 'wg_'+k)]) write(key,null);
    for (const name of ['_wg_track','wg_uuid','_fbc','_fbp','_ga','_ga_XN01L3VWSH']) {
      document.cookie = name+'=; Max-Age=0; path=/; SameSite=Lax';
      if (location.hostname === 'thrivedripspa.com' || location.hostname.endsWith('.thrivedripspa.com')) document.cookie=name+'=; Max-Age=0; path=/; domain=.thrivedripspa.com; SameSite=Lax';
    }
  };
  const choose = value => {
    const revoke = allowed && !value;
    allowed = value && !privacySignal;
    preference = {allowed, at:Date.now()}; write('tds_privacy_v1',preference);
    window.__wgConsent = consent(); window.__wg_tracking?.setConsent(consent());
    gtag('consent','update',googleConsent());
    if (allowed) { saveTouch(); loadTracking(); } else clearTracking();
    document.getElementById('thrive-cookie-notice')?.remove();
    // Reload on revocation so already-loaded third-party listeners cannot keep running.
    if (revoke) location.reload();
  };
  const showPreferences = () => {
    if (document.getElementById('thrive-cookie-notice')) return;
    const panel = document.createElement('section'); panel.id='thrive-cookie-notice'; panel.className='cookie-notice'; panel.setAttribute('aria-label','Cookie preferences');
    panel.innerHTML='<p>We use cookies to understand visits and measure our advertising. You can decline and still chat and book. <a>Privacy policy</a></p><div class="cookie-actions"><button type="button" data-choice="deny">Decline</button><button type="button" data-choice="allow">OK</button></div>';
    panel.querySelector('a').href=PRIVACY_PAGE;
    if (preference && !privacySignal) panel.querySelector('p').append(allowed ? ' Currently on.' : ' Currently declined.');
    if (privacySignal) { panel.querySelector('p').textContent='Your browser’s privacy preference is active, so analytics and advertising cookies are off. You can still chat and book.'; panel.querySelector('[data-choice="allow"]').remove(); panel.querySelector('[data-choice="deny"]').textContent='OK'; }
    panel.querySelector('[data-choice="deny"]').onclick=()=>choose(false);
    const accept=panel.querySelector('[data-choice="allow"]'); if(accept)accept.onclick=()=>choose(true);
    document.body.append(panel);
  };
  const ready = () => {
    if (allowed) { saveTouch(); loadTracking(); } else clearTracking();
    if (!preference && !privacySignal) showPreferences();
    document.querySelectorAll('[data-cookie-preferences]').forEach(button => button.addEventListener('click',showPreferences));
  };
  document.readyState==='loading' ? document.addEventListener('DOMContentLoaded',ready,{once:true}) : ready();
  // A site form reports success by dispatching `thrive:form-success` with {formId, formName} once its
  // submission is confirmed. forms.js does this for the contact, franchise and newsletter forms.
  document.addEventListener('thrive:form-success', event => track('form_submit', { form_id: limited(event.detail?.formId) || undefined, form_name: limited(event.detail?.formName) || undefined }));
  window.addEventListener('wellgentic-chat:lead-received', event => {
    track('form_submit', { form_id: 'concierge-contact', form_name: 'Concierge chat contact form' });
    if (!allowed || event.detail?.visitorType !== 'new') return;
    // A confirmed CRM receipt, with no contact details or chat text in dataLayer.
    window.dataLayer.push({ event:'wellgentic_chat_lead', event_id:event.detail.requestId, form_source:'chatbot', agent_id:String(event.detail.workflowId) });
  });
})();
