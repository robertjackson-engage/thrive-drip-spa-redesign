/* Thrive's consent and attribution bridge. CRM lead writes stay with chat/booking. */
(() => {
  'use strict';
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
  let allowed = preference?.allowed === true;
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
  const onLink = event => {
    const anchor = event.composedPath().find(node => node?.tagName === 'A' && node.href);
    if (anchor) try { anchor.href = decorate(anchor.href); } catch {}
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
    const crm = document.createElement('script'); crm.async = true; crm.src = TRACKER; crm.dataset.thriveTracking = 'true'; document.head.append(crm);
    window.dataLayer.push({'gtm.start':Date.now(), event:'gtm.js'});
    const gtm = document.createElement('script'); gtm.async = true; gtm.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-WCDPC5KK'; document.head.append(gtm);
  };
  const clearTracking = () => {
    write('tds_attr',null);
    for (const name of ['_wg_track','_fbc','_fbp','_ga','_ga_XN01L3VWSH']) {
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
    panel.innerHTML='<div><strong>Your privacy, your choice.</strong><p>We use optional cookies to understand visits and measure our advertising. You can chat and book without them.</p></div><div class="cookie-actions"><button type="button" data-choice="deny">Essential only</button><button type="button" data-choice="allow">Accept optional cookies</button></div>';
    if (privacySignal) { panel.querySelector('p').textContent='Your browser’s privacy preference is active. Optional tracking is off. You can still chat and book.'; panel.querySelector('[data-choice="allow"]').remove(); }
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
  window.addEventListener('wellgentic-chat:lead-received', event => {
    if (!allowed || event.detail?.visitorType !== 'new') return;
    // A confirmed CRM receipt, with no contact details or chat text in dataLayer.
    window.dataLayer.push({ event:'wellgentic_chat_lead', event_id:event.detail.requestId, form_source:'chatbot', agent_id:String(event.detail.workflowId) });
  });
})();
