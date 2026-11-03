/* ThrIVe Concierge. Forma CRM client with Thrive Clear Water presentation.
   Keep request recovery, session isolation, consent capture and team handoff aligned with crm-website-chat.js. */
(() => {
  "use strict";
  const script = document.currentScript;
  const workflowId = script?.getAttribute("data-agent-id");
  const apiKey = script?.getAttribute("data-website-key");
  if (!script || !/^[1-9]\d*$/.test(workflowId || "") || !apiKey) return;
  const base = "https://api.wellgentic.ai";
  const identity = `${base}:${workflowId}`;
  if (
    [...document.querySelectorAll("[data-wellgentic-chat]")].some(
      (node) => node.getAttribute("data-wellgentic-chat") === identity,
    )
  )
    return;
  const host = document.createElement("div");
  host.setAttribute("data-wellgentic-chat", identity);
  const shadow = host.attachShadow({ mode: "open" });
  // Static markup only. Website configuration, visitor input and replies are
  // always assigned through textContent/value, never interpreted as markup.
  shadow.innerHTML = `<style>
    :host{--accent:#059669;--on-accent:#fff;all:initial;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#17232c;font-size:14px;line-height:1.5}
    *{box-sizing:border-box}button,input,textarea,select{font:inherit}button{cursor:pointer}button:disabled{cursor:default;opacity:.55}button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid #34d399;outline-offset:3px}[hidden]{display:none!important}
    .launcher{position:fixed;right:24px;bottom:24px;z-index:2147483000;border:0;border-radius:999px;background:var(--accent);color:var(--on-accent);padding:16px 22px;box-shadow:0 8px 32px #102a2a30;font-weight:600}
    .panel{position:fixed;right:24px;bottom:94px;z-index:2147483000;width:380px;max-width:calc(100vw - 24px);height:560px;max-height:calc(100vh - 120px);max-height:calc(100dvh - 120px);display:flex;flex-direction:column;border:1px solid #dbe6e3;border-radius:20px;background:#fff;box-shadow:0 18px 70px #0e2c3226;overflow:hidden}
    .top{display:flex;align-items:center;gap:12px;padding:20px;background:var(--accent);color:var(--on-accent)}.mark{font-size:24px}.heading{flex:1;min-width:0}.title{margin:0;font-weight:650;font-size:17px;overflow-wrap:anywhere}.subtitle{margin-top:3px;font-size:12px;opacity:.9}.close{border:0;background:transparent;color:inherit;font-size:24px;line-height:1;padding:6px;border-radius:8px}
    .location{padding:14px 18px;border-bottom:1px solid #e8eeec}.location label{display:block;font-size:12px;font-weight:600;margin-bottom:5px}select{width:100%;border:1px solid #dbe6e3;border-radius:9px;padding:9px;background:#fff;color:#17232c}.history{flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:20px 18px;display:flex;flex-direction:column;gap:12px;background:#fbfdfc}.bubble{flex-shrink:0;padding:12px 14px;border-radius:14px;white-space:pre-wrap;overflow-wrap:anywhere;max-width:90%;background:#edf3f0;align-self:flex-start}.bubble.user{align-self:flex-end;background:var(--accent);color:var(--on-accent)}.status{font-size:12px;color:#58675f;padding:0 18px 8px}.error{color:#a12b20}.retry{margin-left:6px;color:inherit;background:none;border:0;text-decoration:underline}.composer{border-top:1px solid #e8eeec;padding:14px}.form{display:flex;align-items:flex-end;gap:10px}textarea{min-width:0;flex:1;resize:none;min-height:44px;max-height:150px;border:1px solid #dbe6e3;background:#fff;border-radius:12px;padding:11px 12px;line-height:1.5;color:#17232c;overflow-wrap:anywhere;white-space:pre-wrap}.send{width:42px;height:42px;flex:none;border:0;border-radius:12px;background:var(--accent);color:var(--on-accent);font-size:20px}.footer{display:flex;justify-content:space-between;gap:8px;margin-top:10px;font-size:11px;color:#7a8881}.reset{border:0;background:none;padding:0;font-size:11px;color:#58675f}
    :host([data-side="left"]) .panel,:host([data-side="left"]) .launcher{left:24px;right:auto}
    .contact-invite{border:0;background:none;color:#23674f;padding:0 0 12px;font-size:12px;font-weight:600;text-align:left}.panel.capture-mode{height:700px}.lead-form{flex:1;display:flex;flex-direction:column;min-height:0}.lead-fields{flex:1;overflow:auto;padding:18px 20px;overscroll-behavior:contain}.lead-back{border:0;background:none;color:#52675b;padding:0;font-size:12px}.lead-fields h3{font-size:20px;margin:16px 0 6px;letter-spacing:-.3px}.lead-intro{font-size:13px;color:#58675f;margin:0 0 18px}.lead-name{display:grid;grid-template-columns:1fr 1fr;gap:12px}.lead-field{display:block;margin-bottom:14px;font-size:12px;font-weight:600}.lead-field input{display:block;width:100%;min-width:0;margin-top:5px;border:1px solid #dbe6e3;border-radius:9px;padding:10px;color:#17232c;background:#fff;font-size:16px;font-weight:400}.lead-field input:read-only{background:#f4f7f5}.lead-hint{font-size:12px;color:#58675f;margin:-3px 0 17px}.lead-permissions{border:1px solid #e1eae5;border-radius:12px;padding:12px;background:#fbfdfc}.lead-permissions legend{font-size:12px;font-weight:600;padding:0 4px}.lead-check{display:flex;align-items:flex-start;gap:9px;font-size:12px;margin:5px 0}.lead-check input{flex:none;accent-color:var(--accent);margin:3px 0;width:16px;height:16px}.sms-notice{font-size:11px;color:#58675f;margin:4px 0 12px 25px}.lead-actions{flex:none;border-top:1px solid #e8eeec;padding:14px 20px}.lead-submit{width:100%;border:0;border-radius:10px;background:var(--accent);color:var(--on-accent);padding:12px;font-weight:600}.lead-status{font-size:12px;color:#58675f;margin:10px 0 0;overflow-wrap:anywhere}.lead-status.error{color:#a12b20}
    @media(max-width:480px){.panel{right:12px;bottom:84px;width:calc(100vw - 24px)}.launcher{right:16px;bottom:16px}:host([data-side="left"]) .panel{left:12px}:host([data-side="left"]) .launcher{left:16px}}
    .lead-heading{flex:none;padding:14px 20px 12px;border-bottom:1px solid #e8eeec}.lead-heading h3{font-size:18px;letter-spacing:-.3px;margin:8px 0 0}

    /* Original ThrIVe Concierge proportions, type and colors. */
    :host{font-family:var(--font-body,"Montserrat","Helvetica Neue",sans-serif);color:#f4f7f8;--accent:#08d6dd;--on-accent:#04201f}
    button{border:0}button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline-color:var(--accent)}
    .launcher{right:clamp(18px,3vw,36px);bottom:clamp(18px,3vw,36px);width:64px;height:64px;padding:0;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 40px #08d6dd44;transition:transform .3s}
    .launcher svg{width:30px;height:30px}.launcher:hover{transform:translateY(-4px)}
    .panel{right:clamp(12px,2vw,32px);bottom:clamp(12px,2vw,32px);width:min(420px,calc(100vw - 24px));height:min(640px,calc(100dvh - 60px));max-height:calc(100dvh - 24px);border-radius:0;background:#0e1013;border:1px solid #f4f7f824;box-shadow:0 30px 90px #0009}
    .top{padding:16px 18px;background:#060709;color:#f4f7f8;border-bottom:1px solid #f4f7f824}
    .mark{width:34px;height:34px;border-radius:50%;background:var(--accent);color:var(--on-accent);display:flex;align-items:center;justify-content:center;flex:none}.mark svg{width:18px;height:18px}
    .title{font-family:var(--font-display,"Anton","Arial Narrow",sans-serif);font-size:17px;line-height:1.1;text-transform:uppercase;font-weight:400}.subtitle{font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;color:#f4f7f899}
    .close{width:34px;height:34px;border:1px solid #f4f7f824;border-radius:50%;font-size:18px}.close:hover{background:var(--accent);color:var(--on-accent)}
    .history{background:#0e1013;gap:14px;scrollbar-width:thin}.bubble{max-width:88%;font-size:14px;line-height:1.55;padding:12px 15px;border:1px solid #f4f7f824;background:#181b1f;border-radius:16px 16px 16px 4px;color:#f4f7f8}.bubble.user{padding:11px 15px;border:0;border-radius:16px 16px 4px 16px;background:var(--accent);color:var(--on-accent)}.bubble a{color:#6ef0f4;text-decoration:underline;text-underline-offset:2px}
    .composer{background:#060709;border-color:#f4f7f824;padding:14px 16px 10px}.form textarea{border-radius:22px;background:#181b1f;border-color:#f4f7f824;color:#f4f7f8;padding:11px 16px;font-size:16px}.form textarea:focus{border-color:var(--accent)}.send{width:44px;height:44px;border-radius:50%}
    .status,.footer,.reset{color:#b4bdc1}.status{background:#0e1013;padding-top:8px}.error{color:#ffb5a9}.contact-invite{color:#6ef0f4}.location{background:#060709;border-color:#f4f7f824}select{background:#181b1f;border-color:#f4f7f824;color:#f4f7f8}
    .lead-heading,.lead-actions{border-color:#f4f7f824}.lead-back,.lead-intro,.lead-hint,.sms-notice,.lead-status{color:#b4bdc1}.lead-field input{background:#181b1f;border-color:#f4f7f824;color:#f4f7f8}.lead-field input:read-only{background:#24292e}.lead-permissions{background:#181b1f;border-color:#f4f7f824}.lead-status.error{color:#ffb5a9}
    .suggestions{display:flex;flex-wrap:wrap;gap:8px;padding:0 18px 16px;background:#0e1013}.suggestions button{background:transparent;border:1px solid #f4f7f824;color:#f4f7f8;border-radius:999px;padding:9px 14px;text-align:left;font-size:12px}.suggestions button:hover{border-color:var(--accent);color:var(--accent)}
    @media(max-width:600px){.panel,.panel.capture-mode{right:0;bottom:0;width:100vw;max-width:100vw;height:100dvh;max-height:100dvh;border:0}.top{padding-top:max(16px,env(safe-area-inset-top))}.composer,.lead-actions{padding-bottom:max(14px,env(safe-area-inset-bottom))}}
    .hint{position:fixed;right:clamp(18px,3vw,36px);bottom:calc(clamp(18px,3vw,36px) + 80px);z-index:2147483000;background:#fff;color:#060709;border-radius:16px 16px 4px 16px;box-shadow:0 18px 50px #00589844;padding:13px 35px 13px 14px;max-width:270px}.hint-open{display:flex;align-items:center;gap:12px;background:none;color:inherit;padding:0;text-align:left;font-size:13.5px;line-height:1.4}.hint-open strong{display:block;font-weight:500;color:#047a80}.hint-mark{width:36px;height:36px;display:grid;place-items:center;flex:none;border-radius:50%;background:var(--accent);color:var(--on-accent)}.hint-mark svg{width:19px;height:19px}.hint-close{position:absolute;right:9px;top:7px;width:20px;height:20px;border-radius:50%;background:#0001;color:#333;padding:0}
    .bubble.welcome{max-width:100%;padding:0;background:none;border:0;border-radius:0;color:#b4bdc1;font-size:13.5px}.welcome h3{font:400 26px/1.2 var(--font-body,"Montserrat",sans-serif);color:#f4f7f8;margin:8px 0 10px}
    @media(prefers-reduced-motion:reduce){.launcher{transition:none}}
    .entry{flex:1;min-height:0;overflow:auto;padding:24px 20px}.entry h3{font-size:26px;line-height:1.2;font-weight:400;margin:4px 0 12px}.entry p{color:var(--chat-muted,#b4bdc1);font-size:13.5px;line-height:1.6;margin:0 0 24px}.entry-options{display:grid;gap:12px}.entry-option{display:block;width:100%;padding:18px;text-align:left;background:var(--chat-field,#181b1f);border:1px solid var(--chat-line,#f4f7f824);border-radius:12px;color:inherit}.entry-option:hover{border-color:var(--accent)}.entry-option strong{display:block;font-size:15px;margin-bottom:5px}.entry-option span{display:block;color:var(--chat-muted,#b4bdc1);font-size:12px;line-height:1.6}.entry-note{font-size:11px!important;margin:24px 0 0!important}.panel.entry-mode{height:min(640px,calc(100dvh - 60px))}.lead-heading h3{margin-top:12px}.lead-submit{min-height:46px}.lead-permissions{margin-top:20px}.lead-check{line-height:1.5}
    @media(max-width:600px){.panel.entry-mode{height:100dvh}}

    /* Thrive's existing Clear Water design. Runtime behavior above follows Forma. */
    :host{font-family:var(--font-body,"Figtree",sans-serif);color:#173c47;--accent:#23bcc7;--on-accent:#053948;--chat-muted:#546b73;--chat-field:#fff;--chat-line:#d7e7e9}
    .launcher{width:62px;height:62px;background:#053948;color:#23bcc7;box-shadow:0 14px 40px -10px #05394899}.launcher svg{width:26px;height:26px}
    .panel{border-radius:24px;background:#fff;border-color:#d7e7e9;box-shadow:0 30px 90px -20px #05394873}
    .top{background:#053948;border-color:#ffffff24;color:#fff}.title{font:600 16px/1.1 var(--font-display,"Outfit",sans-serif);text-transform:none}.subtitle{color:#d0e5e9;letter-spacing:.14em}
    .history,.entry{background:#f1f8f9}.bubble{background:#fff;border-color:#d7e7e9;color:#173c47}.bubble.user{background:#053948;color:#fff}.bubble a{color:#087b84}
    .composer,.lead-heading,.lead-actions,.lead-form,.location{background:#fff;border-color:#d7e7e9}.form textarea{background:#f1f8f9;border-color:#d7e7e9;color:#173c47}
    .status,.footer,.reset,.lead-back,.lead-intro,.lead-hint,.sms-notice,.lead-status{color:#546b73}.status{background:#f1f8f9}.error,.lead-status.error{color:#a12b20}.contact-invite{color:#087b84}
    select,.lead-field input{background:#fff;border-color:#c8dde0;color:#173c47}.lead-field input:read-only{background:#eef6f7}.lead-permissions{background:#f1f8f9;border-color:#d7e7e9}
    .lead-heading h3,.entry h3,.welcome h3{font-family:var(--font-display,"Outfit",sans-serif);color:#053948;font-weight:600}.entry h3{font-size:24px}.lead-submit{border-radius:999px;color:#053948}
    .suggestions{background:#f1f8f9}.suggestions button{background:#fff;border-color:#c8dde0;color:#053948}.suggestions button:hover{background:#e1f4f5;color:#053948}
    .bubble.welcome{color:#546b73}.welcome h3{font-size:24px}.hint{color:#173c47;border-radius:18px 18px 4px 18px}.hint-open strong{color:#053948;font-family:var(--font-display,"Outfit",sans-serif);font-weight:600}.hint-mark{background:#053948;color:#23bcc7}
    .medical-note{font-size:10px;line-height:1.4;color:#546b73;text-align:center;margin:8px 0 0}
    @media(max-width:820px){.launcher{bottom:88px;width:54px;height:54px}.hint{bottom:150px}}
    @media(max-width:600px){.panel,.panel.capture-mode,.panel.entry-mode{right:0;bottom:0;width:100vw;height:100dvh;max-height:100dvh;border-radius:0}.top{padding-top:max(16px,env(safe-area-inset-top))}}
  </style>
  <button class="launcher" aria-expanded="false" aria-label="Chat with the ThrIVe Concierge" hidden><svg viewBox="0 0 100 130" fill="currentColor" aria-hidden="true"><path d="M50 0C50 0 0 62 0 88a50 50 0 0 0 100 0C100 62 50 0 50 0z"/></svg></button>
  <aside class="hint" hidden><button class="hint-open" aria-label="Ask the ThrIVe Concierge"><span class="hint-mark"><svg viewBox="0 0 100 130" fill="currentColor" aria-hidden="true"><path d="M50 0C50 0 0 62 0 88a50 50 0 0 0 100 0C100 62 50 0 50 0z"/></svg></span><span><strong>Have questions?</strong>I’m here to help.</span></button><button class="hint-close" aria-label="Dismiss chat invitation">×</button></aside>
  <section class="panel" role="dialog" aria-label="Website chat" hidden>
    <header class="top"><span class="mark" aria-hidden="true"><svg viewBox="0 0 100 130" fill="currentColor" aria-hidden="true"><path d="M50 0C50 0 0 62 0 88a50 50 0 0 0 100 0C100 62 50 0 50 0z"/></svg></span><div class="heading"><h2 class="title">Chat with us</h2><div class="subtitle">Your AI concierge</div></div><button class="close" aria-label="Close chat">&times;</button></header>
    <div class="location" hidden><label for="location">Your location</label><select id="location"></select></div>
    <div class="history" role="log" aria-label="Conversation" aria-live="polite" aria-relevant="additions"></div>
    <section class="entry" hidden><h3>Welcome. Let’s get you started.</h3><p>A little about you helps us point you in the right direction.</p><div class="entry-options"><button class="entry-option" data-visitor-type="member" type="button"><strong>I’m a member / returning guest</strong><span>Lounge information, memberships and support.</span></button><button class="entry-option" data-visitor-type="new" type="button"><strong>I’m new</strong><span>Explore our services, memberships and lounges.</span></button></div><p class="entry-note">You’re chatting with an AI assistant. Sharing details does not sign you up for marketing.</p></section>
    <form class="lead-form" data-wg-ignore="true" hidden>
      <div class="lead-heading"><button type="button" class="lead-back">&#8592; Back to chat</button><h3>Share your details</h3></div><div class="lead-fields"><p class="lead-intro"></p>
        <div class="lead-name"><label class="lead-field">First name<input name="firstName" autocomplete="given-name" maxlength="100" required></label><label class="lead-field">Last name<input name="lastName" autocomplete="family-name" maxlength="100" required></label></div>
        <label class="lead-field">Email<input name="email" type="email" autocomplete="email" maxlength="255"></label>
        <label class="lead-field">Phone<input name="phone" type="tel" autocomplete="tel" maxlength="40"></label><p class="lead-hint">Add an email address or phone number.</p>
        <fieldset class="lead-permissions"><legend>Keep in touch (optional)</legend><label class="lead-check"><input type="checkbox" name="optInSms"><span class="sms-label"></span></label><p class="sms-notice"></p><label class="lead-check"><input type="checkbox" name="optInEmail"><span class="email-label"></span></label></fieldset>
      </div><div class="lead-actions"><button type="submit" class="lead-submit">Send details</button><p class="lead-status" role="status" hidden></p></div>
    </form>
    <div class="suggestions" aria-label="Suggested questions" hidden><button type="button">How do memberships work?</button><button type="button">Where are your lounges?</button><button type="button">What is the Good Faith Exam?</button><button type="button">Do you offer mobile IV?</button></div>
    <div class="status" role="status" hidden></div>
    <div class="composer"><button class="contact-invite" type="button" hidden>Share contact details &#8599;</button><form class="form"><textarea rows="1" maxlength="8000" aria-label="Your message" placeholder="Ask about drips, prices, locations…"></textarea><button class="send" aria-label="Send message" type="submit">&#8594;</button></form><div class="footer"><span>Powered by Wellgentic</span><button class="reset" type="button">New conversation</button></div><p class="medical-note">AI assistant, not a medical provider. Please don’t share private medical details here.</p></div>
  </section>`;
  document.body.append(host);
  const get = (selector) => shadow.querySelector(selector);
  const launcher = get(".launcher"),
    panel = get(".panel"),
    history = get(".history"),
    status = get(".status"),
    message = get("textarea"),
    select = get("select"),
    send = get(".send");
  const storageKey = `wellgentic-website:${identity}`;
  let config,
    visitor = null,
    busy = false,
    started = false,
    conversationMode = "agent",
    historyRevision = 0,
    refreshPending = false,
    expiredLead = false,
    selectedVisitorType = null;
  try {
    visitor = JSON.parse(localStorage.getItem(storageKey) || "null");
  } catch {
    /* Storage can be unavailable in private browsing. */
  }
  if (
    visitor &&
    (!visitor.sessionToken ||
      !visitor.sessionId ||
      !Number.isFinite(Date.parse(visitor.expiresAt)) ||
      Date.parse(visitor.expiresAt) <= Date.now())
  ) {
    expiredLead = !!visitor.pendingLead || !!visitor.leadUnconfirmed;
    visitor = null;
  }
  const requiresIntake = () => config?.leadCapture?.prechatVersion === "website-prechat-v1";
  const needsIntake = () => requiresIntake() && !visitor?.leadComplete && !visitor?.leadUnconfirmed && !expiredLead;
  const showEntry = () => {
    get(".entry").hidden = false; get(".lead-form").hidden = true;
    history.hidden = true; get(".composer").hidden = true;
    const suggestions = get(".suggestions"); if (suggestions) suggestions.hidden = true;
    panel.classList.remove("capture-mode"); panel.classList.add("entry-mode");
    tell(""); get(".entry-option").focus();
  };
  const persist = () => {
    try {
      visitor || expiredLead
        ? localStorage.setItem(storageKey, JSON.stringify(visitor || { leadUnconfirmed: true }))
        : localStorage.removeItem(storageKey);
      return true;
    } catch {
      /* The current page still retains the conversation. */
      return false;
    }
  };
  const tell = (
    text,
    error = false,
    onRetry = null,
    retryLabel = "Try again",
  ) => {
    status.textContent = text;
    status.hidden = !text;
    status.classList.toggle("error", error);
    if (onRetry) {
      const button = document.createElement("button");
      button.className = "retry";
      button.textContent = retryLabel;
      button.onclick = onRetry;
      status.append(button);
    }
  };
  const bubble = (role, text, author) => {
    const element = document.createElement("div");
    element.className = `bubble${role === "user" ? " user" : ""}`;
    const appendText = (value) => {
      // Format the model's common emphasis without interpreting HTML. Keep
      // visitor messages exactly as written.
      const segments = role === "user" ? [value] : value.split(/(\*\*[^*\n]+\*\*)/g);
      for (const segment of segments) {
        if (role !== "user" && /^\*\*[^*\n]+\*\*$/.test(segment)) {
          const emphasis = document.createElement("strong");
          emphasis.textContent = segment.slice(2, -2);
          element.append(emphasis);
        } else element.append(document.createTextNode(segment));
      }
    };
    const parts = role === "user" ? [String(text)] : String(text).split(/(\[[^\]]+\]\([^)]+\))/g);
    for (const part of parts) {
      const link = role === "user" ? null : /^\[([^\]]+)\]\(([^)]+)\)$/.exec(part);
      let url;
      try { if (link) url = new URL(link[2], document.baseURI); } catch {}
      const allowed = url && !url.username && !url.password && (
        (url.protocol === "https:" && [location.hostname, "thrivedripspa.com", "www.thrivedripspa.com", "book.thrivedripspa.com"].includes(url.hostname)) ||
        (url.protocol === "tel:" && /^tel:[+()0-9 -]+$/.test(url.href)));
      if (allowed) {
        if (["thrivedripspa.com", "www.thrivedripspa.com"].includes(url.hostname) && url.pathname.endsWith(".html")) {
          const root = new URL(script.src); root.pathname = root.pathname.replace(/assets\/js\/chat\.js$/, ""); root.search = "";
          url = new URL(url.pathname.slice(1) + url.search + url.hash, root);
        }
        const a = document.createElement("a"); a.href = url.href; a.textContent = link[1]; element.append(a); }
      else appendText(link ? link[1] : part);
    }
    if (author === "team") {
      const label = document.createElement("strong");
      label.textContent = "Team\n";
      element.prepend(label);
    }
    if (role !== "user" && !history.children.length) {
      element.classList.add("welcome");
      const heading = document.createElement("h3");
      heading.textContent = "How can we help you thrive today?";
      element.prepend(heading);
    }
    history.append(element);
    history.scrollTop = history.scrollHeight;
  };
  const setBusy = (value) => {
    busy = value;
    message.disabled = value || needsIntake();
    message.readOnly = !!visitor?.pending;
    send.disabled =
      value ||
      !message.value.trim() ||
      ["review_required", "unavailable"].includes(visitor?.pending?.state);
    select.disabled = value || !!visitor;
    get(".reset").disabled =
      value || !!visitor?.pendingLead || (!!visitor?.pending && visitor.pending.state !== "unavailable");
    get(".contact-invite").hidden = !started || config?.leadCapture?.consentVersion !== "website-inquiry-v1";
    get(".contact-invite").disabled = value || !!visitor?.pending || !!visitor?.leadComplete || !!visitor?.leadUnconfirmed;
    get(".contact-invite").textContent = visitor?.leadComplete ? "Contact details sent" : "Share contact details ↗";
    get(".lead-submit").disabled = value || visitor?.pendingLead?.unavailable === true;
    get(".lead-submit").textContent = value ? "Please wait..." : visitor?.pendingLead ? "Check submission" : needsIntake() ? "Start chat →" : "Send details";
    get(".lead-back").disabled = value || !!visitor?.pendingLead;
    for (const button of shadow.querySelectorAll(".entry-option")) button.disabled = value;
    for (const input of shadow.querySelectorAll(".lead-form input")) {
      input.readOnly = !!visitor?.pendingLead;
      input.disabled = value || (input.type === "checkbox" && !!visitor?.pendingLead);
    }
  };
  const request = async (endpoint, body) => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 35000);
    let response;
    try {
      response = await fetch(`${base}/api/widget${endpoint}`, {
        method: body ? "POST" : "GET",
        credentials: "omit",
        signal: controller.signal,
        headers: {
          Authorization: `Bearer ${apiKey}`,
          ...(body ? { "Content-Type": "application/json" } : {}),
        },
        body: body ? JSON.stringify({ workflowId, ...body }) : undefined,
      });
    } finally {
      clearTimeout(timeout);
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(
        data.message || data.error || "Chat is temporarily unavailable.",
      );
      error.status = response.status;
      error.code = data.error;
      error.actionOutcome = data.actionOutcome;
      throw error;
    }
    return data;
  };
  const captureAttribution = () => {
    const provider = window.THRIVE_CRM?.attribution || window.WellgenticWebsite?.attribution;
    if (typeof provider === "function") return provider();
    // Campaign dimensions may accompany the inquiry. Cookies and click IDs
    // require an explicit consent-aware provider; never infer permission here.
    const touch = { landingPage: location.origin + location.pathname, referrer: "",
      consentState: { analytics: "denied", ads: "denied", personalization: "denied" } };
    try { const ref = new URL(document.referrer); touch.referrer = ref.origin + ref.pathname; } catch {}
    const params = new URLSearchParams(location.search);
    for (const key of ["utm_source","utm_medium","utm_campaign","utm_content","utm_term","utm_id","utm_source_platform"]) {
      if (params.get(key)) touch[key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())] = params.get(key).slice(0,255);
    }
    return touch;
  };
  const newRequestId = () => {
    const bytes = crypto.getRandomValues(new Uint8Array(16));
    bytes[6] = (bytes[6] & 15) | 64; bytes[8] = (bytes[8] & 63) | 128;
    const hex = [...bytes].map(value => value.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  };
  const leadTell = (text, error = false) => {
    const element = get(".lead-status"); element.textContent = text; element.hidden = !text; element.classList.toggle("error", error);
  };
  const showLeadCapture = (open) => {
    get(".entry").hidden = true; panel.classList.remove("entry-mode");
    get(".lead-back").textContent = needsIntake() ? "← Back" : "← Back to chat";
    get(".lead-heading h3").textContent = needsIntake() ? "How can we reach you?" : "Share your details";
    selectedVisitorType = visitor?.pendingLead?.visitorType || selectedVisitorType;
    if (needsIntake()) get(".lead-intro").textContent = selectedVisitorType === "member"
      ? "Tell us who you are so the team can follow up on your question. This does not sign you in to your member account."
      : "Add your details, then ask us anything about ThrIVe. Marketing updates are entirely your choice.";
    get(".suggestions").hidden = open || renderedEntries.some(entry => entry.role === "user");
    get(".lead-form").hidden = !open; history.hidden = open; get(".composer").hidden = open; panel.classList.toggle("capture-mode", open);
    if (open) {
      tell("");
      if (visitor?.pendingLead) {
        for (const key of ["firstName", "lastName", "email", "phone", "optInSms", "optInEmail"]) {
          const value = visitor.pendingLead.lead?.[key];
          const input = get(`.lead-form [name="${key}"]`);
          if (!input) continue;
          if (input.type === "checkbox") input.checked = value === true; else input.value = String(value || "");
        }
        leadTell(visitor.pendingLead.unavailable ? "This submission can no longer be checked here. Ask the team in this chat before sending your details again." : "Your submission has not been confirmed. Check it again using the same details.");
      }
      get('.lead-form [name="firstName"]').focus();
    } else message.focus();
    setBusy(busy);
  };
  get(".contact-invite").onclick = () => { if (!busy && started && !visitor?.pending && !visitor?.leadComplete && !visitor?.leadUnconfirmed) showLeadCapture(true); };
  get(".lead-back").onclick = () => { if (!busy && !visitor?.pendingLead) needsIntake() ? showEntry() : showLeadCapture(false); };
  for (const button of shadow.querySelectorAll(".entry-option")) {
    button.onclick = () => { if (busy) return; selectedVisitorType = button.dataset.visitorType; showLeadCapture(true); };
  }
  get(".lead-form").addEventListener("input", () => { if (!busy && !visitor?.pendingLead) leadTell(""); });
  get(".lead-form").onsubmit = async event => {
    event.preventDefault();
    if (busy || visitor?.pending || visitor?.leadComplete || visitor?.leadUnconfirmed || visitor?.pendingLead?.unavailable) return;
    if (requiresIntake() && !selectedVisitorType && !visitor?.pendingLead?.visitorType) return showEntry();
    if (!started) {
      await initialize();
      if (!started || !visitor) return;
    }
    if (!visitor.pendingLead) {
      const lead = {};
      for (const key of ["firstName", "lastName", "email", "phone", "optInSms", "optInEmail"]) {
        const input = get(`.lead-form [name="${key}"]`); lead[key] = input.type === "checkbox" ? input.checked : input.value.trim();
      }
      if (!lead.firstName || !lead.lastName) return leadTell("Add your first and last name.", true);
      if (!lead.email && !lead.phone) return leadTell("Add an email address or phone number.", true);
      if ((lead.optInSms && !lead.phone) || (lead.optInEmail && !lead.email)) return leadTell("Add the phone number or email address for the updates you selected.", true);
      visitor.pendingLead = { requestId: newRequestId(), lead, consentVersion: config.leadCapture.consentVersion,
        ...(requiresIntake() ? { visitorType: selectedVisitorType, attribution: captureAttribution() } : {}),
      };
      if (!persist()) {
        delete visitor.pendingLead;
        return leadTell("This browser cannot save your submission for recovery. Please share your details with the team in this chat instead.", true);
      }
    }
    setBusy(true); leadTell("Sending your details...");
    try {
      const data = await request("/leads", { sessionId: visitor.sessionId, sessionToken: visitor.sessionToken, ...visitor.pendingLead });
      if (data.received !== true) throw new Error("Your submission has not been confirmed. Check it again.");
      const submittedType = visitor.pendingLead.visitorType;
      const receiptId = visitor.pendingLead.requestId;
      delete visitor.pendingLead; visitor.leadComplete = true; visitor.visitorType = submittedType; persist();
      window.dispatchEvent(new CustomEvent("wellgentic-chat:lead-received", { detail: { requestId: receiptId, visitorType: submittedType, workflowId } }));
      get(".lead-form").reset(); leadTell(""); showLeadCapture(false);
      tell("Thanks—you’re ready to chat.");
    } catch (error) {
      if (error.actionOutcome === "not_applied") { delete visitor.pendingLead; persist(); }
      else if (error.status === 401 || error.status === 403) { visitor.pendingLead.unavailable = true; persist(); }
      leadTell(["AbortError", "TypeError"].includes(error.name) ? "The connection was interrupted. Check your submission again; your details will not be sent twice." : error.message, true);
    } finally { setBusy(false); }
  };
  let renderedHistory = "", renderedEntries = [];
  const renderHistory = (messages) => {
    const signature = JSON.stringify(messages);
    if (signature === renderedHistory) return;
    renderedHistory = signature;
    const atBottom = history.scrollHeight - history.scrollTop - history.clientHeight < 48;
    const oldTop = history.scrollTop;
    const appended = messages.length >= renderedEntries.length && renderedEntries.every((entry, index) => JSON.stringify(entry) === JSON.stringify(messages[index]));
    const entries = appended ? messages.slice(renderedEntries.length) : messages;
    if (!appended) history.replaceChildren();
    renderedEntries = messages;
    for (const entry of entries)
      if (
        ["user", "assistant"].includes(entry.role) &&
        typeof entry.content === "string"
      )
        bubble(entry.role, entry.content, entry.author);
    if (!atBottom) history.scrollTop = oldTop;
  };
  const durableRequest = async (endpoint, body) => {
    for (let attempt = 0; attempt < 8; attempt++) {
      const data = await request(endpoint, body);
      if (!data.pending) return data;
      tell("Your message is still being processed...");
      await new Promise((resolve) => setTimeout(resolve, 4000));
    }
    throw new Error(
      "Your message is still being processed. Try again to check its reply.",
    );
  };
  const retryMessage = async () => {
    if (busy || !visitor?.pending) return;
    const pending = visitor.pending;
    historyRevision++;
    get(".suggestions").hidden = true;
    message.value = pending.message;
    setBusy(true);
    tell(conversationMode === "team" ? "Sending to the team..." : "Thinking...");
    try {
      const data = await durableRequest("/chat", {
        sessionId: visitor.sessionId,
        sessionToken: visitor.sessionToken,
        requestId: pending.requestId,
        message: pending.message,
      });
      if (Array.isArray(data.conversationHistory))
        renderHistory(data.conversationHistory);
      else {
        bubble("user", pending.message);
        if (data.response) bubble("assistant", data.response);
      }
      showMode(data.mode);
      delete visitor.pending;
      persist();
      message.value = "";
      message.style.height = "auto";
      tell("");
    } catch (error) {
      const held = error.code === "review_required";
      const unavailable =
        error.status === 401 || error.code === "session_closed";
      if (unavailable) {
        visitor.pending.state = "unavailable";
        persist();
      }
      if (held) {
        visitor.pending.state = "review_required";
        persist();
      }
      tell(
        ["AbortError", "TypeError"].includes(error.name)
          ? "The connection was interrupted. Try again to check the reply to your message."
          : error.message,
        true,
        unavailable ? null : retryMessage,
        held ? "Check for team reply" : "Try again",
      );
    } finally {
      setBusy(false);
      message.focus();
    }
  };
  const initialize = async () => {
    if (busy || started) return;
    if (config.locations.length > 1 && !select.value && !visitor) {
      tell("Choose your location to start chatting.");
      return;
    }
    historyRevision++;
    setBusy(true);
    tell("Connecting...");
    try {
      if (!visitor) {
        const locationProfileId =
          Number(select.value) || config.locations[0]?.id || null;
        visitor = {
          ...(await request("/session", { locationProfileId })),
          locationProfileId,
          ...(expiredLead ? { leadUnconfirmed: true } : {}),
        };
        persist();
      }
      const data = await durableRequest("/chat/init", {
        sessionId: visitor.sessionId,
        sessionToken: visitor.sessionToken,
      });
      const messages = Array.isArray(data.conversationHistory)
        ? data.conversationHistory
        : [];
      renderHistory(messages);
      showMode(data.mode);
      if (!messages.length) bubble("assistant", config.welcomeMessage);
      if (data.pendingRequest) visitor.pending = data.pendingRequest;
      else if ("pendingRequest" in data) delete visitor.pending;
      persist();
      started = true;
      get(".suggestions").hidden = messages.some(entry => entry.role === "user");
      if (visitor.pending?.state === "review_required") {
        message.value = visitor.pending.message;
        tell(
          "An action needs to be checked by the team before this conversation can continue.",
          true,
          retryMessage,
          "Check for team reply",
        );
      } else if (visitor.pending) {
        message.value = visitor.pending.message;
        // Reuse the submitted request, including after a page reload. Never
        // manufacture a new execution because its HTTP response was lost.
        setTimeout(retryMessage, 0);
      } else if (visitor.pendingLead) showLeadCapture(true);
      else if (visitor.leadUnconfirmed) tell("A previous submission could not be confirmed before this session expired. Ask the team in this chat before sending your details again.", true);
      else if (needsIntake()) selectedVisitorType ? showLeadCapture(true) : showEntry();
      else tell("");
    } catch (error) {
      if (error.status === 401) {
        expiredLead = !!visitor?.pendingLead || !!visitor?.leadUnconfirmed;
        visitor = null;
        persist();
      }
      if (error.code === "session_closed" && visitor?.pending) {
        visitor.pending.state = "unavailable";
        persist();
      }
      tell(
        error.message,
        true,
        error.code === "session_closed" ? null : initialize,
      );
    } finally {
      setBusy(false);
    }
  };
  const showMode = (mode) => {
    conversationMode = mode === "team" ? "team" : "agent";
    get(".subtitle").textContent = conversationMode === "team" ? "Your conversation is with our team" : "Your AI concierge";
  };
  const refreshHistory = async () => {
    if (refreshPending || busy || !started || !visitor || visitor.pending || panel.hidden || document.hidden) return;
    const currentVisitor = visitor;
    const revision = historyRevision;
    refreshPending = true;
    try {
      const data = await request("/chat/history", { sessionId: visitor.sessionId, sessionToken: visitor.sessionToken });
      // Ignore a read that raced a send, reset or a different signed visitor.
      if (currentVisitor !== visitor || revision !== historyRevision || busy || visitor.pending) return;
      if (Array.isArray(data.conversationHistory)) renderHistory(data.conversationHistory);
      showMode(data.mode);
    } catch {
      // Preserve the current history and draft. The next visible poll retries;
      // a failed read never creates a conversation or resubmits a message.
    } finally { refreshPending = false; }
  };
  setInterval(refreshHistory, 10000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) refreshHistory(); });
  const open = () => {
    panel.hidden = false;
    document.body.classList.add("chat-open");
    launcher.hidden = true;
    get(".hint").hidden = true;
    try { sessionStorage.setItem("thrive-chat-hint", "1"); } catch {}
    launcher.setAttribute("aria-expanded", "true");
    if (needsIntake() && !visitor?.pending && !visitor?.leadUnconfirmed) {
      if (visitor?.pendingLead || selectedVisitorType) showLeadCapture(true); else showEntry();
    } else initialize();
    refreshHistory();
    if (!needsIntake()) message.focus();
  };
  const close = () => {
    panel.hidden = true;
    document.body.classList.remove("chat-open");
    launcher.hidden = false;
    launcher.setAttribute("aria-expanded", "false");
    launcher.focus();
  };
  launcher.onclick = () => (panel.hidden ? open() : close());
  get(".hint-open").onclick = open;
  get(".hint-close").onclick = () => { get(".hint").hidden = true; try { sessionStorage.setItem("thrive-chat-hint", "1"); } catch {} };
  get(".close").onclick = close;
  shadow.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) {
      event.preventDefault();
      close();
    }
  });
  select.onchange = () => { if (!needsIntake()) initialize(); };
  message.oninput = () => {
    message.style.height = "auto";
    message.style.height = `${Math.min(message.scrollHeight, 150)}px`;
    setBusy(busy);
  };
  get(".form").onsubmit = async (event) => {
    event.preventDefault();
    if (busy || needsIntake() || !message.value.trim()) return;
    if (!started) {
      await initialize();
      if (!started) return;
    }
    if (!visitor.pending) {
      visitor.pending = {
        requestId: newRequestId(),
        message: message.value.trim(),
      };
      persist();
    }
    if (!["review_required", "unavailable"].includes(visitor.pending.state))
      await retryMessage();
  };
  for (const button of shadow.querySelectorAll(".suggestions button")) {
    button.onclick = () => { if (busy) return; message.value = button.textContent; get(".form").requestSubmit(); };
  }
  message.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) { event.preventDefault(); get(".form").requestSubmit(); }
  });
  get(".reset").onclick = () => {
    if (busy || visitor?.pendingLead) return;
    visitor = null;
    expiredLead = false;
    get(".lead-form").reset(); leadTell(""); showLeadCapture(false);
    started = false; selectedVisitorType = null;
    historyRevision++;
    renderedHistory = "";
    renderedEntries = [];
    showMode("agent");
    persist();
    history.replaceChildren();
    message.value = "";
    message.style.height = "auto";
    select.disabled = false;
    if (config.locations.length > 1) select.value = "";
    if (needsIntake()) showEntry(); else initialize();
  };
  request(`/config/${workflowId}`)
    .then((value) => {
      if (value.leadCapture?.prechatVersion !== "website-prechat-v1") throw new Error("The pre-chat intake service is not ready.");
      config = {
        ...value,
        locations: Array.isArray(value.locations) ? value.locations : [],
      };
      for (const [selector, key] of [[".lead-intro", "introduction"], [".sms-label", "smsLabel"], [".sms-notice", "smsNotice"], [".email-label", "emailLabel"]]) {
        get(selector).textContent = typeof config.leadCapture?.[key] === "string" ? config.leadCapture[key] : "";
      }
      get(".title").textContent = config.agentName;
      panel.setAttribute("aria-label", config.agentName);
      if (/^#[0-9a-f]{6}$/i.test(config.primaryColor)) {
        host.style.setProperty("--accent", config.primaryColor);
        const channels = [1, 3, 5].map((index) => {
          const v =
            parseInt(config.primaryColor.slice(index, index + 2), 16) / 255;
          return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
        });
        host.style.setProperty(
          "--on-accent",
          channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722 >
            0.179
            ? "#10251b"
            : "#ffffff",
        );
      }
      host.setAttribute(
        "data-side",
        config.position === "bottom-left" ? "left" : "right",
      );
      if (config.locations.length > 1) {
        get(".location").hidden = false;
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Choose a location";
        select.append(placeholder);
        for (const location of config.locations) {
          const option = document.createElement("option");
          option.value = location.id;
          option.textContent = location.name;
          select.append(option);
        }
        select.value = visitor?.locationProfileId
          ? String(visitor.locationProfileId)
          : "";
      }
      launcher.hidden = false;
      try {
        if (!sessionStorage.getItem("thrive-chat-hint")) {
          setTimeout(() => { try { if (panel.hidden && !sessionStorage.getItem("thrive-chat-hint")) get(".hint").hidden = false; } catch {} }, 3500);
          setTimeout(() => { get(".hint").hidden = true; try { sessionStorage.setItem("thrive-chat-hint", "1"); } catch {} }, 16000);
        }
      } catch {}
      setBusy(false);
    })
    .catch(() => {
      host.remove();
    });
})();
