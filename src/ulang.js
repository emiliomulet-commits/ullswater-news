/* ulang — shared default-language rule for every Ullswater site (www, news, events, project landings).
   Same file inlined in the <head> of each site; master copy: ullswater-www/scripts/ulang.js.
   1. ?lang=en|es in the URL, or the visitor's own choice (EN/ES click, cookie "ulang", shared by all
      *.ullswaterinvestments.com subdomains, 1 year) always wins.
   2. Otherwise the visitor's country (Cloudflare /cdn-cgi/trace, cached 7 days in cookie "ucc"):
      Spain, Spanish-speaking Latin America, Puerto Rico and Equatorial Guinea -> Spanish; anywhere else -> English.
      If the country cannot be read, the browser language decides.
   3. Search engines and AI crawlers are never redirected, so every URL (EN and /es/) stays indexable.
   Path sites (/es/ twins): jumps to the <link rel="alternate" hreflang> twin, only if the page has one.
   Toggle sites (<html data-lang>, EN/ES in one page): sets data-lang and fires "ulang:change". */
(function (w, d) {
  var ES = " ES MX CO AR PE VE CL EC GT CU BO DO HN PY SV NI CR PA UY PR GQ ";
  var BOT = /bot|crawl|spider|slurp|archiver|preview|facebookexternalhit|lighthouse|headless|google-|chatgpt|gptbot|claude|anthropic|perplexity|bytespider|yandex|baidu|duckduck|applebot|petal|semrush|ahrefs/i;
  var html = d.documentElement, toggle = html.hasAttribute("data-lang"), YEAR = 31536000, timer;
  var shared = /(^|\.)ullswaterinvestments\.com$/.test(location.hostname);
  function get(n) { var m = d.cookie.match(new RegExp("(?:^|; )" + n + "=([^;]*)")); return m ? m[1] : null; }
  function put(n, v, age) { d.cookie = n + "=" + v + ";path=/;max-age=" + age + ";SameSite=Lax" + (shared ? ";domain=.ullswaterinvestments.com" : ""); }
  function cur() { return ((toggle ? html.getAttribute("data-lang") : html.getAttribute("lang")) || "en").slice(0, 2); }
  function reveal() { clearTimeout(timer); html.classList.remove("ulang-wait"); }
  function fromBrowser() { return /^es\b/i.test(navigator.language || "") ? "es" : "en"; }
  function fromCountry(c) { return !c || c === "XX" || c === "T1" ? fromBrowser() : ES.indexOf(" " + c + " ") >= 0 ? "es" : "en"; }
  function apply(l) {
    if (l !== "en" && l !== "es") return reveal();
    w.ULANG.lang = l;
    if (l === cur()) return reveal();
    if (toggle) {
      html.setAttribute("data-lang", l); html.setAttribute("lang", l);
      try { d.dispatchEvent(new CustomEvent("ulang:change", { detail: l })); } catch (e) {}
      return reveal();
    }
    var a = d.querySelector('link[rel="alternate"][hreflang="' + l + '"]');
    if (!a && d.readyState === "loading" && !apply.waited) {    /* <head> links not parsed yet */
      apply.waited = 1; html.classList.add("ulang-wait"); clearTimeout(timer); timer = setTimeout(reveal, 900);
      return d.addEventListener("DOMContentLoaded", function () { apply(l); });
    }
    if (a) {
      var p = a.getAttribute("href").replace(/^https?:\/\/[^\/]+/, "") || "/";
      if (p !== location.pathname) { location.replace(p + location.search + location.hash); return; }
    }
    reveal();
  }
  w.ULANG = { lang: null, save: function (l) { if (l === "en" || l === "es") put("ulang", l, YEAR); } };
  /* any EN/ES control on any site records the visitor's choice */
  d.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".lang a, .lang button");
    if (b) w.ULANG.save((b.getAttribute("data-l") || b.getAttribute("data-lang") || b.getAttribute("hreflang") || b.getAttribute("lang") || "").slice(0, 2));
  }, true);
  if (BOT.test(navigator.userAgent || "") || navigator.webdriver) return;
  var q = (location.search.match(/[?&]lang=(en|es)\b/) || [])[1];
  if (q) w.ULANG.save(q);
  var pref = q || get("ulang");
  if (pref === "en" || pref === "es") return apply(pref);
  var cc = get("ucc");
  if (cc) return apply(fromCountry(cc));
  html.classList.add("ulang-wait");                 /* hide for a moment instead of flashing the wrong language */
  timer = setTimeout(reveal, 900);
  try {
    fetch("/cdn-cgi/trace", { cache: "no-store" }).then(function (r) { return r.text(); }).then(function (t) {
      var c = (t.match(/^loc=([A-Z0-9]{2})$/m) || [])[1] || "XX";
      put("ucc", c, 604800); apply(fromCountry(c));
    }).catch(function () { apply(fromBrowser()); });
  } catch (e) { apply(fromBrowser()); }
})(window, document);
