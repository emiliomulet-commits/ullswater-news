#!/usr/bin/env python3
"""Ullswater Investments · EU Funding Events — static site generator.

Reads src/events/*.json and writes a complete static site to docs/.
Same model as news.ullswaterinvestments.com: plain server-side HTML, no JavaScript.
Usage: python3 src/build.py
"""
import json, html, datetime, pathlib, shutil, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src", ROOT / "docs"
KEY = "fbefbc9e1523d63695cbd540bb33e4b1"  # IndexNow
TODAY = datetime.date.fromisoformat(os.environ["TODAY"]) if os.environ.get("TODAY") else datetime.date.today()

SITE = dict(domain="events.ullswaterinvestments.com", url="https://events.ullswaterinvestments.com",
    name="EU Funding Events · Ullswater Investments", short="EU Funding Events", org="Ullswater Investments",
    org_legal="Ullswater Investments S.L.", org_url="https://www.ullswaterinvestments.com",
    news_url="https://news.ullswaterinvestments.com", book_url="https://www.ullswaterinvestments.com/investment-readiness",
    email="eufunding@ullswaterinvestments.com", address="Calle Ramírez de Arellano, 17, 28043 Madrid, Spain", address_brussels="Square de Meeûs 37, 1000 Brussels, Belgium",
    description="Horizon Europe info days and brokerage events to build consortia and prepare proposals, with dates, locations and official links, checked by Ullswater Investments.")

TYPES = {"info-day": ("Info days", "Info day", "Official briefings on EU funding calls and work programmes."),
         "brokerage": ("Brokerage", "Brokerage", "Partner-search and matchmaking events to build consortia."),
         "conference": ("Conferences", "Conference", "Major EU research and innovation gatherings."),
         "training": ("Training", "Training", "Training and proposal-preparation programmes."),
         "webinar": ("Webinars", "Webinar", "Online sessions on EU funding.")}
PROGS = {"horizon-europe": "Horizon Europe (general)", "cluster-1": "Cluster 1: Health", "cluster-2": "Cluster 2: Culture and Society",
         "cluster-3": "Cluster 3: Security", "cluster-4": "Cluster 4: Digital and Industry", "cluster-5": "Cluster 5: Climate, Energy and Mobility",
         "cluster-6": "Cluster 6: Food and Bioeconomy", "widera": "WIDERA", "eic": "European Innovation Council", "digital-europe": "Digital Europe", "other": "Other programmes"}
# Shared taxonomy (Nov 2026): every programme key maps to a theme page on calls.ullswaterinvestments.com,
# the single source for calls. Reference list: https://calls.ullswaterinvestments.com/data/taxonomy.json
CALLS = "https://calls.ullswaterinvestments.com"
THEME = {"cluster-1": "health", "cluster-2": "culture-society", "cluster-3": "civil-security", "cluster-4": "digital-industry-space",
         "cluster-5": "climate-energy-mobility", "cluster-6": "food-environment", "widera": "science-widening", "eic": "eic",
         "digital-europe": "digital-europe-defence", "other": "other-eu-programmes"}
def theme_url(k): return f"{CALLS}/theme/{THEME[k]}/" if k in THEME else f"{CALLS}/"
_TITLES = {}
def call_title(cid):
    """Call title from the calls site (falls back to the id when the feed is unavailable)."""
    if not _TITLES:
        try:
            import urllib.request
            req = urllib.request.Request(CALLS + "/data/calls.json", headers={"User-Agent": "UllswaterEventsBot/1.0"})
            _TITLES.update({c["id"]: c["title"] for c in json.load(urllib.request.urlopen(req, timeout=30))["calls"]})
        except Exception as e:
            print("calls titles unavailable:", e); _TITLES["_"] = ""
    return _TITLES.get(cid) or cid
<<<<<<< HEAD
=======
# "Apply with our support" form (Google Form, see ullswater-calls/tools/support_request_setup.gs). CALL and PAGE are replaced per page.
SUPPORT_FORM = ""
def support_link(label, page_url):
    from urllib.parse import quote
    if SUPPORT_FORM:
        return SUPPORT_FORM.replace("CALL", quote(label)).replace("PAGE", quote(page_url))
    return f"mailto:{SITE['email']}?subject={quote('Support request: ' + label)}&body={quote('Event/call: ' + label + chr(10) + 'Page: ' + page_url + chr(10) + chr(10) + 'Organisation, country and what you need:' + chr(10))}"
>>>>>>> 8bcd412 ("Apply with our support" button (support request form; mailto fallback until the form URL is set))
def call_url(cid):
    import re
    return f"{CALLS}/call/{re.sub(r'[^a-z0-9]+', '-', cid.lower()).strip('-')}/"
# Same network menu on www, calls, news and events
NETWORK = [("Home", "https://www.ullswaterinvestments.com/"), ("EU calls", CALLS + "/"), ("News", "https://news.ullswaterinvestments.com/"),
           ("Events", "https://events.ullswaterinvestments.com/"), ("Projects", "https://www.ullswaterinvestments.com/projects/"), ("About", "https://www.ullswaterinvestments.com/about/")]
def network(cur): return "".join(f'<a href="{u}"{" aria-current=page" if t == cur else ""}>{t}</a>' for t, u in NETWORK)
MODES = {"online": "Online", "onsite": "In person", "hybrid": "Hybrid"}
STATUS = {"scheduled": "", "applications-closed": "Applications closed", "cancelled": "Cancelled", "postponed": "Postponed"}

E = lambda s: html.escape(str(s), quote=True)
MON = ["January","February","March","April","May","June","July","August","September","October","November","December"]
def nice(d): return f"{d.day} {MON[d.month-1]} {d.year}"
def span(e):
    s, t = e["s"], e["e"]
    if s == t: return nice(s)
    if (s.year, s.month) == (t.year, t.month): return f"{s.day}–{t.day} {MON[s.month-1]} {s.year}"
    return f"{nice(s)} – {nice(t)}"

CSS = """
:root{--navy:#233567;--navy2:#1a2850;--gold:#c9a646;--ink:#1f2937;--muted:#4b5563;--line:#e5e7eb;--bg:#f5f6f8}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.6}
a{color:var(--navy)}a:hover{color:var(--navy2)}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header.site{background:var(--navy);color:#fff}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:64px;flex-wrap:wrap}
.brand{color:#fff;text-decoration:none;font-weight:800;font-size:18px;letter-spacing:.01em}.brand span{color:var(--gold);font-weight:600}
nav.cats{background:var(--navy2)}nav.cats .wrap{display:flex;gap:4px;overflow-x:auto;padding-top:6px;padding-bottom:6px}
nav.cats a{color:#dbe2f5;text-decoration:none;font-size:14px;padding:6px 10px;border-radius:6px;white-space:nowrap}
nav.cats a:hover,nav.cats a[aria-current]{background:rgba(255,255,255,.12);color:#fff}
.top-links a{color:#fff;font-size:14px;text-decoration:none;margin-left:16px;opacity:.9}
.hero{background:var(--bg);border-bottom:1px solid var(--line)}.hero .wrap{padding:40px 20px 32px}
.kicker{font-size:12px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:#8a6a1c;margin:0 0 8px}
h1{font-size:36px;line-height:1.2;margin:0 0 12px;color:var(--navy)}
.lead{font-size:18px;color:var(--muted);margin:0;max-width:760px}
.stats{display:flex;flex-wrap:wrap;gap:12px;margin:22px 0 0;padding:0;list-style:none}
.stats li{background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 16px;font-size:14px;color:var(--muted)}.stats strong{display:block;font-size:22px;color:var(--navy);line-height:1.2}
.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}
.btn{display:inline-block;background:var(--gold);color:var(--navy);font-weight:700;text-decoration:none;padding:10px 18px;border-radius:6px;white-space:nowrap}
.btn.ghost{background:#fff;border:1px solid var(--line);font-weight:600}
.month{padding:28px 0 4px}.month h2{color:var(--navy);font-size:24px;margin:0 0 12px}
.ev{display:grid;grid-template-columns:96px 1fr;gap:18px;border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:0 0 14px;background:#fff}
.date{background:var(--navy);color:#fff;border-radius:8px;text-align:center;padding:10px 6px;align-self:start}
.date b{display:block;font-size:22px;line-height:1.15}.date i{font-style:normal;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#dbe2f5}
.ev h3{font-size:19px;line-height:1.3;margin:0 0 4px}.ev h3 a{text-decoration:none}.ev p{margin:6px 0 0;color:var(--muted);font-size:15px}
.meta{font-size:13px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center}
.tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#fff;background:var(--navy);border-radius:4px;padding:3px 8px;text-decoration:none}
.tag.b{background:#8a6a1c}.tag.c{background:#555}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 0}.chips a{font-size:14px;border:1px solid var(--line);border-radius:999px;padding:4px 12px;text-decoration:none;background:#fff}
article.post{max-width:760px;margin:0 auto;padding:36px 20px 56px}article.post h1{font-size:34px}
.dek{font-size:19px;color:var(--muted);margin:0 0 16px}
.facts{background:var(--bg);border-left:4px solid var(--gold);border-radius:8px;padding:18px 22px;margin:24px 0}
.facts h2{font-size:15px;text-transform:uppercase;letter-spacing:.06em;margin:0 0 10px;color:var(--navy)}
.facts dl{display:grid;grid-template-columns:minmax(120px,170px) 1fr;gap:6px 16px;margin:0}.facts dt{font-weight:700;color:var(--navy)}.facts dd{margin:0}
.body p{font-size:17px;margin:0 0 16px}
.why{border-top:1px solid var(--line);margin-top:28px;padding-top:20px}.why h2,.src h2{font-size:20px;color:var(--navy);margin:0 0 8px}
.src{border:1px solid var(--line);border-radius:8px;padding:16px 20px;margin-top:24px}.src p{margin:0}
.cta{background:var(--navy);color:#fff;border-radius:10px;padding:22px 24px;margin:32px 0;display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.cta strong{font-size:18px}.cta p{margin:4px 0 0;color:#dbe2f5;font-size:15px}
.tags{margin-top:20px;display:flex;flex-wrap:wrap;gap:6px}.tags span{font-size:13px;background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:2px 10px;color:var(--muted)}
.crumbs{font-size:13px;color:var(--muted);margin-bottom:14px}.crumbs a{color:var(--muted)}
.notice{background:#fff4d6;border-radius:8px;padding:12px 16px;margin:16px 0}
.about{max-width:760px;margin:0 auto;padding:36px 20px 56px}.about p,.about li{font-size:17px}
footer.site{background:var(--navy);color:#dbe2f5;font-size:14px}footer.site .wrap{padding:28px 20px;display:flex;flex-wrap:wrap;gap:24px;justify-content:space-between}footer.site a{color:#fff}
@media(max-width:640px){h1,article.post h1{font-size:28px}.facts dl{grid-template-columns:1fr}.top-links{display:flex;overflow-x:auto;width:100%;padding-bottom:6px}.top-links a{margin:0 14px 0 0;white-space:nowrap}.ev{grid-template-columns:72px 1fr;gap:12px;padding:14px}.date b{font-size:18px}}
"""

def org_ld():
    return {"@type": "Organization", "@id": SITE["org_url"] + "/#org", "name": SITE["org"], "legalName": SITE["org_legal"], "url": SITE["org_url"], "email": SITE["email"],
            "logo": {"@type": "ImageObject", "url": SITE["url"] + "/assets/logo.png", "width": 512, "height": 512}}

def page(title, desc, path, body, ld=None, cur=None, noindex=False, og="website"):
    canon = SITE["url"] + path
    items = [("/", "All events", "home")] + [(f"/type/{k}/", TYPES[k][0], k) for k in TYPES if k in USED] + [("/calendar/", "Calendar", "calendar"), ("/past/", "Past events", "past")]
    navs = "".join(f'<a href="{h}"{" aria-current=page" if k == cur else ""}>{E(t)}</a>' for h, t, k in items)
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">
<meta name="robots" content="{'noindex, follow' if noindex else 'index, follow, max-snippet:-1, max-image-preview:large'}">
<meta property="og:site_name" content="{E(SITE['name'])}"><meta property="og:type" content="{og}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:locale" content="en_GB"><meta property="og:image" content="{SITE['url']}/assets/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{E(SITE['name'])}" href="{SITE['url']}/feed.xml"><link rel="icon" href="/assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style>{lds}</head><body>
<header class="site"><div class="wrap"><a class="brand" href="/">Ullswater Investments <span>· EU Funding Events</span></a>
<nav class="top-links" aria-label="Ullswater Investments sites">{network("Events")}</nav></div></header>
<nav class="cats" aria-label="Event types"><div class="wrap">{navs}</div></nav>
<main>{body}</main>
<footer class="site"><div class="wrap"><div><strong style="color:#fff">{E(SITE['org_legal'])}</strong><br>EU Funding Advisors · Madrid: {E(SITE['address'])} · Brussels: {E(SITE['address_brussels'])}<br><a href="mailto:{SITE['email']}">{SITE['email']}</a></div>
<div><a href="{SITE['org_url']}">ullswaterinvestments.com</a> · <a href="{SITE['news_url']}/">EU Funding News</a> · <a href="/about/">Editorial policy</a> · <a href="/sitemap.xml">Sitemap</a><br>© {TODAY.year} {E(SITE['org_legal'])}</div></div></footer>
</body></html>"""

def load():
    ev = []
    for f in sorted((SRC / "events").glob("*.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        e["s"], e["e"] = datetime.date.fromisoformat(e["start"]), datetime.date.fromisoformat(e["end"])
        e["old_path"] = f"/{e['s'].year}/{e['s'].month:02d}/{e['slug']}/"
        e["path"] = f"/events/{e['slug']}/"
        ev.append(e)
    return sorted(ev, key=lambda x: (x["s"], x["title"]))

def badge(e):
    st = STATUS.get(e.get("status", "scheduled"), "")
    return f'<span class="tag c">{E(st)}</span>' if st else ""

def card(e):
    return f"""<div class="ev"><div class="date"><b>{e['s'].day}{'–' + str(e['e'].day) if e['s'] != e['e'] and e['s'].month == e['e'].month else ''}</b><i>{MON[e['s'].month-1][:3]} {e['s'].year}</i></div>
<div><div class="meta"><a class="tag{' b' if e['type'] == 'brokerage' else ''}" href="/type/{e['type']}/">{E(TYPES[e['type']][1])}</a>{badge(e)}<span>{E(e['location'])}</span><span>{E(PROGS[e['programme']])}</span></div>
<h3><a href="{e['path']}">{E(e['title'])}</a></h3><p>{E(e['summary'])}</p></div></div>"""

def by_month(evs):
    out, cur = [], None
    for e in evs:
        k = (e["s"].year, e["s"].month)
        if k != cur:
            if cur: out.append("</section>")
            out.append(f'<section class="month"><h2>{MON[k[1]-1]} {k[0]}</h2>'); cur = k
        out.append(card(e))
    return "".join(out) + ("</section>" if cur else "")

def ics_esc(s): return str(s).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", " ")
def vevent(e):
    d1 = e["e"] + datetime.timedelta(days=1)
    return ["BEGIN:VEVENT", f"UID:{e['slug']}@{SITE['domain']}", f"DTSTAMP:{TODAY:%Y%m%d}T000000Z", f"DTSTART;VALUE=DATE:{e['s']:%Y%m%d}", f"DTEND;VALUE=DATE:{d1:%Y%m%d}",
            f"SUMMARY:{ics_esc(e['title'])}", f"LOCATION:{ics_esc(e['location'])}", f"DESCRIPTION:{ics_esc(e['summary'])}", f"URL:{SITE['url']}{e['path']}", "END:VEVENT"]
def ics(evs):
    return "\r\n".join(["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//{SITE['org']}//{SITE['short']}//EN", f"X-WR-CALNAME:{SITE['short']}"] + [l for e in evs for l in vevent(e)] + ["END:VCALENDAR", ""])

def event_ld(e):
    mode = {"online": "OnlineEventAttendanceMode", "onsite": "OfflineEventAttendanceMode", "hybrid": "MixedEventAttendanceMode"}[e["mode"]]
    place = {"@type": "Place", "name": e["location"], "address": {"@type": "PostalAddress", "addressLocality": e["city"]}} if e.get("city") else None
    virt = {"@type": "VirtualLocation", "url": e["registration_url"]}
    loc = [x for x in (place if e["mode"] != "online" else None, virt if e["mode"] != "onsite" else None) if x]
    st = {"cancelled": "EventCancelled", "postponed": "EventPostponed"}.get(e.get("status"), "EventScheduled")
    return {"@context": "https://schema.org", "@type": "Event", "name": e["title"], "description": e["summary"], "startDate": e["start"], "endDate": e["end"],
            "eventStatus": f"https://schema.org/{st}", "eventAttendanceMode": f"https://schema.org/{mode}", "location": loc if len(loc) > 1 else loc[0],
            "organizer": {"@type": "Organization", "name": e["organiser"]}, "url": SITE["url"] + e["path"], "image": SITE["url"] + "/assets/og.png"}

def related(e, events):
    """Links to the call page(s), the programme's open calls and the other sessions of the same series."""
    li = [f'<li><a href="{call_url(c)}">{E(call_title(c))}</a>: deadline, conditions and partners</li>' for c in e.get("calls", [])]
    li.append(f'<li><a href="{theme_url(e["programme"])}">Open calls: {E(PROGS[e["programme"]])}</a></li>')
    if e.get("series"):
        li.append(f'<li><a href="/series/{e["series"]}/">All sessions of this series</a></li>')
    return f'<section class="src"><h2>Related calls</h2><ul>{"".join(li)}</ul></section>'

def write(path, text):
    p = OUT / path.lstrip("/")
    if path.endswith("/"): p = p / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")

USED = set()

def build():
    events = load()
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(); shutil.copytree(SRC / "assets", OUT / "assets")
    write("/.nojekyll", ""); write("/CNAME", SITE["domain"] + "\n"); write(f"/{KEY}.txt", KEY)
    USED.update(e["type"] for e in events)
    up = [e for e in events if e["e"] >= TODAY]; past = [e for e in reversed(events) if e["e"] < TODAY]
    cta = f'<div class="cta"><div><strong>Going to an event to build a consortium?</strong><p>Ullswater Investments helps SMEs, start-ups and technology centres prepare EU funding proposals.</p></div><a class="btn" href="{SITE["book_url"]}">Talk to us</a></div>'
    site_ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": SITE["name"], "url": SITE["url"] + "/", "description": SITE["description"], "publisher": org_ld(),
                "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE["url"] + e["path"], "name": e["title"]} for i, e in enumerate(up)]}}]
    chips = "".join(f'<a href="/programme/{k}/">{E(v)}</a>' for k, v in PROGS.items() if any(e["programme"] == k for e in up))
    n = {t: sum(e["type"] == t for e in up) for t in TYPES}
    stats = f'<ul class="stats"><li><strong>{len(up)}</strong>upcoming events</li><li><strong>{n["info-day"]}</strong>info days</li><li><strong>{n["brokerage"]}</strong>brokerage events</li></ul>'
    write("/", page(f"EU funding events {TODAY.year}–{TODAY.year+1}: info days and brokerage · {SITE['org']}", SITE["description"], "/",
        f"""<section class="hero"><div class="wrap"><p class="kicker">EU Funding Events</p><h1>EU funding events: info days and brokerage</h1>
<p class="lead">Official info days and partner-search events to build consortia and prepare proposals for the 2027 calls. Dates and links checked {nice(TODAY)}.</p>{stats}
<div class="actions"><a class="btn" href="/calendar.ics">Add all to my calendar</a><a class="btn ghost" href="{CALLS}/closing-soon/">Call deadlines</a></div>
<nav class="chips" aria-label="Programmes">{chips}</nav></div></section><div class="wrap">{by_month(up)}{cta}</div>""", site_ld, cur="home"))
    for e in events:
        ended = e["e"] < TODAY
        noindex = ended and (TODAY - e["e"]).days > 90
        ended_note = '<div class="notice">This event has ended.</div>' if ended else ""
        st = STATUS.get(e.get("status", "scheduled"), "")
        rows = [("Date", span(e)), ("Type", TYPES[e["type"]][1]), ("Format", MODES[e["mode"]]), ("Location", e["location"]), ("Organiser", e["organiser"]), ("Programme", PROGS[e["programme"]])] + ([("Status", st)] if st else [])
        dl = "".join(f"<dt>{E(a)}</dt><dd>{E(b)}</dd>" for a, b in rows)
        reg = "" if ended or e.get("status") in ("applications-closed", "cancelled") else f'<a class="btn" href="{E(e["registration_url"])}" rel="noopener">Event page and registration</a>'
        write(e["path"] + "event.ics", ics([e]))
        write(e["path"], page(f"{e['title']} · {span(e)}", e["summary"], e["path"],
            f"""<article class="post"><div class="crumbs"><a href="/">Events</a> › <a href="/type/{e['type']}/">{E(TYPES[e['type']][0])}</a></div><h1>{E(e['title'])}</h1><p class="dek">{E(e['summary'])}</p>{ended_note}
<<<<<<< HEAD
<section class="facts"><h2>Key facts</h2><dl>{dl}</dl></section><div class="actions">{reg}<a class="btn ghost" href="{e['path']}event.ics">Add to calendar</a></div>
=======
<section class="facts"><h2>Key facts</h2><dl>{dl}</dl></section><div class="actions">{reg}<a class="btn ghost" href="{e['path']}event.ics">Add to calendar</a><a class="btn ghost" href="{E(support_link((call_title(e['calls'][0]) if e.get('calls') else e['title']), SITE['url'] + e['path']))}" target="_blank" rel="noopener">Apply with our support</a></div>
>>>>>>> 8bcd412 ("Apply with our support" button (support request form; mailto fallback until the form URL is set))
<div class="body" style="margin-top:24px">{''.join(f'<p>{E(p)}</p>' for p in e['details'])}</div>
<section class="why"><h2>Why it matters for applicants</h2><p>{E(e['why'])}</p></section>{related(e, events)}
<section class="src"><h2>Source</h2><p><a href="{E(e['source_url'])}" rel="noopener">{E(e['source_name'])}</a> — always confirm dates and registration on the organiser's page before you travel.</p></section>
<div class="tags">{''.join(f'<span>{E(t)}</span>' for t in e['tags'])}</div>{cta}</article>""", [event_ld(e)], cur=e["type"], noindex=noindex, og="article"))
    def listing(path, title, lead, evs, cur=None, noindex=False, calls_link=None):
        cl = f'<div class="actions"><a class="btn ghost" href="{calls_link}">See the related open calls →</a></div>' if calls_link else ""
        write(path, page(f"{title} · {SITE['short']}", lead, path, f'<section class="hero"><div class="wrap"><p class="kicker">EU Funding Events</p><h1>{E(title)}</h1><p class="lead">{E(lead)}</p>{cl}</div></section><div class="wrap">{by_month(evs) or "<p style=padding:28px_0>No upcoming events listed.</p>".replace("_"," ")}{cta}</div>', cur=cur, noindex=noindex or not evs))
    for k in USED: listing(f"/type/{k}/", f"EU funding events: {TYPES[k][0].lower()}", TYPES[k][2], [e for e in up if e["type"] == k], k)
    for k in {e["programme"] for e in events}: listing(f"/programme/{k}/", f"{PROGS[k]} events", f"Upcoming EU funding events for {PROGS[k]}.", [e for e in up if e["programme"] == k], calls_link=theme_url(k))
    for k in {e["series"] for e in events if e.get("series")}:
        sv = [e for e in events if e.get("series") == k]
        listing(f"/series/{k}/", sv[0].get("series_title", k), f"All sessions of the series, in date order.", [e for e in sv if e["e"] >= TODAY], calls_link=call_url(sv[0]["calls"][0]) if sv[0].get("calls") else None)
    listing("/past/", "Past EU funding events", "Events already held, kept for reference.", past, "past", noindex=not past)
    write("/calendar/", page(f"EU funding events calendar · {SITE['short']}", "Calendar of upcoming EU funding events, by month, with a subscription file for your own calendar.", "/calendar/",
        f'<section class="hero"><div class="wrap"><p class="kicker">Calendar</p><h1>EU funding events calendar</h1><p class="lead">{len(up)} upcoming events by month. Add them all to Outlook, Google Calendar or Apple Calendar.</p><div class="actions"><a class="btn" href="/calendar.ics">Download calendar file</a></div></div></section><div class="wrap">{by_month(up)}</div>', cur="calendar"))
    write("/calendar.ics", ics(up))
    write("/_redirects", "".join(f"{e['old_path']} {e['path']} 301\n{e['old_path']}event.ics {e['path']}event.ics 301\n" for e in events))
    # Machine-readable feed (used by calls.ullswaterinvestments.com to show events per call)
    feed = [{k: e.get(k) for k in ("slug", "title", "start", "end", "type", "programme", "mode", "location", "organiser", "summary", "registration_url", "status")}
            | {"url": SITE["url"] + e["path"], "theme": THEME.get(e["programme"]), "calls": e.get("calls", [])} for e in up]
    write("/events.json", json.dumps({"updated": str(TODAY), "events": feed}, ensure_ascii=False, indent=1, default=str))
    write("/about/", page(f"About and editorial policy · {SITE['short']}", "How Ullswater Investments selects and checks the EU funding events listed on this site.", "/about/",
        f"""<div class="about"><h1>About EU Funding Events</h1><p>EU Funding Events is published by {E(SITE['org_legal'])}, a Madrid-based European funding advisory firm. It lists events that help companies, researchers and consortia prepare EU funding proposals.</p>
<h2>How events are checked</h2><ul><li>Every event links to the organiser's page or to a recognised National Contact Point or partner source.</li><li>Dates, locations and formats are checked against that source before publication.</li><li>Our comments on why an event matters are analysis and add no new facts.</li><li>Always confirm details with the organiser before registering or travelling.</li></ul>
<p>Corrections: <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p></div>"""))
    write("/404.html", page(f"Page not found · {SITE['short']}", "Page not found.", "/404.html", '<div class="about"><h1>Page not found</h1><p><a href="/">See upcoming EU funding events</a>.</p></div>', noindex=True))
    urls = [("/", TODAY.isoformat()), ("/calendar/", TODAY.isoformat()), ("/about/", TODAY.isoformat())] + [(f"/type/{k}/", TODAY.isoformat()) for k in sorted(USED) if any(e["type"] == k for e in up)] + \
           [(f"/programme/{k}/", TODAY.isoformat()) for k in sorted({e["programme"] for e in up})] + [(f"/series/{k}/", TODAY.isoformat()) for k in sorted({e["series"] for e in up if e.get("series")})] + \
           [(e["path"], TODAY.isoformat()) for e in events if not (e["e"] < TODAY and (TODAY - e["e"]).days > 90)]
    write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{SITE['url']}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls) + "</urlset>\n")
    bots = ["*", "Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "GPTBot", "PerplexityBot", "ClaudeBot", "Claude-SearchBot", "Claude-User", "Google-Extended", "Applebot", "DuckDuckBot"]
    write("/robots.txt", f"# {SITE['name']}\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {SITE['url']}/sitemap.xml\n")
    write("/llms.txt", "\n".join([f"# {SITE['name']}", "", f"> {SITE['description']}", "", "## Upcoming events", ""] + [f"- [{e['title']}]({SITE['url']}{e['path']}): {span(e)}, {e['location']}." for e in up] + ["", "## Related", "", f"- [EU Funding News]({SITE['news_url']}/)", f"- [Open EU funding calls]({CALLS}/)", ""]))
    from email.utils import format_datetime
    now = format_datetime(datetime.datetime.now(datetime.timezone.utc))
    write("/feed.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{E(SITE["name"])}</title><link>{SITE["url"]}/</link><description>{E(SITE["description"])}</description><language>en</language><lastBuildDate>{now}</lastBuildDate>' +
          "".join(f'<item><title>{E(e["title"])}</title><link>{SITE["url"]}{e["path"]}</link><guid>{SITE["url"]}{e["path"]}</guid><description>{E(span(e) + ". " + e["summary"])}</description></item>' for e in up) + "</channel></rss>\n")
    print(f"Built {len(events)} events ({len(up)} upcoming) -> {OUT}")

if __name__ == "__main__":
    build()
