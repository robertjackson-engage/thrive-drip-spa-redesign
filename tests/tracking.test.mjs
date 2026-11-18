import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../docs/assets/js/tracking.js',import.meta.url),'utf8');
function boot({search='',saved={},gpc=false,dnt,path='/'}={}){
 const store=new Map(Object.entries(saved));const appended=[];let reloads=0;
 // Just enough of an element for the cookie notice: children are created on first querySelector.
 const el=()=>{const kids={};const texts=[];return {dataset:{},texts,kids,setAttribute(){},append(t){texts.push(t);},remove(){this.removed=true;},querySelector(sel){return kids[sel]&&kids[sel].removed?null:(kids[sel]=kids[sel]||el());}};};const scripts=[];const listeners={};const handlers={};const forms=[{setAttribute(k,v){this[k]=v;}}];
 const document={currentScript:{src:'https://thrive-site.azurewebsites.net/assets/js/tracking.js'},readyState:'loading',referrer:'https://search.example/results',baseURI:'https://thrive-site.azurewebsites.net/',cookie:'',head:{append:s=>scripts.push(s)},querySelectorAll:s=>s==='form'?forms:[],addEventListener:(n,f)=>listeners[n]=f,createElement:()=>el(),getElementById:id=>appended.find(e=>e.id===id&&!e.removed)||null,body:{append:e=>appended.push(e)}};
 const window={addEventListener:(n,f)=>handlers[n]=f,__wg_tracking:{setConsent(c){this.consent=c;},getTrackingId:()=> 'visitor-123',getAttribution:()=>({fbc:'fb.1.10.old-click',gaClientId:'ga-client'})}};
 const context={window,document,location:{origin:'https://thrive-site.azurewebsites.net',pathname:path,hostname:'thrive-site.azurewebsites.net',search,reload:()=>{reloads++;}},navigator:{globalPrivacyControl:gpc,doNotTrack:dnt},URL,URLSearchParams,Date,localStorage:{getItem:k=>store.get(k),setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)}};
 vm.runInNewContext(code,context);return {window,document,scripts,store,forms,listeners,ready:listeners.DOMContentLoaded,handlers,notice:()=>document.getElementById('thrive-cookie-notice'),reloads:()=>reloads};
}
const events=(h,name)=>h.window.dataLayer.filter(e=>e&&e.event===name);
const consentDefault=h=>{const c=h.window.dataLayer.find(e=>e[0]==='consent'&&e[1]==='default');return c&&c[2];};
// A link as the click handler sees it: `inside` lists the selectors that closest() should match.
const link=(h,href,{text='',inside=['main'],shadow=false}={})=>({tagName:'A',href,textContent:text,getRootNode:()=>shadow?{}:h.document,closest:sel=>sel.split(',').some(s=>inside.includes(s.trim()))?{}:null});
const click=(h,a,type='click',button=0)=>h.listeners[type]({type,button,composedPath:()=>[{tagName:'SPAN'},a]});
test('declined cookies: no scripts or identity handoff; current campaign still reaches booking',()=>{
 const h=boot({search:'?utm_source=google&gclid=secret',saved:{tds_privacy_v1:JSON.stringify({allowed:false})}});h.ready();
 assert.equal(h.scripts.length,0);const url=new URL(h.window.THRIVE_CRM.decorateBookingUrl('https://book.thrivedripspa.com/?loc=203322&gclid=old'));
 assert.equal(url.searchParams.get('loc'),'203322');assert.equal(url.searchParams.get('utm_source'),'google');assert.equal(url.searchParams.get('wg_consent'),'denied');assert.equal(url.searchParams.has('gclid'),false);assert.equal(url.searchParams.has('wg_uuid'),false);
 assert.equal(h.window.THRIVE_CRM.attribution().visitorKey,undefined);
});
test('accepted cookies load the supplied tracker once and preserve booking route + attribution',()=>{
 const h=boot({search:'?utm_source=google&utm_content=hero&gclid=new-click',saved:{tds_privacy_v1:JSON.stringify({allowed:true}),tds_attr:JSON.stringify({at:Date.now(),p:{fbclid:'old-click',utm_source:'meta'}})}});h.ready();h.ready();
 assert.equal(h.scripts.length,2);assert.equal(h.scripts[0].crossOrigin,'anonymous');assert.match(h.scripts[0].dataset.source,/wg_trk_33fd34b9794482e2ab37a1fff32de468cf6a$/);assert.match(h.scripts[0].src,/wellgentic-tracking.js/);assert.equal(h.forms[0]['data-wg-ignore'],'true');
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
 h.handlers['wellgentic-chat:lead-received']({detail:{visitorType:'member',requestId:'member',workflowId:135}});assert.equal(h.window.dataLayer.length,n+1);assert.equal(h.window.dataLayer.at(-1).event,'form_submit');assert.equal(events(h,'wellgentic_chat_lead').length,0);
 h.handlers['wellgentic-chat:lead-received']({detail:{visitorType:'new',requestId:'receipt-1',workflowId:135,email:'never@example.test'}});
 assert.equal(h.window.dataLayer.at(-1).event_id,'receipt-1');assert.equal(JSON.stringify(h.window.dataLayer).includes('never@example.test'),false);
});

test('no stored choice: tracking is on by default, consent mode is granted and booking carries the handoff',()=>{
 const h=boot({search:'?utm_source=google&gclid=click-1'});h.ready();
 assert.equal(h.scripts.length,2);assert.match(h.scripts[1].src,/gtm\.js\?id=GTM-WCDPC5KK$/);
 assert.deepEqual({...consentDefault(h)},{analytics_storage:'granted',ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted',functionality_storage:'granted',security_storage:'granted'});
 assert.equal(h.window.__wgConsent.analytics,'granted');
 const u=new URL(h.window.THRIVE_CRM.decorateBookingUrl('https://book.thrivedripspa.com/?loc=203322'));
 assert.equal(u.searchParams.get('wg_consent'),'granted');assert.equal(u.searchParams.get('gclid'),'click-1');assert.equal(u.searchParams.get('utm_source'),'google');assert.equal(u.searchParams.get('wg_uuid'),'visitor-123');assert.equal(u.searchParams.get('loc'),'203322');
});
test('a stored decline keeps consent mode denied and pushes no site events',()=>{
 const h=boot({path:'/fort-worth.html',saved:{tds_privacy_v1:JSON.stringify({allowed:false})}});h.ready();
 assert.equal(consentDefault(h).analytics_storage,'denied');assert.equal(consentDefault(h).ad_storage,'denied');
 const n=h.window.dataLayer.length;const a=link(h,'https://book.thrivedripspa.com/?loc=203322',{text:'Book Fort Worth'});
 click(h,a);click(h,link(h,'tel:6827473747'));click(h,link(h,'mailto:someone@example.test'));
 h.listeners['thrive:form-success']({detail:{formId:'contact'}});h.handlers['wellgentic-chat:lead-received']({detail:{visitorType:'new',requestId:'r',workflowId:135}});
 assert.equal(h.window.dataLayer.length,n);assert.equal(new URL(a.href).searchParams.get('wg_consent'),'denied');
});
test('Do Not Track and Global Privacy Control both count as declined without a stored choice',()=>{
 for(const signal of [{dnt:'1'},{gpc:true}]){const h=boot(signal);h.ready();assert.equal(h.scripts.length,0);assert.equal(consentDefault(h).analytics_storage,'denied');
  assert.equal(new URL(h.window.THRIVE_CRM.decorateBookingUrl('https://book.thrivedripspa.com/')).searchParams.get('wg_consent'),'denied');
  click(h,link(h,'tel:6827473747'));assert.equal(events(h,'click_to_call').length,0);}
});
test('booking_click: decorated link, clean parameters, lounge from the link or the page',()=>{
 const h=boot({path:'/book.html',search:'?gclid=click-2'});h.ready();
 const a=link(h,'https://book.thrivedripspa.com/?loc=203322',{text:'  Book\n Fort Worth  →',inside:['main']});click(h,a);
 assert.equal(new URL(a.href).searchParams.get('wg_consent'),'granted');assert.equal(new URL(a.href).searchParams.get('gclid'),'click-2');
 assert.deepEqual({...events(h,'booking_click')[0]},{event:'booking_click',link_url:'https://book.thrivedripspa.com/',link_text:'Book Fort Worth',lounge:'fort-worth',cta_position:'body'});
 click(h,link(h,'https://na1.meevo.com/customerportal/advanced/ob?tenantId=200296&locationId=203033',{text:'x'.repeat(200),inside:['.hero','main']}));
 const meevo=events(h,'booking_click')[1];assert.equal(meevo.link_url,'https://na1.meevo.com/customerportal/advanced/ob');assert.equal(meevo.lounge,'katy');assert.equal(meevo.cta_position,'hero');assert.equal(meevo.link_text.length,80);
 click(h,link(h,'https://book.thrivedripspa.com/?path=new',{text:'Call 713-955-3747 or book',inside:['footer']}));
 const plain=events(h,'booking_click')[2];assert.equal(plain.lounge,undefined);assert.equal('lounge' in plain,true);assert.equal(plain.link_text,undefined);assert.equal(plain.cta_position,'footer');
 click(h,link(h,'https://book.thrivedripspa.com/',{text:'Book',shadow:true}));assert.equal(events(h,'booking_click')[3].cta_position,'chat');
 for(const other of ['https://na1.meevo.com/EgiftApp/location/search?tenantId=200296','https://example.com/?loc=203322','https://thrive-site.azurewebsites.net/book.html','https://notmeevo.com/customerportal/x'])click(h,link(h,other,{text:'Other'}));
 assert.equal(events(h,'booking_click').length,4);assert.equal(JSON.stringify(h.window.dataLayer).includes('click-2'),false);assert.equal(JSON.stringify(h.window.dataLayer).includes('visitor-123'),false);
});
test('booking_click falls back to the location page slug; middle click counts, right click does not',()=>{
 const h=boot({path:'/highland-park/'});h.ready();
 click(h,link(h,'https://book.thrivedripspa.com/',{text:'Book'}),'auxclick',1);click(h,link(h,'https://book.thrivedripspa.com/',{text:'Book'}),'auxclick',2);
 assert.equal(events(h,'booking_click').length,1);assert.equal(events(h,'booking_click')[0].lounge,'highland-park');
});
test('click_to_call and contact_link_click never carry the number or the address',()=>{
 const h=boot({path:'/fort-worth.html'});h.ready();
 click(h,link(h,'tel:6827473747',{text:'(682) 747-3747',inside:['.hero','main']}));click(h,link(h,'mailto:admin_ftw@thrivedripspa.com',{text:'admin_ftw@thrivedripspa.com'}));
 assert.deepEqual({...events(h,'click_to_call')[0]},{event:'click_to_call',lounge:'fort-worth',cta_position:'hero'});
 assert.deepEqual({...events(h,'contact_link_click')[0]},{event:'contact_link_click',link_type:'email',lounge:'fort-worth',cta_position:'body'});
 const pushed=JSON.stringify(h.window.dataLayer);assert.equal(/6827473747|747-3747|admin_ftw|@/.test(pushed),false);
 const home=boot();home.ready();click(home,link(home,'tel:+18448201713',{inside:['header, .menu-overlay','header']}));
 assert.equal(events(home,'click_to_call')[0].lounge,undefined);assert.equal(events(home,'click_to_call')[0].cta_position,'header');
});
test('form_submit fires once per confirmed form success and keeps the chat lead event unchanged',()=>{
 const h=boot();h.ready();
 h.listeners['thrive:form-success']({detail:{formId:'contact',formName:'Contact form',email:'never@example.test'}});
 assert.deepEqual({...events(h,'form_submit')[0]},{event:'form_submit',form_id:'contact',form_name:'Contact form'});
 h.handlers['wellgentic-chat:lead-received']({detail:{visitorType:'new',requestId:'receipt-9',workflowId:135}});
 assert.deepEqual({...events(h,'form_submit')[1]},{event:'form_submit',form_id:'concierge-contact',form_name:'Concierge chat contact form'});
 assert.deepEqual({...events(h,'wellgentic_chat_lead')[0]},{event:'wellgentic_chat_lead',event_id:'receipt-9',form_source:'chatbot',agent_id:'135'});
 assert.equal(events(h,'form_submit').length,2);assert.equal(JSON.stringify(h.window.dataLayer).includes('never@example.test'),false);
});
test('the lounge map in tracking.js matches the lounges in build.py',()=>{
 const build=readFileSync(new URL('../build.py',import.meta.url),'utf8');const block=build.slice(build.indexOf('LOCATIONS = ['),build.indexOf('def book_url')>0?build.indexOf('def book_url'):undefined);
 const expected=Object.fromEntries([...block.matchAll(/dict\(slug="([^"]+)"[\s\S]*?meevo="(\d+)"/g)].map(m=>[m[2],m[1]]));
 const actual=Object.fromEntries([...code.match(/const LOUNGES = \{([^}]+)\}/)[1].matchAll(/(\d+):'([^']+)'/g)].map(m=>[m[1],m[2]]));
 assert.equal(Object.keys(expected).length,10);assert.deepEqual(actual,expected);
});

test('the notice offers OK and Decline; OK records the choice without interrupting tracking',()=>{
 const h=boot();h.ready();const notice=h.notice();assert.ok(notice);assert.match(notice.innerHTML,/data-choice="deny">Decline<.*data-choice="allow">OK</);assert.match(notice.kids.a.href,/\/privacy\.html$/);
 notice.kids['[data-choice="allow"]'].onclick();
 assert.equal(JSON.parse(h.store.get('tds_privacy_v1')).allowed,true);assert.equal(h.notice(),null);assert.equal(h.reloads(),0);assert.equal(h.scripts.length,2);
});
test('Decline stores the choice, turns consent off, clears attribution and reloads',()=>{
 const h=boot({search:'?gclid=click-3',saved:{wg_uuid:'gtm-visitor',wg_gclid:'gtm-click',wg_utm_source:'google'}});h.ready();assert.ok(h.store.has('tds_attr'));
 const cleared=[];Object.defineProperty(h.document,'cookie',{get:()=>'',set:v=>cleared.push(v.split('=')[0])});
 h.notice().kids['[data-choice="deny"]'].onclick();
 assert.equal(JSON.parse(h.store.get('tds_privacy_v1')).allowed,false);assert.equal(h.store.has('tds_attr'),false);assert.equal(h.reloads(),1);
 assert.deepEqual([...h.store.keys()],['tds_privacy_v1']);for(const name of ['_ga','_ga_XN01L3VWSH','_wg_track','wg_uuid','_fbp','_fbc'])assert.ok(cleared.includes(name),name);
 const update=h.window.dataLayer.filter(e=>e[0]==='consent'&&e[1]==='update').at(-1)[2];assert.equal(update.analytics_storage,'denied');assert.equal(update.ad_storage,'denied');
 assert.equal(h.window.__wgConsent.analytics,'denied');click(h,link(h,'tel:6827473747'));assert.equal(events(h,'click_to_call').length,0);
 assert.equal(new URL(h.window.THRIVE_CRM.decorateBookingUrl('https://book.thrivedripspa.com/')).searchParams.get('wg_consent'),'denied');
});
test('a visitor who already chose is not shown the notice again, and can reopen it to change their mind',()=>{
 const h=boot({saved:{tds_privacy_v1:JSON.stringify({allowed:false})}});const reopen={addEventListener(n,f){this[n]=f;}};h.document.querySelectorAll=s=>s==='[data-cookie-preferences]'?[reopen]:[];h.ready();
 assert.equal(h.notice(),null);assert.equal(h.scripts.length,0);reopen.click();assert.ok(h.notice());assert.deepEqual(h.notice().kids.p.texts,[' Currently declined.']);
 h.notice().kids['[data-choice="allow"]'].onclick();assert.equal(h.scripts.length,2);assert.equal(h.reloads(),0);assert.equal(h.window.dataLayer.filter(e=>e[0]==='consent'&&e[1]==='update').at(-1)[2].analytics_storage,'granted');
});
