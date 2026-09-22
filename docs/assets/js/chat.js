/* ThrIVe Concierge — Claude-powered */
(function () {
  "use strict";

  var CFG = window.TDS_CHAT || {};
  var MODEL = CFG.model || "claude-sonnet-4-6";

  var SYSTEM = [
    "You are the ThrIVe Concierge, the friendly AI assistant for ThrIVe Drip Spa (thrivedripspa.com) — an IV vitamin therapy and lifestyle wellness spa founded in Houston as the first IV drip spa in Texas, with ten lounges across Greater Houston, Dallas and Fort Worth plus mobile concierge service. You live on their website.",
    "Voice: warm, upbeat, spa-calm and concise — like the best spa consultant at the front desk. Short paragraphs. Brand lines: 'Hydrate. Energize. Thrive.' and 'Feel better in about an hour.' Brand spelled ThrIVe.",
    "MEDICAL GUARDRAILS: you are not a medical provider. Never diagnose, never recommend a treatment for a specific medical condition, never discuss dosing of prescription medications. You may describe what each drip contains and what clients commonly book it for, and always note that a licensed provider completes a Good Faith Exam before any treatment and that clients should consult their physician about medical concerns. If someone describes an emergency, tell them to call 911.",
    "FACTS:",
    "- PHONE 844-820-1713. Book online at book.thrivedripspa.com (under a minute, no card needed). eGift cards and member login through the Meevo portal. Affirm financing available.",
    "- LOUNGES (Mon–Fri 9am–7pm, Sat–Sun 10am–6pm unless noted): Memorial 1014 Wirt Rd Ste 210, Houston (713) 955-3747 · Memorial Green 12505 Memorial Dr Ste 120, Houston (346) 444-3747 (9:30–7 / 9:30–6:30) · The Heights 2799 Katy Fwy Ste 210, Houston (346) 320-3114 (weekends 9:30–6:30) · West University 3277 Southwest Fwy, Houston (713) 955-3797 · Vintage Park 10300 Louetta Rd Ste 114, Houston (346) 712-3747 · Katy 6445 FM 1463 Ste 120 (346) 707-8703 · The Woodlands 9595 Six Pines Dr Ste 1460 (281) 343-3747 (10–6 daily) · Clear Lake 3535 Clearlake City Blvd Ste 700 (281) 783-4108 (Sun 10–6; call for Sat) · Highland Park (Dallas) 5301 W Lovers Ln Ste 103 (214) 214-3747 · Fort Worth 2708 S Hulen St (682) 747-3747. Mobile IV serves the Houston area (home, hotel, office, event; groups welcome).",
    "- DRIPS (walk-in / member; every drip = 1 L IV fluids + electrolytes; 30–45 min): Hydrate $150/$120 · Myers $190/$150 (Vit C, Mg, B-complex, B12) · Detox $190/$150 (high-dose glutathione) · Party $190/$150 (Toradol, Zofran — hangover) · Fit $190/$150 (carnitine, arginine, BCAAs) · Slim $190/$150 (carnitine, aminos, B12) · Libido $190/$150 (arginine, B12) · Beauty $190/$150 (Vit C, glutathione) · Migraine $190/$150 (Mg, Reglan, Toradol; Benadryl free, bring a driver) · High C $230/$200 (10 g Vit C) · Immuno $310/$250 (Vit C, glutathione, zinc) · NAD+ drip: consultant pricing, up to 2 hours.",
    "- BOOSTERS (add to any drip): $25 Zofran, Vit C, Anti-Acid, Magnesium, Toradol, Zinc, Reglan, B12, Benadryl, Proline; $40 Glutathione, Arginine, Carnitine, B-Complex, Biotin, Taurine; $70 Total Wellness; $80 High-C; NAD+ from $125; Immuno $160 ($130 member).",
    "- SHOTS (15 min, IM): $25 Toradol, Zofran, B12; $40 Fit, Vitamin D3, Lipo B, Lipo C, Biotin, CoQ10; $70 Tri-Immuno; NAD+ $50/50 mg, $75/75 mg, $100/100 mg.",
    "- MEMBERSHIPS (month-to-month, pause/cancel anytime at front desk, credits usable on any service incl. NAD+ and BTL, unused rolls over, birthday drip free, priority booking): Select $95/mo → $140 credit · Premium $165 → $260 · Luxe $285 → $490 · Family Premium $129 (1 premium IV + 1 booster; needs a household member with a regular membership) · Family Luxe $229 (2 IVs + 1 booster) · Student Premium $105 / Luxe $180 · NAD+ Premium $350 (500 mg) / Luxe $700 (1,000 mg) / Platinum $999 (1,500 mg).",
    "- PACKAGES: shots/boosters buy 4 get 1 free or buy 8 get 3 free; B12 buy 8 get 2; Tri-Immuno 5 for $300; NAD+ shot packs 400 mg $300, 500 mg $375; NAD+ loading doses 2-day 2,500 mg $1,750 member/$2,375, 3-day 3,500 mg $2,450/$3,325, 5-day 6,000 mg $4,200/$5,700; members-only premium drips 4 for $500 or 10 for $1,100.",
    "- BODY & FACE (BTL; pricing at complimentary consultation; membership credits apply): EMFACE (needle-free facial lift, 20 min, series of 4; Memorial, Memorial Green, West U, Highland Park, Fort Worth) · Emsculpt (HIFEM muscle building, 30 min) · Emsculpt NEO (fat + muscle, four weekly 30-min sessions; most lounges) · EMTONE (cellulite/skin tightening, ~20 min, 4 sessions; Memorial, Highland Park) · Normatec compression $25 ($20 member) · Infrared sauna at Vintage Park and Clear Lake · Styku 3D body scan at Memorial Green.",
    "- WEIGHT LOSS: medically supervised weight-loss injections with telehealth consults; weekly injections; results often within the first month, significant by 12–16 weeks. Pricing and medication details come from the provider at consultation.",
    "- GOOD FAITH EXAM: required by Texas law before the first service (video or in-lounge), renewed annually; $35 ($45 with bloodwork), credited back to the account. Nurses use lidocaine to numb the site.",
    "- PROMOS: new clients 25% off first IV drip. Founder/CEO: Dr. Eugene Lou, MD (MIT graduate, orthopedic surgeon). LegitScript certified. ABC13 Houston featured the Party Drip.",
    "RULES: Answer only about ThrIVe Drip Spa — drips, boosters, shots, NAD+, body & face, weight loss, memberships, packages, locations, booking and policies. Link pages with markdown like [Drip Menu](iv-therapy.html), [NAD+](nad.html), [Memberships](memberships.html), [Locations](locations.html), [Mobile IV](mobile-iv.html), [Body & Face](body-contouring.html), [Weight Loss](weight-loss.html), [FAQ](faq.html), [Book Now](book.html), [Good Faith Exam](gfe-process.html). For location-specific questions give that lounge's phone. Keep answers under 110 words. End with one clear next step — usually booking online.",
  ].join("\n");

  // ThrIVe drop mark
  var MARK = '<svg viewBox="0 0 100 130" aria-hidden="true"><path d="M50 0C50 0 0 62 0 88a50 50 0 0 0 100 0C100 62 50 0 50 0z" fill="currentColor"/></svg>';

  var CHIPS = [
    "Which drip should I book?",
    "How much is a Myers Drip?",
    "How do memberships work?",
    "What's the Good Faith Exam?",
    "Do you come to my house?"
  ];

  /* ---------- build DOM ---------- */
  var root = document.createElement("div");
  root.innerHTML =
    '<button class="chat-orb" aria-label="Chat with the ThrIVe Concierge">' + MARK + "</button>" +
    '<div class="chat-orb__hint" role="button" tabindex="0">' +
    '  <span class="chat-orb__hint-avatar">' + MARK + "</span>" +
    '  <span class="chat-orb__hint-text"><em>Not sure which drip?</em> Ask me anything.</span>' +
    '  <button class="chat-orb__hint-x" aria-label="Dismiss">✕</button>' +
    "</div>" +
    '<div class="chat-panel" role="dialog" aria-label="ThrIVe Concierge chat">' +
    '  <div class="chat-head">' +
    '    <div class="chat-head__icon">' + MARK + "</div>" +
    '    <div><div class="chat-head__name">ThrIVe Concierge</div><div class="chat-head__sub">AI assistant · ThrIVe Drip Spa</div></div>' +
    '    <button class="chat-head__close" aria-label="Close chat">✕</button>' +
    "  </div>" +
    '  <div class="chat-msgs"></div>' +
    '  <div class="chat-input">' +
    '    <textarea rows="1" placeholder="Ask about drips, prices, locations…" aria-label="Message"></textarea>' +
    '    <button class="chat-send" aria-label="Send">→</button>' +
    "  </div>" +
    '  <div class="chat-note">The Concierge is an AI assistant, not a medical provider. Book at book.thrivedripspa.com or call 844-820-1713.</div>' +
    "</div>";
  document.body.appendChild(root);

  var orb = root.querySelector(".chat-orb");
  var hint = root.querySelector(".chat-orb__hint");
  var msgs = root.querySelector(".chat-msgs");
  var input = root.querySelector(".chat-input textarea");
  var sendBtn = root.querySelector(".chat-send");
  var history = [];
  try { history = JSON.parse(sessionStorage.getItem("tds-chat") || "[]"); } catch (e) {}

  /* activation link: visiting any page with #ck=<api-key> stores the key in
     this browser and cleans the URL — the key never lives in the repo */
  try {
    var ckm = location.hash.match(/[#&]ck=([^&]+)/);
    if (ckm) {
      localStorage.setItem("tds-anthropic-key", decodeURIComponent(ckm[1]));
      try { window.history.replaceState(null, "", location.pathname + location.search); } catch (e) {}
    }
  } catch (e) {}

  function getKey() {
    if (CFG.proxyUrl) return "proxy";
    if (CFG.apiKey) return CFG.apiKey;
    try { return localStorage.getItem("tds-anthropic-key") || ""; } catch (e) { return ""; }
  }

  /* ---------- rendering ---------- */
  function md(t) {
    t = t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    var blocks = t.split(/\n{2,}/).map(function (b) {
      var lines = b.split("\n");
      var items = lines.filter(function (l) { return /^\s*[-•]\s+/.test(l); });
      if (items.length && items.length === lines.length) {
        return "<ul>" + items.map(function (l) { return "<li>" + l.replace(/^\s*[-•]\s+/, "") + "</li>"; }).join("") + "</ul>";
      }
      return "<p>" + b.replace(/\n/g, "<br>") + "</p>";
    });
    return blocks.join("");
  }

  function addMsg(role, html) {
    var d = document.createElement("div");
    d.className = "chat-msg chat-msg--" + (role === "user" ? "user" : "ai");
    d.innerHTML = role === "user" ? html.replace(/</g, "&lt;") : html;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }

  function welcome() {
    var w = document.createElement("div");
    w.className = "chat-welcome";
    w.innerHTML = "<h3>Which drip is right for you?</h3><p>Drips, prices, memberships, locations, mobile service — ask me anything about ThrIVe.</p>" +
      '<div class="chat-chips">' + CHIPS.map(function (c) { return "<button>" + c + "</button>"; }).join("") + "</div>";
    msgs.appendChild(w);
    w.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () { input.value = b.textContent; send(); });
    });
  }

  function keyGate() {
    var g = document.createElement("div");
    g.className = "chat-gate";
    g.innerHTML = "<p><strong>One-time setup:</strong> paste your Anthropic API key to activate the ThrIVe Concierge. It's stored only in this browser.</p>" +
      '<input type="password" placeholder="sk-ant-…" aria-label="Anthropic API key">' +
      '<button class="btn btn--solid btn--sm">Activate →</button>';
    msgs.appendChild(g);
    g.querySelector("button").addEventListener("click", function () {
      var v = g.querySelector("input").value.trim();
      if (!v) return;
      try { localStorage.setItem("tds-anthropic-key", v); } catch (e) {}
      g.remove();
      addMsg("ai", "<p>All set! Ask me anything about ThrIVe. 💧</p>");
    });
  }

  function restore() {
    if (!history.length) { welcome(); }
    else history.forEach(function (m) { addMsg(m.role, m.role === "user" ? m.content : md(m.content)); });
    if (!getKey()) keyGate();
  }

  /* ---------- Claude call (streaming) ---------- */
  function send() {
    var text = input.value.trim();
    if (!text) return;
    if (!getKey()) { keyGate(); return; }
    input.value = "";
    var wEl = msgs.querySelector(".chat-welcome");
    if (wEl) wEl.remove();
    addMsg("user", text);
    history.push({ role: "user", content: text });
    sendBtn.disabled = true;

    var typing = document.createElement("div");
    typing.className = "chat-typing";
    typing.innerHTML = "<i></i><i></i><i></i>";
    msgs.appendChild(typing);
    msgs.scrollTop = msgs.scrollHeight;

    var aiEl = null, full = "";
    var apiUrl = CFG.proxyUrl || "https://api.anthropic.com/v1/messages";
    var apiHeaders = { "content-type": "application/json" };
    if (!CFG.proxyUrl) {
      apiHeaders["x-api-key"] = getKey();
      apiHeaders["anthropic-version"] = "2023-06-01";
      apiHeaders["anthropic-dangerous-direct-browser-access"] = "true";
    }
    fetch(apiUrl, {
      method: "POST", headers: apiHeaders,
      body: JSON.stringify({ model: MODEL, max_tokens: 700, system: SYSTEM, messages: history.slice(-12), stream: true })
    }).then(function (res) {
      if (!res.ok) return res.text().then(function (t) { throw new Error("API " + res.status + ": " + t.slice(0, 200)); });
      var reader = res.body.getReader(), dec = new TextDecoder(), buf = "";
      function pump() {
        return reader.read().then(function (r) {
          if (r.done) return;
          buf += dec.decode(r.value, { stream: true });
          var lines = buf.split("\n"); buf = lines.pop();
          lines.forEach(function (ln) {
            if (ln.indexOf("data: ") !== 0) return;
            try {
              var ev = JSON.parse(ln.slice(6));
              if (ev.type === "content_block_delta" && ev.delta && ev.delta.text) {
                if (!aiEl) { typing.remove(); aiEl = addMsg("ai", ""); }
                full += ev.delta.text;
                aiEl.innerHTML = md(full);
                msgs.scrollTop = msgs.scrollHeight;
              }
            } catch (e) {}
          });
          return pump();
        });
      }
      return pump();
    }).then(function () {
      if (typing.parentNode) typing.remove();
      if (full) {
        history.push({ role: "assistant", content: full });
        try { sessionStorage.setItem("tds-chat", JSON.stringify(history.slice(-20))); } catch (e) {}
      }
    }).catch(function (err) {
      if (typing.parentNode) typing.remove();
      var isAuth = /401|403/.test(err.message);
      if (isAuth) { try { localStorage.removeItem("tds-anthropic-key"); } catch (e) {} }
      addMsg("ai", "<p>" + (isAuth
        ? "That API key didn't work — let's try again."
        : "I'm having trouble connecting right now. You can always <a href='book.html'>book online</a> or call 844-820-1713.") + "</p>");
      if (isAuth) keyGate();
      history.pop();
    }).finally(function () {
      sendBtn.disabled = false;
      input.focus();
    });
  }

  /* ---------- events ---------- */
  function openChat() {
    document.body.classList.add("chat-open");
    hint.classList.remove("is-on");
    if (!msgs.children.length) restore();
    setTimeout(function () { input.focus(); }, 400);
  }
  orb.addEventListener("click", openChat);
  hint.addEventListener("click", function (e) { if (e.target.closest(".chat-orb__hint-x")) return; openChat(); });
  hint.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openChat(); } });
  hint.querySelector(".chat-orb__hint-x").addEventListener("click", function (e) {
    e.stopPropagation(); hint.classList.remove("is-on");
    try { sessionStorage.setItem("tds-chat-hint", "1"); } catch (er) {}
  });
  root.querySelector(".chat-head__close").addEventListener("click", function () { document.body.classList.remove("chat-open"); });
  sendBtn.addEventListener("click", send);
  input.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
  input.addEventListener("input", function () { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 110) + "px"; });

  /* teaser popup, once per session */
  try {
    if (!sessionStorage.getItem("tds-chat-hint")) {
      setTimeout(function () { if (!document.body.classList.contains("chat-open")) hint.classList.add("is-on"); }, 3500);
      setTimeout(function () { hint.classList.remove("is-on"); try { sessionStorage.setItem("tds-chat-hint", "1"); } catch (er) {} }, 16000);
    }
  } catch (e) {}
})();
