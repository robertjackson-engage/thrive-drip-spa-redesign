import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../docs/assets/js/wellgentic-tracking.js',import.meta.url),'utf8');
function boot(analytics='granted') {
 const calls=[];const events={};const jar=new Map();
 const document={title:'Thrive',referrer:'',addEventListener:(n,f)=>events[n]=f};
 Object.defineProperty(document,'cookie',{get:()=>[...jar].map(([k,v])=>`${k}=${v}`).join('; '),set:s=>{let [name,...val]=s.split(';')[0].split('=');jar.set(name,val.join('='));}});
 const window={location:new URL('https://thrive-site.azurewebsites.net/?utm_source=google&utm_campaign=transport'),__wgConsent:{analytics,ads:analytics},addEventListener(){},fetch:(url,options)=>{calls.push({url,options});return Promise.resolve({ok:true});}};
 vm.runInNewContext(code,{window,document,navigator:{sendBeacon(){throw Error('Beacon must not be used');}},history:{pushState(){}},URLSearchParams,Date,Math,JSON,decodeURIComponent,encodeURIComponent});
 return {window,calls,jar,events};
}
test('page view uses a credentialless request with the exact tracking key and cookie identity',()=>{
 const h=boot();assert.equal(h.calls.length,1);const call=h.calls[0];assert.equal(call.url,'https://api.wellgentic.ai/api/crm-tracking/pageview');assert.equal(call.options.credentials,'omit');assert.equal(call.options.keepalive,true);
 const body=JSON.parse(call.options.body);assert.equal(body.apiKey,'wg_trk_33fd34b9794482e2ab37a1fff32de468cf6a');assert.equal(body.trackingId,h.window.__wg_tracking.getTrackingId());assert.equal(body.utmCampaign,'transport');assert.equal(body.consentState.analytics,'granted');assert.ok(h.jar.has('_wg_track'));
});
test('denied analytics sends no request',()=>{assert.equal(boot('denied').calls.length,0);});
test('a form with its own CRM submit handler cannot create a duplicate generic capture',()=>{const h=boot();h.events.submit({target:{tagName:'FORM',getAttribute:k=>k==='data-wg-ignore'?'true':null}});assert.equal(h.calls.length,1);});
