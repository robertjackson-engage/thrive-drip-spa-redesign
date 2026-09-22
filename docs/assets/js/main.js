/* ThrIVe Drip Spa — interactions */
(function () {
  "use strict";

  var docEl = document.documentElement;
  docEl.classList.add("js");

  /* ---------- guest / member view ---------- */
  function setView(v) {
    docEl.setAttribute("data-view", v);
    try { localStorage.setItem("tds-view", v); } catch (e) {}
  }
  document.querySelectorAll("[data-view-set]").forEach(function (b) {
    b.addEventListener("click", function () { setView(b.getAttribute("data-view-set")); });
  });

  /* ---------- utility bar dismiss ---------- */
  var utilX = document.querySelector(".util-bar__x");
  if (utilX) utilX.addEventListener("click", function () {
    docEl.classList.add("no-util");
    try { sessionStorage.setItem("tds-util", "1"); } catch (e) {}
  });

  /* ---------- preloader (once per session) ---------- */
  var pre = document.querySelector(".preloader");
  var skipIntro = docEl.classList.contains("no-preloader");
  function reveal() { document.body.classList.add("is-loaded"); }

  if (!pre || skipIntro) {
    if (pre) pre.remove();
    requestAnimationFrame(function () { requestAnimationFrame(reveal); });
  } else {
    var bar = pre.querySelector(".preloader__bar i");
    var t0 = null, INTRO_MS = 1100, done = false;
    function tick(t) {
      if (done) return;
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / INTRO_MS, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      if (bar) bar.style.transform = "scaleX(" + eased + ")";
      if (p < 1) requestAnimationFrame(tick); else setTimeout(introDone, 150);
    }
    function introDone() {
      if (done) return;
      done = true;
      if (bar) bar.style.transform = "scaleX(1)";
      pre.classList.add("is-done");
      reveal();
      try { sessionStorage.setItem("tds-intro", "1"); } catch (e) {}
      setTimeout(function () { pre.remove(); }, 1000);
    }
    requestAnimationFrame(tick);
    setTimeout(introDone, INTRO_MS + 1200); /* rAF pauses in background tabs */
  }

  /* ---------- page-to-page fade ---------- */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href]");
    if (!a || a.target || e.metaKey || e.ctrlKey || e.shiftKey) return;
    var href = a.getAttribute("href");
    if (!href || href.charAt(0) === "#" || /^(https?:|tel:|mailto:|sms:)/.test(href)) return;
    var url = new URL(a.href, location.href);
    if (url.pathname === location.pathname && url.hash) return;
    e.preventDefault();
    document.body.classList.remove("menu-open");
    document.body.classList.add("page-exit");
    setTimeout(function () { location.href = a.href; }, 260);
  });
  window.addEventListener("pageshow", function (ev) {
    if (ev.persisted) { document.body.classList.remove("page-exit"); document.body.classList.add("is-loaded"); }
  });

  /* smooth scrolling only after the page settles — entry positioning is instant */
  window.addEventListener("load", function () {
    setTimeout(function () { docEl.classList.add("smooth-scroll"); }, 80);
  });

  /* ---------- header ---------- */
  var header = document.querySelector(".site-header");
  function onScrollHeader() { if (header) header.classList.toggle("is-scrolled", window.scrollY > 40); }
  window.addEventListener("scroll", onScrollHeader, { passive: true });
  onScrollHeader();

  /* dropdown nav: hover on desktop, tap-to-open on touch */
  document.querySelectorAll(".nav-item > a").forEach(function (a) {
    a.addEventListener("click", function (e) {
      var item = a.parentElement;
      if (window.matchMedia("(hover: none)").matches && !item.classList.contains("is-open")) {
        e.preventDefault();
        document.querySelectorAll(".nav-item.is-open").forEach(function (o) { o.classList.remove("is-open"); });
        item.classList.add("is-open");
      }
    });
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".nav-item")) document.querySelectorAll(".nav-item.is-open").forEach(function (o) { o.classList.remove("is-open"); });
  });

  /* ---------- menu overlay ---------- */
  var toggle = document.querySelector(".menu-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.querySelectorAll(".menu-list a").forEach(function (a, i) {
        a.style.transitionDelay = open ? 0.15 + i * 0.04 + "s" : "0s";
      });
    });
  }
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") document.body.classList.remove("menu-open"); });

  /* ---------- reveal on scroll ---------- */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
  }, { threshold: 0.1, rootMargin: "0px 0px -6% 0px" });
  document.querySelectorAll(".reveal, .reveal-img, [data-stagger]").forEach(function (el) { io.observe(el); });

  /* ---------- counters ---------- */
  var cio = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      var el = en.target; cio.unobserve(el);
      var target = parseFloat(el.getAttribute("data-count")), dur = 1600, t0 = null;
      function tick(t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / dur, 1), eased = 1 - Math.pow(1 - p, 4);
        el.textContent = Math.round(target * eased).toLocaleString();
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.5 });
  document.querySelectorAll("[data-count]").forEach(function (el) { cio.observe(el); });

  /* ---------- parallax on CTA bands ---------- */
  var pxItems = Array.prototype.slice.call(document.querySelectorAll(".cta-band__media img"));
  var ticking = false;
  function parallax() {
    var vh = window.innerHeight;
    pxItems.forEach(function (el) {
      var r = el.parentElement.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) return;
      var p = (r.top + r.height / 2 - vh / 2) / (vh / 2 + r.height / 2);
      el.style.transform = "translateY(" + (-p * 14).toFixed(2) + "px)";
    });
    ticking = false;
  }
  if (pxItems.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    window.addEventListener("scroll", function () { if (!ticking) { requestAnimationFrame(parallax); ticking = true; } }, { passive: true });
    parallax();
  }

  /* ---------- accordion ---------- */
  document.querySelectorAll(".acc__item").forEach(function (item) {
    var head = item.querySelector(".acc__head"), body = item.querySelector(".acc__body");
    head.addEventListener("click", function () {
      var isOpen = item.classList.contains("is-open");
      item.closest(".acc").querySelectorAll(".acc__item.is-open").forEach(function (o) {
        o.classList.remove("is-open"); o.querySelector(".acc__body").style.maxHeight = "0px";
        o.querySelector(".acc__head").setAttribute("aria-expanded", "false");
      });
      if (!isOpen) { item.classList.add("is-open"); body.style.maxHeight = body.scrollHeight + "px"; head.setAttribute("aria-expanded", "true"); }
    });
  });

  /* ---------- testimonial slider ---------- */
  document.querySelectorAll(".t-slider").forEach(function (slider) {
    var track = slider.querySelector(".t-slider__track"), slides = track.children.length, idx = 0, auto;
    function go(n) { idx = (n + slides) % slides; track.style.transform = "translateX(-" + idx * 100 + "%)"; }
    slider.querySelectorAll("[data-dir]").forEach(function (b) {
      b.addEventListener("click", function () {
        go(idx + (b.getAttribute("data-dir") === "next" ? 1 : -1));
        clearInterval(auto); auto = setInterval(function () { go(idx + 1); }, 7000);
      });
    });
    auto = setInterval(function () { go(idx + 1); }, 7000);
  });

  /* ---------- floating labels for selects ---------- */
  document.querySelectorAll(".field select").forEach(function (s) {
    function mark() { s.closest(".field").classList.toggle("has-value", !!s.value); }
    s.addEventListener("change", mark); mark();
  });

  /* ---------- demo submit ---------- */
  document.querySelectorAll("form[data-demo]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = f.querySelector("button[type=submit]");
      if (btn) {
        var txt = btn.innerHTML;
        btn.innerHTML = "Got it — we'll be in touch shortly";
        btn.disabled = true;
        setTimeout(function () { btn.innerHTML = txt; btn.disabled = false; f.reset(); }, 4200);
      }
    });
  });

  /* ---------- lazy video poster → iframe ---------- */
  document.querySelectorAll(".video-feature__poster[data-yt]").forEach(function (p) {
    p.addEventListener("click", function () {
      var id = p.getAttribute("data-yt");
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
      f.allow = "autoplay; encrypted-media; picture-in-picture"; f.allowFullscreen = true;
      f.title = "Video";
      p.replaceWith(f);
    });
  });

  /* ---------- hero video: respect data saver ---------- */
  var heroVid = document.querySelector(".hero__media video, .hero__bg video");
  if (heroVid && navigator.connection && navigator.connection.saveData) { heroVid.removeAttribute("autoplay"); heroVid.pause(); }
})();
