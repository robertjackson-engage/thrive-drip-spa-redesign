import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../docs/assets/js/tracking.js',import.meta.url),'utf8');
function boot({search='',saved={},gpc=false}={}){
 const store=new Map(Object.entries(saved));const scripts=[];const listeners={};const handlers={};const forms=[{setAttribute(k,v){this[k]=v;}}];
 const document={readyState:'loading',referrer:'https://search.example/results',baseURI:'https://thrive-site.azurewebsites.net/',cookie:'',head:{append:s=>scripts.push(s)},querySelectorAll:s=>s==='form'?forms:[],addEventListener:(n,f)=>listeners[n]=f,createElement:()=>({dataset:{}})};
 const window={addEventListener:(n,f)=>handlers[n]=f,__wg_tracking:{getTrackingId:()=> 'visitor-123',getAttribution:()=>({fbc:'fb.1.10.old-click',gaClientId:'ga-client'})}};
 const context={window,document,location:{origin:'https://thrive-site.azurewebsites.net',pathname:'/',hostname:'thrive-site.azurewebsites.net',search},navigator:{globalPrivacyControl:gpc},URL,URLSearchParams,Date,localStorage:{getItem:k=>store.get(k),setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)}};
 vm.runInNewContext(code,context);return {window,scripts,store,forms,ready:listeners.DOMContentLoaded,handlers};
}
test('declined cookies: no scripts or identity handoff; current campaign still reaches booking',()=>{
 const h=boot({search:'?utm_source=google&gclid=secret',saved:{tds_privacy_v1:JSON.stringify({allowed:false})}});h.ready();
 assert.equal(h.scripts.length,0);const url=new URL(h.window.THRIVE_CRM.decorateBookingUrl('https://book.thrivedripspa.com/?loc=203322&gclid=old'));
 assert.equal(url.searchParams.get('loc'),'203322');assert.equal(url.searchParams.get('utm_source'),'google');assert.equal(url.searchParams.get('wg_consent'),'denied');assert.equal(url.searchParams.has('gclid'),false);assert.equal(url.searchParams.has('wg_uuid'),false);
 assert.equal(h.window.THRIVE_CRM.attribution().visitorKey,undefined);
});
test('accepted cookies load the supplied tracker once and preserve booking route + attribution',()=>{
 const h=boot({search:'?utm_source=google&utm_content=hero&gclid=new-click',saved:{tds_privacy_v1:JSON.stringify({allowed:true}),tds_attr:JSON.stringify({at:Date.now(),p:{fbclid:'old-click',utm_source:'meta'}})}});h.ready();h.ready();
 assert.equal(h.scripts.length,2);assert.equal(h.scripts[0].crossOrigin,'anonymous');assert.match(h.scripts[0].src,/wg_trk_33fd34b9794482e2ab37a1fff32de468cf6a$/);assert.equal(h.forms[0]['data-wg-ignore'],'true');
 const u=new URL(h.window.THRIVE_CRM.decorateBookingUrl('https://book.thrivedripspa.com/?offer=NEW&loc=203322'));
 assert.equal(u.searchParams.get('offer'),'NEW');assert.equal(u.searchParams.get('wg_uuid'),'visitor-123');assert.equal(u.searchParams.get('gclid'),'new-click');assert.equal(u.searchParams.has('fbclid'),false);
 assert.equal(h.window.THRIVE_CRM.attribution().utmContent,'hero');assert.equal(h.window.THRIVE_CRM.attribution().fbc,undefined);
 assert.equal(h.window.THRIVE_CRM.decorateBookingUrl('https://example.com/'),'https://example.com/');
});
test('browser privacy signal overrides a prior acceptance',()=>{
 const h=boot({gpc:true,saved:{tds_privacy_v1:JSON.stringify({allowed:true})}});h.ready();assert.equal(h.scripts.length,0);assert.equal(h.window.THRIVE_CRM.attribution().consentState.ads,'denied');
});
test('only confirmed new-visitor receipts produce a PII-free lead event',()=>{
 const h=boot({saved:{tds_privacy_v1:JSON.stringify({allowed:true})}});let n=h.window.dataLayer.length;
 h.handlers['wellgentic-chat:lead-received']({detail:{visitorType:'member',requestId:'member',workflowId:135}});assert.equal(h.window.dataLayer.length,n);
 h.handlers['wellgentic-chat:lead-received']({detail:{visitorType:'new',requestId:'receipt-1',workflowId:135,email:'never@example.test'}});
 assert.equal(h.window.dataLayer.at(-1).event_id,'receipt-1');assert.equal(JSON.stringify(h.window.dataLayer).includes('never@example.test'),false);
});
