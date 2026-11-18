import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../docs/assets/js/forms.js',import.meta.url),'utf8');
const spec=JSON.parse(readFileSync(new URL('../content/crm-forms.spec.json',import.meta.url),'utf8'));
const UUID4=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const EVENT_ID='wg_form_7_'+'a'.repeat(64);
const ATTRIBUTION={landingPage:'https://thrivedripspa.com/katy/',referrer:'https://www.google.com/',utmSource:'google',gclid:'click-1',visitorKey:'visitor-123',consentState:{analytics:'granted',ads:'granted',personalization:'denied'}};

// Just enough of a form for forms.js: named fields, a submit button, a status line, listeners.
function makeForm({kind='contact',slug='website-contact-form-abc123',id='contact-katy',name='Lounge contact form',phone='(346) 707-8703',values={},extra=[],statusInside=true}={}){
 const listeners={};const dispatched=[];const fields={};
 for(const [k,v] of Object.entries(values))fields[k]={name:k,value:v};
 const status={textContent:'',hidden:true,classes:new Set(),classList:{toggle(c,on){on?status.classes.add(c):status.classes.delete(c);},contains:c=>c==='form-status'||status.classes.has(c)}};
 const button={disabled:false};const attrs={};
 const selects=Object.values(fields).filter(f=>f.name==='location'||f.name==='interest').map(f=>({value:f.value,closest:()=>({classList:{toggle(){}}})}));
 const form={dataset:{crmForm:kind,formId:id,formName:name,phone,...(slug?{formSlug:slug}:{})},elements:fields,resets:0,button,status,dispatched,listeners,attrs,
  querySelector:s=>s==='button[type="submit"]'?button:s==='.form-status'?(statusInside?status:null):null,
  querySelectorAll:s=>s==='[data-label]'?extra.map(([label,value])=>({dataset:{label},value})):s==='.field select'?selects:[],
  nextElementSibling:statusInside?null:status,
  addEventListener:(n,f)=>{listeners[n]=f;},setAttribute:(k,v)=>{attrs[k]=v;},reportValidity:()=>true,
  reset(){this.resets++;for(const f of Object.values(fields))f.value='';},dispatchEvent:e=>{dispatched.push(e);return true;}};
 return form;
}
const PERSON={firstName:' Maria ',lastName:'Lopez',email:'maria@example.test',phone:'(713) 555-0100',location:'Katy',interest:'NAD+',message:'Do you take walk-ins?',company_website:''};
// Loads forms.js against the given forms. `respond` decides what the stubbed CRM answers.
function boot(forms,{respond=()=>({status:200,body:{success:true,eventId:EVENT_ID,clubNumber:'203033'}}),attribution=()=>ATTRIBUTION}={}){
 const calls=[];const pending=[];
 const fetch=(url,options)=>{calls.push({url,options,body:JSON.parse(options.body)});
  return new Promise((resolve,reject)=>{const settle=()=>{const r=respond(calls.length,options);if(r instanceof Error)return reject(r);resolve({ok:r.status>=200&&r.status<300,status:r.status,json:async()=>{if(r.body===undefined)throw new Error('not json');return r.body;}});};
   pending.push(settle);});};
 class CustomEvent{constructor(type,init){this.type=type;this.bubbles=!!init?.bubbles;this.detail=init?.detail;}}
 const context={window:{THRIVE_CRM:attribution?{attribution}:undefined},document:{readyState:'complete',querySelectorAll:s=>s==='form[data-crm-form]'?forms:[]},
  location:{origin:'https://thrivedripspa.com',pathname:'/katy/'},crypto:globalThis.crypto,fetch,CustomEvent,AbortController,setTimeout,clearTimeout,encodeURIComponent,JSON,Object,Uint8Array};
 vm.runInNewContext(code,context);
 const submit=form=>form.listeners.submit({preventDefault(){}});
 // Let the stubbed CRM answer every request made so far, then let forms.js finish handling it.
 const answer=async()=>{while(pending.length)pending.shift()();await new Promise(r=>setImmediate(r));};
 return {calls,submit,answer};
}
const successes=form=>form.dispatched.filter(e=>e.type==='thrive:form-success');

test('contact form: sends the answers and attribution, and only says "sent" after the CRM confirms',async()=>{
 const form=makeForm({values:{...PERSON}});const h=boot([form]);
 const done=h.submit(form);
 assert.equal(h.calls.length,1);assert.equal(form.button.disabled,true);assert.equal(form.attrs['aria-busy'],'true');
 assert.equal(form.status.textContent,'Sending…');assert.equal(form.status.classes.has('is-ok'),false);assert.equal(successes(form).length,0);assert.equal(form.resets,0);
 const call=h.calls[0];
 assert.equal(call.url,'https://api.wellgentic.ai/f/website-contact-form-abc123/submit');assert.equal(call.options.method,'POST');assert.equal(call.options.credentials,'omit');assert.equal(call.options.headers['Content-Type'],'application/json');
 const {_meta,...answers}=call.body;
 assert.deepEqual(answers,{firstName:'Maria',lastName:'Lopez',email:'maria@example.test',phone:'(713) 555-0100',location:'Katy',interest:'NAD+',message:'Do you take walk-ins?',formName:'Lounge contact form'});
 assert.match(_meta.requestId,UUID4);const {requestId,...sent}=_meta;assert.deepEqual(sent,ATTRIBUTION);
 await h.answer();await done;
 assert.equal(form.status.classes.has('is-ok'),true);assert.match(form.status.textContent,/your message is with our team/);assert.equal(form.status.hidden,false);
 assert.equal(form.resets,1);assert.equal(form.button.disabled,false);assert.equal(form.attrs['aria-busy'],'false');
});
test('form_submit hook fires once per confirmed receipt and carries no personal data',async()=>{
 const form=makeForm({values:{...PERSON}});const h=boot([form]);
 const done=h.submit(form);await h.answer();await done;
 assert.equal(successes(form).length,1);const event=successes(form)[0];
 assert.equal(event.bubbles,true);assert.deepEqual({...event.detail},{formId:'contact-katy',formName:'Lounge contact form'});
 assert.equal(/maria|lopez|555|example\.test|walk-ins/i.test(JSON.stringify(event.detail)),false);
});
test('a reply without the CRM receipt id is not a confirmation: error, lounge phone, details kept, no event',async()=>{
 for(const body of [{success:true},{success:true,eventId:''},{eventId:EVENT_ID},{},undefined]){
  const form=makeForm({values:{...PERSON}});const h=boot([form],{respond:()=>({status:200,body})});
  const done=h.submit(form);await h.answer();await done;
  assert.equal(form.status.classes.has('is-error'),true,JSON.stringify(body));assert.equal(form.status.classes.has('is-ok'),false);
  assert.match(form.status.textContent,/couldn’t send this.*\(346\) 707-8703 or 844-820-1713/);
  assert.equal(form.resets,0);assert.equal(form.elements.message.value,'Do you take walk-ins?');assert.equal(successes(form).length,0);assert.equal(form.button.disabled,false);
 }
});
test('server error, network failure and "form not found" all fail honestly',async()=>{
 for(const respond of [()=>({status:500,body:{error:'Server error'}}),()=>new TypeError('Failed to fetch'),()=>({status:404,body:{error:'Form not found'}}),()=>({status:429,body:{error:'Too many requests'}}),()=>Object.assign(new Error('aborted'),{name:'AbortError'})]){
  const form=makeForm({values:{...PERSON},phone:'844-820-1713'});const h=boot([form],{respond});
  const done=h.submit(form);await h.answer();await done;
  assert.equal(form.status.classes.has('is-error'),true);assert.match(form.status.textContent,/please try again, or call us on 844-820-1713\.$/);
  assert.equal(/Server error|Form not found|Too many/.test(form.status.textContent),false);
  assert.equal(form.resets,0);assert.equal(successes(form).length,0);assert.equal(form.button.disabled,false);
 }
});
test('a 400 shows the CRM\'s plain reason and keeps the details',async()=>{
 const form=makeForm({values:{...PERSON,phone:'12'}});const h=boot([form],{respond:()=>({status:400,body:{error:'Please enter a valid phone number.'}})});
 const done=h.submit(form);await h.answer();await done;
 assert.match(form.status.textContent,/^Please enter a valid phone number\. Your details are still here/);assert.equal(form.status.classes.has('is-error'),true);
 assert.equal(form.resets,0);assert.equal(successes(form).length,0);
});
test('an unchanged retry reuses its request id so the CRM cannot save it twice; an edit starts a new one',async()=>{
 const form=makeForm({values:{...PERSON}});let n=0;
 const h=boot([form],{respond:()=>++n<3?new TypeError('Failed to fetch'):{status:200,body:{success:true,eventId:EVENT_ID}}});
 let done=h.submit(form);await h.answer();await done;
 done=h.submit(form);await h.answer();await done;
 assert.equal(h.calls[0].body._meta.requestId,h.calls[1].body._meta.requestId);
 form.elements.message.value='Changed my question';form.listeners.input();
 done=h.submit(form);await h.answer();await done;
 assert.notEqual(h.calls[2].body._meta.requestId,h.calls[0].body._meta.requestId);assert.equal(h.calls[2].body.message,'Changed my question');
 assert.equal(successes(form).length,1);
 form.elements.email.value='second@example.test';form.elements.location.value='Katy';form.elements.firstName.value='A';form.elements.lastName.value='B';form.elements.phone.value='7135550101';
 done=h.submit(form);await h.answer();await done;
 assert.notEqual(h.calls[3].body._meta.requestId,h.calls[2].body._meta.requestId);
});
test('double submit: a second press while sending makes no second request',async()=>{
 const form=makeForm({values:{...PERSON}});const h=boot([form]);
 const first=h.submit(form);const second=h.submit(form);const third=h.submit(form);
 assert.equal(h.calls.length,1);await h.answer();await Promise.all([first,second,third]);
 assert.equal(h.calls.length,1);assert.equal(successes(form).length,1);assert.equal(form.resets,1);
});
test('honeypot: a filled trap sends nothing, fires nothing and never claims success',async()=>{
 const form=makeForm({values:{...PERSON,company_website:'http://spam.example'}});const h=boot([form]);
 const done=h.submit(form);await h.answer();await done;
 assert.equal(h.calls.length,0);assert.equal(successes(form).length,0);assert.equal(form.resets,0);
 assert.equal(form.status.classes.has('is-ok'),false);assert.equal(form.status.classes.has('is-error'),true);
});
test('a form with no CRM form connected tells the visitor to call instead of pretending',async()=>{
 const form=makeForm({slug:'',values:{...PERSON}});const h=boot([form]);
 const done=h.submit(form);await h.answer();await done;
 assert.equal(h.calls.length,0);assert.equal(successes(form).length,0);assert.equal(form.resets,0);
 assert.equal(form.elements.message.value,'Do you take walk-ins?');assert.match(form.status.textContent,/^Online messages are not switched on yet\. Please call us on \(346\) 707-8703 or 844-820-1713\.$/);assert.equal(form.status.classes.has('is-error'),true);
});
test('newsletter: email plus the email opt-in the visitor asked for, and nothing about texts',async()=>{
 const form=makeForm({kind:'newsletter',slug:'website-newsletter-signup-def456',id:'newsletter',name:'Newsletter signup',phone:'844-820-1713',values:{email:'reader@example.test',company_website:''},statusInside:false});
 const h=boot([form]);const done=h.submit(form);await h.answer();await done;
 const {_meta,...answers}=h.calls[0].body;
 assert.equal(h.calls[0].url,'https://api.wellgentic.ai/f/website-newsletter-signup-def456/submit');
 assert.deepEqual(answers,{email:'reader@example.test',emailConsent:'yes'});assert.match(_meta.requestId,UUID4);
 assert.match(form.status.textContent,/You’re on the list/);assert.deepEqual({...successes(form)[0].detail},{formId:'newsletter',formName:'Newsletter signup'});
});
test('franchise enquiry: its own fields, no lounge',async()=>{
 const form=makeForm({kind:'franchise',slug:'website-franchise-enquiry-0a1b2c',id:'franchise-form',name:'Franchise enquiry',phone:'844-820-1713',values:{firstName:'Sam',lastName:'Reed',email:'sam@example.test',phone:'2145550100',interest:'I\'m an investor',city:'Austin, TX',message:'',company_website:''}});
 const h=boot([form]);const done=h.submit(form);await h.answer();await done;
 const {_meta,...answers}=h.calls[0].body;
 assert.deepEqual(answers,{firstName:'Sam',lastName:'Reed',email:'sam@example.test',phone:'2145550100',background:'I\'m an investor',city:'Austin, TX'});
 assert.match(form.status.textContent,/franchise team/);
});
test('mobile IV request: address and time travel inside the message, labelled',async()=>{
 const form=makeForm({id:'mobile-request',name:'Mobile IV request',phone:'844-820-1713',values:{...PERSON,location:'Mobile / Concierge',interest:'Group / party (2–6)',message:'Six of us'},extra:[['Address','The Woodlands'],['Date and time','Sat 2pm'],['Unused','  ']]});
 const h=boot([form]);const done=h.submit(form);await h.answer();await done;
 assert.equal(h.calls[0].body.message,'Address: The Woodlands\nDate and time: Sat 2pm\nSix of us');assert.equal(h.calls[0].body.location,'Mobile / Concierge');assert.equal(h.calls[0].body.formName,'Mobile IV request');
});
test('no form ever sends a text-message or email opt-in on the visitor\'s behalf, except the newsletter\'s own email opt-in',async()=>{
 const forms=[makeForm({values:{...PERSON}}),makeForm({kind:'franchise',values:{...PERSON,city:'Austin'}}),makeForm({kind:'newsletter',values:{email:'reader@example.test'},statusInside:false})];
 const h=boot(forms);const done=forms.map(h.submit);await h.answer();await Promise.all(done);
 assert.equal(h.calls.length,3);
 for(const call of h.calls)for(const key of Object.keys(call.body))assert.equal(/sms|text|optin|voice/i.test(key),false,key);
 assert.deepEqual(h.calls.map(c=>'emailConsent' in c.body),[false,false,true]);assert.equal(h.calls[2].body.emailConsent,'yes');
});
test('without the tracking script the form still sends, with a denied-consent attribution record',async()=>{
 const form=makeForm({values:{...PERSON}});const h=boot([form],{attribution:null});
 const done=h.submit(form);await h.answer();await done;
 const {requestId,...meta}=h.calls[0].body._meta;
 assert.deepEqual(meta,{landingPage:'https://thrivedripspa.com/katy/',consentState:{analytics:'denied',ads:'denied',personalization:'denied'}});assert.equal(successes(form).length,1);
});

// ----- the CRM form definitions the owner creates must match what the site sends -----
const sentKeys=async(kind,values,extra=[])=>{const form=makeForm({kind,values,extra,statusInside:kind!=='newsletter'});const h=boot([form]);const done=h.submit(form);await h.answer();await done;return Object.keys(h.calls[0].body).filter(k=>k!=='_meta');};
test('every key the site sends is a field of the matching CRM form, and every required CRM field is sent',async()=>{
 const full={...PERSON,city:'Austin'};
 for(const [kind,values] of [['contact',full],['franchise',full],['newsletter',{email:'reader@example.test'}]]){
  const keys=await sentKeys(kind,values);const fields=spec[kind].fields;
  assert.deepEqual(keys.filter(k=>!fields.some(f=>f.key===k)),[],kind+' sends a key the CRM form does not have');
  assert.deepEqual(fields.filter(f=>f.required&&!keys.includes(f.key)).map(f=>f.key),[],kind+' misses a required CRM field');
 }
});
test('CRM form definitions respect the CRM\'s own limits and consent rules',()=>{
 for(const kind of ['contact','franchise','newsletter']){
  const {fields,settings}=spec[kind];
  assert.ok(fields.length<=8,kind+' has more than 8 fields');
  for(const f of fields)assert.match(f.key,/^[a-zA-Z][a-zA-Z0-9_]{0,49}$/);
  assert.ok(fields.some(f=>f.type==='email'||f.type==='phone'));
  assert.equal(settings.website.version,1);assert.equal(settings.website.smsConsentField,undefined,kind+' must not record text consent: the site has no text-consent checkbox');
  assert.equal(JSON.stringify(spec[kind]).toLowerCase().includes('aivoiceconsent'),false);
 }
 assert.equal(spec.contact.settings.website.purpose,'lead');assert.equal(spec.franchise.settings.website.purpose,'service_request');assert.equal(spec.newsletter.settings.website.purpose,'newsletter');
 assert.equal(spec.contact.settings.website.emailConsentField,undefined);assert.equal(spec.franchise.settings.website.emailConsentField,undefined);
 const consent=spec.newsletter.fields.find(f=>f.key===spec.newsletter.settings.website.emailConsentField);assert.equal(consent.type,'checkbox');assert.equal(consent.required,true);
 const build=readFileSync(new URL('../build.py',import.meta.url),'utf8');
 assert.ok(build.includes(`NEWSLETTER_CONSENT = ${JSON.stringify(consent.label)}`),'the consent wording on the site must be the wording saved in the CRM');
});
test('the lounge list in the CRM contact form matches the lounges in build.py, each with its own location number',()=>{
 const build=readFileSync(new URL('../build.py',import.meta.url),'utf8');const block=build.slice(build.indexOf('LOCATIONS = ['),build.indexOf('LOC_BY'));
 const lounges=Object.fromEntries([...block.matchAll(/dict\(slug="[^"]+", label="([^"]+)"[\s\S]*?meevo="(\d+)"/g)].map(m=>[m[1],m[2]]));
 const mobile=build.match(/MOBILE_OPTION = "([^"]+)"/)[1];const mobileClub=build.match(/MOBILE_CLUB = "(\d+)"/)[1];
 const expected={...lounges,[mobile]:mobileClub};
 assert.equal(Object.keys(lounges).length,10);
 const location=spec.contact.fields.find(f=>f.key===spec.contact.settings.website.locationField);
 assert.deepEqual(location.options,Object.keys(expected));assert.deepEqual(spec.contact.settings.website.locations,expected);
 assert.equal(new Set(Object.values(expected)).size,11,'two lounges share a location number');
});
