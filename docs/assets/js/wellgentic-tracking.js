/* Wellgentic public tracking client, captured 2026-11-03.
 * Thrive-scoped transport compatibility fix: credentialless fetch instead of
 * credentialed Beacon. Source: supplied CRM tracking script URL in tracking.js.
 * Keep its cookie, consent, form-ignore and attribution contract intact. */
(function(w, d, apiKey, endpoint) {
  'use strict';

  if (navigator.doNotTrack === '1' || w.doNotTrack === '1') return;

  var WG = w.__wg_tracking = {};
  var COOKIE_NAME = '_wg_track';
  var COOKIE_DAYS = 365;
  var pageEntryTime = Date.now();
  var pages = [];
  var sessionStart = Date.now();

  // ─── Cookie helpers ──────────────────────────────────────────────────────

  function setCookie(name, value, days) {
    var expires = '';
    if (days) {
      var d = new Date();
      d.setTime(d.getTime() + days * 86400000);
      expires = '; expires=' + d.toUTCString();
    }
    var secure = w.location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/; SameSite=Lax' + secure;
  }

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function uuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0;
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
  }

  // ─── Tracking data store ─────────────────────────────────────────────────

  function getTrackingData() {
    var raw = getCookie(COOKIE_NAME);
    if (raw) {
      try { return JSON.parse(raw); } catch(e) {}
    }
    return null;
  }

  function saveTrackingData(data) {
    setCookie(COOKIE_NAME, JSON.stringify(data), COOKIE_DAYS);
  }

  function getParam(name) {
    try {
      return new URLSearchParams(w.location.search).get(name) || '';
    } catch (e) {
      var match = w.location.search.match(new RegExp('[?&]' + name + '=([^&]*)'));
      return match ? decodeURIComponent(match[1]) : '';
    }
  }

  function getCookieByPrefix(prefix) {
    var parts = document.cookie ? document.cookie.split(/;\s*/) : [];
    for (var i = 0; i < parts.length; i++) {
      var separator = parts[i].indexOf('=');
      var name = separator >= 0 ? parts[i].slice(0, separator) : parts[i];
      if (name.indexOf(prefix) === 0) {
        return separator >= 0 ? decodeURIComponent(parts[i].slice(separator + 1)) : '';
      }
    }
    return '';
  }

  function getGaClientId() {
    var value = getCookie('_ga') || '';
    var parts = value.split('.');
    return parts.length >= 4 ? parts.slice(-2).join('.') : '';
  }

  function getGaSessionId() {
    var value = getCookieByPrefix('_ga_');
    if (!value) return '';
    var parts = value.split('.');
    if (parts[0] === 'GS1' && parts.length > 2) return parts[2] || '';
    if (parts[0] === 'GS2' && parts.length > 1) {
      var session = parts[1].match(/(?:^|&)s(\d+)/);
      return session ? session[1] : '';
    }
    return '';
  }

  function normalizeConsent(value, source) {
    value = value && typeof value === 'object' ? value : {};
    function state(key) {
      var current = String(value[key] || 'unknown').toLowerCase();
      return current === 'granted' || current === 'denied' ? current : 'unknown';
    }
    return {
      analytics: state('analytics'),
      ads: state('ads'),
      personalization: state('personalization'),
      source: source || String(value.source || 'unavailable'),
      updatedAt: new Date().toISOString()
    };
  }

  // ─── Initialize tracking ─────────────────────────────────────────────────

  var data = getTrackingData() || {};
  if (!data.id) data.id = uuid();
  if (!data.firstVisit) data.firstVisit = new Date().toISOString();

  var utmSource = getParam('utm_source');
  var utmMedium = getParam('utm_medium');
  var utmCampaign = getParam('utm_campaign');
  var utmContent = getParam('utm_content');
  var utmTerm = getParam('utm_term');
  var utmId = getParam('utm_id');
  var utmSourcePlatform = getParam('utm_source_platform');

  if (utmSource && !data.utmSource) data.utmSource = utmSource;
  if (utmMedium && !data.utmMedium) data.utmMedium = utmMedium;
  if (utmCampaign && !data.utmCampaign) data.utmCampaign = utmCampaign;
  if (utmContent && !data.utmContent) data.utmContent = utmContent;
  if (utmTerm && !data.utmTerm) data.utmTerm = utmTerm;
  if (utmId && !data.utmId) data.utmId = utmId;
  if (utmSourcePlatform && !data.utmSourcePlatform) data.utmSourcePlatform = utmSourcePlatform;

  // Ad click IDs — write-once so the first ad click wins attribution.
  var gclid = getParam('gclid');
  var gbraid = getParam('gbraid');
  var wbraid = getParam('wbraid');
  var fbclid = getParam('fbclid');
  if (gclid && !data.gclid) data.gclid = gclid;
  if (gbraid && !data.gbraid) data.gbraid = gbraid;
  if (wbraid && !data.wbraid) data.wbraid = wbraid;
  if (fbclid && !data.fbclid) data.fbclid = fbclid;
  if (!data.fbc) data.fbc = getCookie('_fbc') || '';
  if (!data.fbp) data.fbp = getCookie('_fbp') || '';
  if (fbclid && !data.fbc) {
    data.fbc = 'fb.1.' + Date.now() + '.' + fbclid;
    setCookie('_fbc', data.fbc, 90);
  }
  data.gaClientId = getGaClientId() || data.gaClientId || '';
  data.gaSessionId = getGaSessionId() || data.gaSessionId || '';
  data.consentState = normalizeConsent(w.__wgConsent || data.consentState, w.__wgConsent ? 'window' : 'unavailable');

  if (!data.landingPage) data.landingPage = w.location.href;
  if (!data.referrer && d.referrer && d.referrer.indexOf(w.location.hostname) === -1) {
    data.referrer = d.referrer;
  }

  data.lastSeen = new Date().toISOString();
  saveTrackingData(data);

  // ─── Send to API ─────────────────────────────────────────────────────────

  function send(path, payload) {
    if (data.consentState && data.consentState.analytics === 'denied') return;
    payload.apiKey = apiKey;
    payload.trackingId = data.id;
    try {
      // This public endpoint authenticates with the tracking key in the body.
      // Beacon always includes credentials, which cannot use wildcard CORS.
      if (w.fetch) {
        w.fetch(endpoint + path, {
          method: 'POST', mode: 'cors', credentials: 'omit', keepalive: true,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).catch(function() {});
      } else {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', endpoint + path, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(payload));
      }
    } catch(e) {}
  }

  // ─── Page view tracking ──────────────────────────────────────────────────

  function trackPageView() {
    var entry = {
      url: w.location.href,
      title: d.title,
      timestamp: new Date().toISOString()
    };
    pages.push(entry);

    send('/pageview', {
      url: entry.url,
      title: entry.title,
      referrer: d.referrer || '',
      utmSource: data.utmSource || '',
      utmMedium: data.utmMedium || '',
      utmCampaign: data.utmCampaign || '',
      utmContent: data.utmContent || '',
      utmTerm: data.utmTerm || '',
      utmId: data.utmId || '',
      utmSourcePlatform: data.utmSourcePlatform || '',
      gclid: data.gclid || '',
      gbraid: data.gbraid || '',
      wbraid: data.wbraid || '',
      fbclid: data.fbclid || '',
      fbc: data.fbc || '',
      fbp: data.fbp || '',
      gaClientId: getGaClientId() || data.gaClientId || '',
      gaSessionId: getGaSessionId() || data.gaSessionId || '',
      consentState: data.consentState || {},
      landingPage: data.landingPage || '',
      firstReferrer: data.referrer || ''
    });
  }

  trackPageView();

  // SPA navigation support
  var origPushState = history.pushState;
  if (origPushState) {
    history.pushState = function() {
      origPushState.apply(this, arguments);
      recordPageDuration();
      pageEntryTime = Date.now();
      trackPageView();
    };
    w.addEventListener('popstate', function() {
      recordPageDuration();
      pageEntryTime = Date.now();
      trackPageView();
    });
  }

  function recordPageDuration() {
    var last = pages[pages.length - 1];
    if (last) last.duration = Math.round((Date.now() - pageEntryTime) / 1000);
  }

  // ─── Form capture ────────────────────────────────────────────────────────

  function getFormName(form) {
    return form.getAttribute('data-wellgentic-form')
      || form.getAttribute('data-form-name')
      || form.getAttribute('name')
      || form.getAttribute('id')
      || form.className.split(' ')[0]
      || 'unnamed-form';
  }

  function extractFormData(form) {
    var result = {};
    var fields = form.querySelectorAll('input, select, textarea');
    for (var i = 0; i < fields.length; i++) {
      var el = fields[i];
      var name = (el.name || el.id || '').toLowerCase();
      var val = el.value || '';
      if (!name || !val) continue;
      if (el.type === 'password' || el.type === 'hidden' || el.type === 'submit') continue;

      if (name.match(/first.?name|fname/i)) result.firstName = val;
      else if (name.match(/last.?name|lname|surname/i)) result.lastName = val;
      else if (name.match(/email|e-mail/i) || el.type === 'email') result.email = val;
      else if (name.match(/phone|tel|mobile|cell/i) || el.type === 'tel') result.phone = val;
      else if (name.match(/^name$/i) && !result.firstName) {
        var parts = val.trim().split(/\s+/);
        result.firstName = parts[0];
        result.lastName = parts.slice(1).join(' ') || '';
      }
    }
    return result;
  }

  function isWellgenticForm(form) {
    return form.hasAttribute('data-wellgentic');
  }

  function isKnownFormPlugin(form) {
    var cls = form.className || '';
    var parent = form.parentElement;
    var parentCls = parent ? (parent.className || '') : '';
    return cls.indexOf('wpcf7-form') !== -1
      || cls.indexOf('wpforms-form') !== -1
      || cls.indexOf('gform_wrapper') !== -1
      || parentCls.indexOf('gform_wrapper') !== -1
      || cls.indexOf('elementor-form') !== -1
      || cls.indexOf('frm-show-form') !== -1
      || form.querySelector('.wpcf7-form-control') !== null;
  }

  function handleFormSubmit(form) {
    recordPageDuration();
    var fields = extractFormData(form);
    if (!fields.email && !fields.phone) return;

    var pagesWithDuration = pages.map(function(p) {
      return { url: p.url, title: p.title, duration: p.duration || 0 };
    });

    send('/capture', {
      firstName: fields.firstName || '',
      lastName: fields.lastName || '',
      email: fields.email || '',
      phone: fields.phone || '',
      formName: getFormName(form),
      pageUrl: w.location.href,
      referrer: data.referrer || d.referrer || '',
      utmSource: data.utmSource || '',
      utmMedium: data.utmMedium || '',
      utmCampaign: data.utmCampaign || '',
      utmContent: data.utmContent || '',
      utmTerm: data.utmTerm || '',
      utmId: data.utmId || '',
      utmSourcePlatform: data.utmSourcePlatform || '',
      gclid: data.gclid || '',
      gbraid: data.gbraid || '',
      wbraid: data.wbraid || '',
      fbclid: data.fbclid || '',
      fbc: data.fbc || '',
      fbp: data.fbp || '',
      gaClientId: getGaClientId() || data.gaClientId || '',
      gaSessionId: getGaSessionId() || data.gaSessionId || '',
      consentState: data.consentState || {},
      landingPage: data.landingPage || '',
      pagesViewed: pagesWithDuration,
      sessionDuration: Math.round((Date.now() - sessionStart) / 1000)
    });
  }

  d.addEventListener('submit', function(e) {
    var form = e.target;
    if (!form || form.tagName !== 'FORM') return;
    if (form.getAttribute('data-wg-ignore') === 'true') return;

    if (isWellgenticForm(form) || isKnownFormPlugin(form)) {
      handleFormSubmit(form);
      return;
    }

    var fields = extractFormData(form);
    if (fields.email || fields.phone) {
      handleFormSubmit(form);
    }
  }, true);

  // Contact Form 7 AJAX success
  d.addEventListener('wpcf7mailsent', function(e) {
    var form = e.target;
    if (form) handleFormSubmit(form);
  });

  // Gravity Forms AJAX confirmation
  if (w.jQuery) {
    try {
      w.jQuery(d).on('gform_confirmation_loaded', function(_e, formId) {
        var form = d.getElementById('gform_' + formId) || d.querySelector('.gform_wrapper #gform_' + formId);
        if (form) handleFormSubmit(form);
      });
    } catch(ex) {}
  }

  // ─── Session duration — send on unload ───────────────────────────────────

  function onUnload() {
    recordPageDuration();
    data.lastSeen = new Date().toISOString();
    saveTrackingData(data);
  }

  w.addEventListener('beforeunload', onUnload);
  d.addEventListener('visibilitychange', function() {
    if (d.visibilityState === 'hidden') onUnload();
  });

  // ─── Public API ──────────────────────────────────────────────────────────

  WG.getTrackingId = function() { return data.id; };
  WG.getAttribution = function() {
    return {
      utmSource: data.utmSource,
      utmMedium: data.utmMedium,
      utmCampaign: data.utmCampaign,
      utmContent: data.utmContent,
      utmTerm: data.utmTerm,
      utmId: data.utmId,
      utmSourcePlatform: data.utmSourcePlatform,
      gclid: data.gclid,
      gbraid: data.gbraid,
      wbraid: data.wbraid,
      fbclid: data.fbclid,
      fbc: data.fbc,
      fbp: data.fbp,
      gaClientId: getGaClientId() || data.gaClientId,
      gaSessionId: getGaSessionId() || data.gaSessionId,
      consentState: data.consentState,
      landingPage: data.landingPage,
      referrer: data.referrer
    };
  };
  WG.identify = function(fields) {
    send('/capture', {
      firstName: fields.firstName || '',
      lastName: fields.lastName || '',
      email: fields.email || '',
      phone: fields.phone || '',
      formName: fields.formName || 'api-identify',
      pageUrl: w.location.href,
      referrer: data.referrer || d.referrer || '',
      utmSource: data.utmSource || '',
      utmMedium: data.utmMedium || '',
      utmCampaign: data.utmCampaign || '',
      utmContent: data.utmContent || '',
      utmTerm: data.utmTerm || '',
      utmId: data.utmId || '',
      utmSourcePlatform: data.utmSourcePlatform || '',
      gclid: data.gclid || '',
      gbraid: data.gbraid || '',
      wbraid: data.wbraid || '',
      fbclid: data.fbclid || '',
      fbc: data.fbc || '',
      fbp: data.fbp || '',
      gaClientId: getGaClientId() || data.gaClientId || '',
      gaSessionId: getGaSessionId() || data.gaSessionId || '',
      consentState: data.consentState || {},
      landingPage: data.landingPage || '',
      pagesViewed: pages.map(function(p) {
        return { url: p.url, title: p.title, duration: p.duration || 0 };
      }),
      sessionDuration: Math.round((Date.now() - sessionStart) / 1000)
    });
  };
  WG.setConsent = function(consent) {
    w.__wgConsent = consent || {};
    data.consentState = normalizeConsent(consent, 'api');
    saveTrackingData(data);
  };

})(window, document, 'wg_trk_33fd34b9794482e2ab37a1fff32de468cf6a', 'https://api.wellgentic.ai/api/crm-tracking');
