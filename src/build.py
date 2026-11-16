#!/usr/bin/env python3
"""Ullswater Investments · EU Funding News — static site generator.

Reads src/articles/*.json and writes a complete static site to docs/
(served by GitHub Pages at https://news.ullswaterinvestments.com).
Every page is plain server-side HTML: no JavaScript is needed to read it,
so search engines and AI crawlers see the full text on the first request.

Usage:  python3 src/build.py
"""
import json, html, datetime, pathlib, shutil, re, os, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from calls import load_calls, GROUPS
from redirects import CALLS, TITLES, calls_slug, live_ids, call_url, theme_url, stub
from email.utils import format_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "docs"

SITE = {
    "domain": "news.ullswaterinvestments.com",
    "url": "https://news.ullswaterinvestments.com",
    "name": "EU Funding News · Ullswater Investments",
    "short": "EU Funding News",
    "org": "Ullswater Investments",
    "org_legal": "Ullswater Investments S.L.",
    "org_url": "https://www.ullswaterinvestments.com",
    "book_url": "https://www.ullswaterinvestments.com/investment-readiness",
    "email": "eufunding@ullswaterinvestments.com",
    "address": "Calle Ramírez de Arellano, 17, 28043 Madrid, Spain",
    "address_brussels": "Square de Meeûs 37, 1000 Brussels, Belgium",
    "description": "Daily, verified news on European funding for innovators, researchers and SMEs: Horizon Europe, EIC, Digital Europe, defence, cohesion funds and Spanish R&D grants, with links to the official sources.",
}

# Shared taxonomy (Nov 2026): news categories -> theme pages on calls.ullswaterinvestments.com
# (reference list: https://calls.ullswaterinvestments.com/data/taxonomy.json)
CAT_CALLS = {"digital-ai": ("/theme/digital-industry-space/", "Open digital and AI calls"), "eic-defence": ("/theme/eic/", "Open EIC calls"),
             "climate-energy": ("/theme/climate-energy-mobility/", "Open climate, energy and mobility calls"), "health": ("/theme/health/", "Open health calls"),
             "spain": ("/spain/", "Open Spanish national and regional calls"), "horizon-europe": ("/", "All open EU calls")}
# Same network menu on www, calls, news and events
NETWORK = [("Home", "https://www.ullswaterinvestments.com/"), ("EU calls", "https://calls.ullswaterinvestments.com/"), ("News", "https://news.ullswaterinvestments.com/"),
           ("Events", "https://events.ullswaterinvestments.com/"), ("Projects", "https://www.ullswaterinvestments.com/projects/"), ("About", "https://www.ullswaterinvestments.com/about/")]
# Spanish menu: www, news and events have /es/ versions; calls.ullswaterinvestments.com stays in English only.
NETWORK_ES = [("Inicio", "https://www.ullswaterinvestments.com/es/"), ("Convocatorias UE", "https://calls.ullswaterinvestments.com/"), ("Noticias", "https://news.ullswaterinvestments.com/es/"),
              ("Eventos", "https://events.ullswaterinvestments.com/es/"), ("Proyectos", "https://www.ullswaterinvestments.com/es/projects/"), ("Quiénes somos", "https://www.ullswaterinvestments.com/es/about/")]
def network(cur):
    items = NETWORK_ES if ES() else NETWORK
    return "".join(f'<a href="{u}"{" aria-current=page" if i == [t for t, _ in NETWORK].index(cur) else ""}>{t}</a>' for i, (t, u) in enumerate(items))

AUTHOR = {
    "name": "Emilio Mulet",
    "slug": "emilio-mulet",
    "role": "Managing Partner, Ullswater Investments",
    "bio": [
        "Emilio Mulet is Managing Partner (Socio Director) of Ullswater Investments, a Madrid-based European funding advisory and venture-building firm.",
        "He advises companies and consortia on EU and Spanish R&D funding, including Horizon Europe, CDTI, Red.es and ENISA instruments, and on the management of funded projects.",
        "His practice is built around federated data spaces: he has worked on three SEDIA-funded European data space demonstrators — Global Data Care (health), PROCUREDATA (public procurement) and EcoDataNet (circular economy) — and on Gaia-X, IDSA and ODRL-based data-sharing architectures.",
    ],
    "knows": ["EU funding", "Horizon Europe", "European Innovation Council", "CDTI", "Red.es", "ENISA", "Federated data spaces", "Gaia-X", "Sovereign AI"],
}
AUTHOR_PATH = f"/author/{AUTHOR['slug']}/"

CATEGORIES = {
    "horizon-europe": ("Horizon Europe", "Calls, work programmes and results under Horizon Europe, the EU research and innovation programme."),
    "digital-ai": ("Digital & AI", "EU funding for artificial intelligence, data spaces, digital infrastructure and Digital Europe."),
    "eic-defence": ("EIC, Defence & Equity", "European Innovation Council, STEP, European Defence Fund and EU equity instruments."),
    "research-policy": ("Research Policy", "European Research Area, open science and the rules that shape EU-funded research."),
    "budget-policy": ("EU Budget & Policy", "The EU budget, the 2028–2034 MFF, FP10 and the policy behind EU funding."),
    "spain": ("Spain", "Spanish R&D and innovation funding: CDTI, AEI, Red.es, ENISA and NextGenerationEU."),
    "climate-energy": ("Climate & Energy", "Innovation Fund, LIFE, clean energy and climate funding."),
    "health": ("Health & Health Data", "EU4Health, Horizon Europe Health and the European Health Data Space."),
}
CATEGORIES_ES = {
    "horizon-europe": ("Horizonte Europa", "Convocatorias, programas de trabajo y resultados de Horizonte Europa, el programa de investigación e innovación de la UE."),
    "digital-ai": ("Digital e IA", "Financiación europea para inteligencia artificial, espacios de datos, infraestructura digital y Europa Digital."),
    "eic-defence": ("EIC, defensa y capital", "Consejo Europeo de Innovación, STEP, Fondo Europeo de Defensa e instrumentos de capital de la UE."),
    "research-policy": ("Política de investigación", "Espacio Europeo de Investigación, ciencia abierta y las normas de la investigación financiada por la UE."),
    "budget-policy": ("Presupuesto y política UE", "El presupuesto de la UE, el MFP 2028–2034, el FP10 y la política detrás de la financiación europea."),
    "spain": ("España", "Financiación española de I+D+i: CDTI, AEI, Red.es, ENISA y NextGenerationEU."),
    "climate-energy": ("Clima y energía", "Fondo de Innovación, LIFE, energía limpia y financiación climática."),
    "health": ("Salud y datos sanitarios", "EU4Health, Horizonte Europa Salud y el Espacio Europeo de Datos Sanitarios."),
}
def CAT(k): return (CATEGORIES_ES if ES() else CATEGORIES)[k]
SITE_ES = {
    "name": "Noticias de financiación europea · Ullswater Investments",
    "short": "Noticias de financiación UE",
    "description": "Noticias diarias y verificadas sobre financiación europea para innovadores, investigadores y pymes: Horizonte Europa, EIC, Europa Digital, defensa, fondos de cohesión y ayudas españolas de I+D, con enlace a las fuentes oficiales.",
    "book_url": "https://www.ullswaterinvestments.com/es/investment-readiness/",
}
def S(k): return SITE_ES.get(k, SITE[k]) if ES() else SITE[k]
AUTHOR_ES = {
    "role": "Socio Director, Ullswater Investments",
    "bio": [
        "Emilio Mulet es Socio Director de Ullswater Investments, firma de asesoramiento en financiación europea y creación de empresas con sede en Madrid.",
        "Asesora a empresas y consorcios en financiación europea y española de I+D, incluidos Horizonte Europa y los instrumentos del CDTI, Red.es y ENISA, y en la gestión de proyectos financiados.",
        "Su actividad gira en torno a los espacios de datos federados: ha trabajado en tres demostradores europeos de espacios de datos financiados por la SEDIA —Global Data Care (salud), PROCUREDATA (contratación pública) y EcoDataNet (economía circular)— y en arquitecturas de intercambio de datos basadas en Gaia-X, IDSA y ODRL.",
    ],
}
def A(k): return AUTHOR_ES.get(k, AUTHOR[k]) if ES() else AUTHOR[k]
CAT_CALLS_ES = {"digital-ai": "Convocatorias abiertas de digital e IA", "eic-defence": "Convocatorias abiertas del EIC", "climate-energy": "Convocatorias abiertas de clima, energía y movilidad",
                "health": "Convocatorias abiertas de salud", "spain": "Convocatorias abiertas nacionales y regionales en España", "horizon-europe": "Todas las convocatorias abiertas de la UE"}

E = lambda s: html.escape(str(s), quote=True)
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]

# ---- Bilingual site (Nov 2026): English at /, Spanish at /es/ ----
# Each article/video JSON may carry an "es" block with the Spanish text of
# title, dek, key_facts, body, why, tags, summary and action.label.
LANG = "en"
def ES(): return LANG == "es"
def nice(d): return f"{d.day} de {MESES[d.month-1]} de {d.year}" if ES() else f"{d.day} {MONTHS[d.month-1]} {d.year}"
def P(path):
    """Internal path in the current language."""
    return ("/es" + path) if ES() and path.startswith("/") else path
def F(a, key, default=None):
    """Field of an article/video in the current language (falls back to English)."""
    if ES():
        v = (a.get("es") or {}).get(key)
        if v: return v
    return a.get(key, default)
def has_es(a): return bool((a.get("es") or {}).get("title"))
UI = {  # English → Spanish interface strings
    "News": "Noticias", "Videos": "Vídeos", "Category": "Categoría", "Source": "Fuente", "Published": "Publicado el", "By": "Por",
    "Key facts": "Datos clave", "Why it matters": "Por qué importa", "Official source": "Fuente oficial",
    "— always check eligibility, budgets and deadlines on the official page before applying.": "— comprueba siempre la elegibilidad, los presupuestos y los plazos en la página oficial antes de solicitar.",
    "Related calls": "Convocatorias relacionadas", ": deadline, conditions and partners": ": plazo, condiciones y socios", "Apply with our support": "Solicítala con nuestro apoyo",
    "Preparing a proposal?": "¿Preparando una propuesta?", "Ullswater Investments helps companies match, prepare and submit EU funding applications.": "Ullswater Investments ayuda a las empresas a encontrar, preparar y presentar solicitudes de financiación europea.",
    "EU funding advisor.": "Asesor de financiación europea.", "Related news": "Noticias relacionadas", "More videos": "Más vídeos", "Why watch it": "Por qué verlo",
    "Video": "Vídeo", "Video by": "Vídeo de", "Event": "Evento", "Embedded from YouTube.": "Insertado desde YouTube.", "Watch on YouTube ↗": "Ver en YouTube ↗",
    "Updated": "Actualizado el", "articles": "noticias", "Every article links to its official source.": "Cada noticia enlaza a su fuente oficial.",
    "Closing in the next": "Cierran en los próximos", "days": "días", "All deadlines →": "Todos los plazos →",
    "Call": "Convocatoria", "Programme": "Programa", "Deadline": "Plazo", "Status": "Estado", "Open": "Abierta", "Forthcoming": "Próxima", "Closed": "Cerrada",
    "EU Funding Advisors": "Asesores de financiación europea", "Editorial policy": "Política editorial", "Author": "Autor", "Latest articles": "Últimas noticias",
    "Contact": "Contacto", "Categories": "Categorías", "Page not found": "Página no encontrada", "Language": "Idioma",
    "This news item is only available in English for now.": "Esta noticia de momento solo está disponible en inglés.",
}
def T(s): return UI.get(s, s) if ES() else s

CSS = """
:root{--navy:#233567;--navy2:#1a2850;--gold:#c9a646;--ink:#1f2937;--muted:#4b5563;--line:#e5e7eb;--bg:#f5f6f8}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.6}
a{color:var(--navy)}a:hover{color:var(--navy2)}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header.site{background:var(--navy);color:#fff}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:64px;flex-wrap:wrap}
.brand{color:#fff;text-decoration:none;font-weight:800;font-size:18px;letter-spacing:.01em}
.brand span{color:var(--gold);font-weight:600}
nav.cats{background:var(--navy2)}
nav.cats .wrap{display:flex;gap:4px;overflow-x:auto;padding-top:6px;padding-bottom:6px}
nav.cats a{color:#dbe2f5;text-decoration:none;font-size:14px;padding:6px 10px;border-radius:6px;white-space:nowrap}
nav.cats a:hover,nav.cats a[aria-current]{background:rgba(255,255,255,.12);color:#fff}
.top-links a{color:#fff;font-size:14px;text-decoration:none;margin-left:16px;opacity:.9}
.hdr-r{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.lang{display:flex;flex-shrink:0;border:1px solid rgba(255,255,255,.35);border-radius:6px;overflow:hidden;font-size:13px;font-weight:700}.lang a{color:#e6ebf7;text-decoration:none;padding:6px 9px;letter-spacing:.04em}.lang a[aria-current]{background:var(--gold);color:var(--navy)}.lang a:not([aria-current]):hover{background:rgba(255,255,255,.12)}
.hero{background:var(--bg);border-bottom:1px solid var(--line)}
.hero .wrap{padding:40px 20px 32px}
.kicker{font-size:12px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:#8a6a1c;margin:0 0 8px}
h1{font-size:36px;line-height:1.2;margin:0 0 12px;color:var(--navy)}
.lead{font-size:18px;color:var(--muted);margin:0;max-width:760px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:24px;padding:32px 0 48px}
.card{border:1px solid var(--line);border-radius:10px;padding:22px;background:#fff;display:flex;flex-direction:column;gap:8px}
.card h2{font-size:20px;line-height:1.3;margin:0}.card h2 a{text-decoration:none}
.card p{margin:0;color:var(--muted);font-size:15px}
.meta{font-size:13px;color:var(--muted)}
.tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#fff;background:var(--navy);border-radius:4px;padding:3px 8px;text-decoration:none}
article.post{max-width:760px;margin:0 auto;padding:36px 20px 56px}
article.post h1{font-size:34px}
.dek{font-size:19px;color:var(--muted);margin:0 0 16px}
.facts{background:var(--bg);border-left:4px solid var(--gold);border-radius:8px;padding:18px 22px;margin:24px 0}
.facts h2{font-size:15px;text-transform:uppercase;letter-spacing:.06em;margin:0 0 10px;color:var(--navy)}
.facts dl{display:grid;grid-template-columns:minmax(120px,190px) 1fr;gap:6px 16px;margin:0}
.facts dt{font-weight:700;color:var(--navy)}.facts dd{margin:0}
.body p{font-size:17px;margin:0 0 16px}
.why{border-top:1px solid var(--line);margin-top:28px;padding-top:20px}
.why h2,.src h2{font-size:20px;color:var(--navy);margin:0 0 8px}
.src{background:#fff;border:1px solid var(--line);border-radius:8px;padding:16px 20px;margin-top:24px}
.src p{margin:0}.act{margin:14px 0 0!important}.act .btn{display:inline-block}
.cta{background:var(--navy);color:#fff;border-radius:10px;padding:22px 24px;margin-top:32px;display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.cta strong{font-size:18px}.cta p{margin:4px 0 0;color:#dbe2f5;font-size:15px}
.btn{background:var(--gold);color:var(--navy);font-weight:700;text-decoration:none;padding:10px 18px;border-radius:6px;white-space:nowrap}
.tags{margin-top:20px;display:flex;flex-wrap:wrap;gap:6px}.tags span{font-size:13px;background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:2px 10px;color:var(--muted)}
.crumbs{font-size:13px;color:var(--muted);margin-bottom:14px}.crumbs a{color:var(--muted)}
footer.site{background:var(--navy);color:#dbe2f5;font-size:14px}
footer.site .wrap{padding:28px 20px;display:flex;flex-wrap:wrap;gap:24px;justify-content:space-between}
footer.site a{color:#fff}
.about{max-width:760px;margin:0 auto;padding:36px 20px 56px}.about p,.about li{font-size:17px}
table.calls{width:100%;border-collapse:collapse;font-size:15px}
table.calls th{text-align:left;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);border-bottom:2px solid var(--line);padding:8px 6px}
table.calls td{border-bottom:1px solid var(--line);padding:10px 6px;vertical-align:top}
table.calls td.dl{white-space:nowrap;font-weight:600}
.code{display:block;font-size:12px;color:var(--muted);font-family:ui-monospace,Menlo,Consolas,monospace}
.st{display:inline-block;font-size:12px;font-weight:700;border-radius:4px;padding:2px 8px;white-space:nowrap}
.st-Open{background:#e6f4ea;color:#1e6b34}.st-Forthcoming{background:#fff4d6;color:#7a5a00}.st-Closed{background:#eee;color:#555}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}.chips a{font-size:14px;border:1px solid var(--line);border-radius:999px;padding:4px 12px;text-decoration:none;background:#fff}
.section{padding:28px 0}.section h2{color:var(--navy);font-size:24px;margin:0 0 6px}
.soon{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:0 0 16px}
.faq h3{font-size:17px;color:var(--navy);margin:16px 0 4px}.faq p{margin:0}
.notice{background:#fff4d6;border-radius:8px;padding:12px 16px;margin:16px 0}
.byline a{color:var(--muted)}
.author-card{display:flex;gap:16px;align-items:center;border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-top:28px}
.avatar{flex:0 0 56px;height:56px;border-radius:50%;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:20px}
.vthumb{display:block;position:relative;aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:#000}.vthumb img{width:100%;height:100%;object-fit:cover;display:block}
.vthumb span{position:absolute;left:12px;bottom:12px;width:48px;height:34px;border-radius:12px;background:rgba(200,0,0,.9);color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px}
.player{position:relative;aspect-ratio:16/9;margin:20px 0;border-radius:10px;overflow:hidden;background:#000}.player iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
@media(max-width:640px){.hdr-r{width:100%;justify-content:space-between}h1,article.post h1{font-size:28px}.facts dl{grid-template-columns:1fr}.top-links{display:flex;overflow-x:auto;width:100%;padding-bottom:6px}.top-links a{margin:0 14px 0 0;white-space:nowrap}}
"""

def org_ld():
    return {"@type": "Organization", "@id": SITE["org_url"] + "/#org", "name": SITE["org"], "legalName": SITE["org_legal"],
            "url": SITE["org_url"], "email": SITE["email"],
            "address": {"@type": "PostalAddress", "streetAddress": "Calle Ramírez de Arellano, 17", "postalCode": "28043", "addressLocality": "Madrid", "addressCountry": "ES"},
            "location": [{"@type": "Place", "name": "Ullswater Investments Brussels", "address": {"@type": "PostalAddress", "streetAddress": "Square de Meeûs 37", "postalCode": "1000", "addressLocality": "Brussels", "addressCountry": "BE"}}],
            "sameAs": ["https://www.wikidata.org/wiki/Q142106306", "https://www.linkedin.com/company/ullswater-investments", "https://www.youtube.com/@ullswaterinvestments", "https://www.ullswaterinvestments.com/"],
            "logo": {"@type": "ImageObject", "url": SITE["url"] + "/assets/logo.png", "width": 512, "height": 512}}

def person_ld():
    return {"@type": "Person", "@id": SITE["url"] + AUTHOR_PATH + "#person", "name": AUTHOR["name"], "jobTitle": AUTHOR["role"],
            "url": SITE["url"] + AUTHOR_PATH, "worksFor": {"@type": "Organization", "name": SITE["org"], "url": SITE["org_url"]},
            "knowsAbout": AUTHOR["knows"], "sameAs": ["https://www.linkedin.com/in/emilio-mulet-esade/"]}

def page(title, desc, path, body, ld=None, og_type="website", extra_head="", cur=None, noindex=False, bilingual=True):
    """path is the English path; the Spanish page lives at /es + path."""
    canon = SITE["url"] + P(path)
    navs = "".join(f'<a href="{P("/" + k + "/")}"{" aria-current=\"page\"" if k == cur else ""}>{E(CAT(k)[0])}</a>' for k in CATEGORIES if k in ACTIVE)
    if HAS_VIDEOS: navs += f'<a href="{P("/videos/")}"{" aria-current=\"page\"" if cur == "videos" else ""}>{T("Videos")}</a>'
    alt = (f'<link rel="alternate" hreflang="en" href="{SITE["url"]}{path}"><link rel="alternate" hreflang="es" href="{SITE["url"]}/es{path}"><link rel="alternate" hreflang="x-default" href="{SITE["url"]}{path}">'
           if bilingual else "")
    switch = (f'<nav class="lang" aria-label="{T("Language")}"><a href="{path}" hreflang="en" lang="en"{"" if ES() else ' aria-current="true"'}>EN</a>'
              f'<a href="/es{path}" hreflang="es" lang="es"{' aria-current="true"' if ES() else ""}>ES</a></nav>' if bilingual else "")
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    year = datetime.date.today().year
    return f"""<!DOCTYPE html>
<html lang="{LANG}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">{alt}
<meta name="robots" content="{'noindex, follow' if noindex else 'index, follow, max-snippet:-1, max-image-preview:large'}">
<meta property="og:site_name" content="{E(S('name'))}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{'es_ES' if ES() else 'en_GB'}">
<meta property="og:image" content="{SITE['url']}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{E(S('name'))}" href="{SITE['url']}{P('/feed.xml')}">
<link rel="icon" href="/assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style>
{extra_head}{ld_html}
</head>
<body>
<header class="site"><div class="wrap"><a class="brand" href="{P('/')}">Ullswater Investments <span>· {E(S('short'))}</span></a>
<div class="hdr-r"><nav class="top-links" aria-label="Ullswater Investments">{network("News")}</nav>{switch}</div></div></header>
<nav class="cats" aria-label="{T('Categories')}"><div class="wrap">{navs}</div></nav>
<main>{body}</main>
<footer class="site"><div class="wrap">
<div><strong style="color:#fff">{E(SITE['org_legal'])}</strong><br>{T("EU Funding Advisors")} · Madrid: {E(SITE['address'])} · Brussels: {E(SITE['address_brussels'])}<br><a href="mailto:{SITE['email']}">{SITE['email']}</a></div>
<div><a href="{SITE['org_url']}{'/es/' if ES() else ''}">ullswaterinvestments.com</a> · <a href="{P('/about/')}">{T("Editorial policy")}</a> · <a href="{P('/feed.xml')}">RSS</a> · <a href="/sitemap.xml">Sitemap</a><br>© {year} {E(SITE['org_legal'])}</div>
</div></footer>
</body>
</html>"""

def load():
    arts = []
    for f in sorted((SRC / "articles").glob("*.json")):
        a = json.loads(f.read_text(encoding="utf-8"))
        a["d"] = datetime.date.fromisoformat(a["date"])
        a["updated"] = a.get("updated", a["date"])
        if a["category"] not in CATEGORIES: raise SystemExit(f"{f.name}: unknown category {a['category']}")
        for k in ("slug", "title", "dek", "body", "source_url", "source_name"):
            if not a.get(k): raise SystemExit(f"{f.name}: missing {k}")
        a["path"] = f"/{a['d'].year}/{a['d'].month:02d}/{a['slug']}/"
        arts.append(a)
    arts.sort(key=lambda a: (a["d"], a["slug"]), reverse=True)
    return arts

def load_videos():
    """src/videos/*.json: official videos embedded from YouTube (never downloaded or re-uploaded)."""
    vids = []
    for f in sorted((SRC / "videos").glob("*.json")) if (SRC / "videos").exists() else []:
        v = json.loads(f.read_text(encoding="utf-8"))
        for k in ("slug", "date", "title", "summary", "youtube_id", "channel_name", "channel_url"):
            if not v.get(k): raise SystemExit(f"{f.name}: missing {k}")
        v["d"] = datetime.date.fromisoformat(v["date"])
        v["path"] = f"/videos/{v['slug']}/"
        v["watch"] = f"https://www.youtube.com/watch?v={v['youtube_id']}"
        v["thumb"] = f"https://i.ytimg.com/vi/{v['youtube_id']}/hqdefault.jpg"
        vids.append(v)
    vids.sort(key=lambda v: (v["d"], v["slug"]), reverse=True)
    return vids

def vcard(v):
    return (f'<article class="card"><a class="vthumb" href="{P(v["path"])}" aria-label="{T("Video")}: {E(F(v, "title"))}"><img src="{v["thumb"]}" alt="" loading="lazy" width="480" height="360"><span>▶</span></a>'
            f'<h2><a href="{P(v["path"])}">{E(F(v, "title"))}</a></h2>'
            f'<div class="meta"><time datetime="{v["date"]}">{nice(v["d"])}</time> · {E(v["channel_name"])}</div>'
            f'<p>{E(F(v, "summary"))}</p></article>')

def card(a):
    c = CAT(a["category"])[0]
    return (f'<article class="card"><div><a class="tag" href="{P("/" + a["category"] + "/")}">{E(c)}</a></div>'
            f'<h2><a href="{P(a["path"])}">{E(F(a, "title"))}</a></h2>'
            f'<div class="meta"><time datetime="{a["date"]}">{nice(a["d"])}</time> · {T("Source")}: {E(a["source_name"])}</div>'
            f'<p>{E(F(a, "dek"))}</p></article>')

def call_rows(cs):
    return "".join(f'<tr><td><a href="{c.get("href") or c["path"]}">{E(c["title"])}</a><span class="code">{E(c["code"])}</span></td>'
                   f'<td>{E(GROUPS[c["group"]][0])}</td><td class="dl"><time datetime="{c["deadline"][:10]}">{nice(c["dl"])}</time></td>'
                   f'<td><span class="st st-{c["state"]}">{T(c["state"])}</span></td></tr>' for c in cs)

def call_table(cs):
    return (f'<div style="overflow-x:auto"><table class="calls"><thead><tr><th>{T("Call")}</th><th>{T("Programme")}</th><th>{T("Deadline")}</th><th>{T("Status")}</th></tr></thead>'
            f'<tbody>{call_rows(cs)}</tbody></table></div>')

def soon_block(live, days, n):
    soon = [c for c in live if c["status"] == "open" and 0 <= c["days"] <= days][:n]
    if not soon: return ""
    return (f'<section class="section"><div class="soon"><h2>{T("Closing in the next")} {days} {T("days")}</h2><a href="https://calls.ullswaterinvestments.com/closing-soon/">{T("All deadlines →")}</a></div>'
            + call_table(soon) + '</section>')

# "Apply with our support" form (Google Form, see ullswater-calls/tools/support_request_setup.gs). CALL and PAGE are replaced per page.
SUPPORT_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScK2yCvR62EAVc1pRxGHuv54TqkjV2zV7310pBoPqE0klQ94w/viewform?usp=pp_url&entry.841001766=CALL&entry.2085908736=PAGE"
def support_link(label, page_url):
    from urllib.parse import quote
    if SUPPORT_FORM:
        return SUPPORT_FORM.replace("CALL", quote(label)).replace("PAGE", quote(page_url))
    return f"mailto:{SITE['email']}?subject={quote('Support request: ' + label)}&body={quote('About: ' + label + chr(10) + 'Page: ' + page_url + chr(10) + chr(10) + 'Organisation, country and what you need:' + chr(10))}"

def related_calls(a):
    """Call pages (optional "calls": [ids]) and the open calls of the article's area, on calls.ullswaterinvestments.com."""
    li = [f'<li><a href="{CALLS}/call/{calls_slug(c)}/">{E(TITLES.get(c) or c)}</a>{T(": deadline, conditions and partners")}</li>' for c in a.get("calls", [])]
    if a["category"] in CAT_CALLS:
        u, t = CAT_CALLS[a["category"]]
        if ES(): t = CAT_CALLS_ES.get(a["category"], t)
        li.append(f'<li><a href="{CALLS}{u}">{E(t)}</a></li>')
    if not li: return ""
    label = (TITLES.get(a["calls"][0]) or a["calls"][0]) if a.get("calls") else a["title"]
    btn = f'<p class="act"><a class="btn" href="{E(support_link(label, SITE["url"] + P(a["path"])))}" target="_blank" rel="noopener">{T("Apply with our support")}</a></p>' if a.get("calls") else ""
    return f'<section class="src"><h2>{T("Related calls")}</h2><ul>{"".join(li)}</ul>{btn}</section>'

def write(path, text):
    p = OUT / path.lstrip("/")
    if path.endswith("/"): p = p / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

ACTIVE = set()
HAS_VIDEOS = False

def lang_pages(arts, vids, live):
    """All reader-facing pages in the current LANG (English paths, /es prefix for Spanish)."""
    url = lambda path: SITE["url"] + P(path)
    book = S("book_url")
    cta = (f'<aside class="cta"><div><strong>{T("Preparing a proposal?")}</strong><p>{T("Ullswater Investments helps companies match, prepare and submit EU funding applications.")}</p></div>'
           f'<a class="btn" href="{book}">Investment Readiness →</a></aside>')
    only_en = lambda a: '' if (not ES() or has_es(a)) else f'<p class="notice" lang="es">{T("This news item is only available in English for now.")}</p>'

    # Articles
    for a in arts:
        cat, catdesc = CAT(a["category"])
        facts = "".join(f"<dt>{E(k)}</dt><dd>{E(v)}</dd>" for k, v in F(a, "key_facts", []))
        body = "".join(f"<p>{E(p)}</p>" for p in F(a, "body"))
        related = [b for b in arts if b is not a and b["category"] == a["category"]][:3] or [b for b in arts if b is not a][:3]
        ld = [{
            "@context": "https://schema.org", "@type": "NewsArticle",
            "headline": F(a, "title"), "description": F(a, "dek"), "inLanguage": "es" if ES() and has_es(a) else "en",
            "datePublished": a["date"], "dateModified": a["updated"],
            "mainEntityOfPage": url(a["path"]), "url": url(a["path"]),
            "image": [SITE["url"] + "/assets/og.png"],
            "articleSection": cat, "keywords": ", ".join(F(a, "tags", [])),
            "author": person_ld(),
            "publisher": org_ld(),
            "isBasedOn": a["source_url"],
            "citation": {"@type": "CreativeWork", "name": a["source_name"], "url": a["source_url"]},
        }, {
            "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": T("News"), "item": url("/")},
                {"@type": "ListItem", "position": 2, "name": cat, "item": url(f"/{a['category']}/")},
                {"@type": "ListItem", "position": 3, "name": F(a, "title"), "item": url(a["path"])}]}]
        if ES() and has_es(a): ld[0]["translationOfWork"] = {"@type": "NewsArticle", "url": SITE["url"] + a["path"], "inLanguage": "en"}
        head = (f'<meta property="article:published_time" content="{a["date"]}">'
                f'<meta property="article:modified_time" content="{a["updated"]}">'
                f'<meta property="article:section" content="{E(cat)}">')
        tags = "".join(f"<span>{E(t)}</span>" for t in F(a, "tags", []))
        why = f'<section class="why"><h2>{T("Why it matters")}</h2><p>{E(F(a, "why"))}</p></section>' if a.get("why") else ""
        act = a.get("action")  # optional {"label", "url"}: direct link to the official registration/application page
        act_label = ((a.get("es") or {}).get("action_label") if ES() else None) or (act or {}).get("label")
        act_btn = f'<p class="act"><a class="btn" href="{E(act["url"])}" rel="noopener" target="_blank">{E(act_label)} ↗</a></p>' if act else ""
        rel = "".join(f'<li><a href="{P(b["path"])}">{E(F(b, "title"))}</a> <span class="meta">· {nice(b["d"])}</span></li>' for b in related)
        html_ = f"""<article class="post">
<div class="crumbs"><a href="{P('/')}">{T('News')}</a> › <a href="{P('/' + a['category'] + '/')}">{E(cat)}</a></div>
{only_en(a)}<p class="kicker">{E(cat)}</p>
<h1>{E(F(a, 'title'))}</h1>
<p class="dek">{E(F(a, 'dek'))}</p>
<div class="meta">{T('Published')} <time datetime="{a['date']}">{nice(a['d'])}</time> · {T('By')} <a href="{P(AUTHOR_PATH)}">{AUTHOR['name']}</a> · {T('Source')}: <a href="{E(a['source_url'])}" rel="noopener">{E(a['source_name'])}</a></div>
{f'<section class="facts" aria-label="{T("Key facts")}"><h2>{T("Key facts")}</h2><dl>{facts}</dl>{act_btn}</section>' if facts else act_btn}
<div class="body">{body}</div>
{why}
<section class="src"><h2>{T('Official source')}</h2><p><a href="{E(a['source_url'])}" rel="noopener">{E(a['source_name'])}</a> {T('— always check eligibility, budgets and deadlines on the official page before applying.')}</p>{act_btn}</section>
{related_calls(a)}
<div class="tags">{tags}</div>
{cta}
<div class="author-card"><div class="avatar">EM</div><div><strong><a href="{P(AUTHOR_PATH)}">{AUTHOR['name']}</a></strong><br><span class="meta">{E(A('role'))}. {T('EU funding advisor.')}</span></div></div>
{f'<section class="why"><h2>{T("Related news")}</h2><ul>{rel}</ul></section>' if rel else ''}
</article>"""
        write(P(a["path"]), page(f"{F(a, 'title')} · {S('short')}", F(a, "dek"), a["path"], html_, ld, "article", head, a["category"]))

    # Home
    site_ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": S("name"), "url": url("/"),
                "description": S("description"), "inLanguage": LANG, "publisher": org_ld()},
               {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
                   {"@type": "ListItem", "position": i + 1, "url": url(a["path"]), "name": F(a, "title")} for i, a in enumerate(arts[:20])]}]
    h1 = "Noticias de financiación europea" if ES() else "EU Funding News"
    home = (f'<section class="hero"><div class="wrap"><p class="kicker">Ullswater Investments · {T("EU Funding Advisors")}</p>'
            f'<h1>{h1}</h1><p class="lead">{E(S("description"))}</p>'
            f'<p class="meta" style="margin-top:12px">{T("Updated")} {nice(arts[0]["d"]) if arts else ""} · {len(arts)} {T("articles")} · {T("Every article links to its official source.")}</p></div></section>'
            f'<div class="wrap"><div class="grid">{"".join(card(a) for a in arts[:30])}</div>'
            + soon_block(live, 30, 10) + '</div>')
    title = (f"{S('short')} · Horizonte Europa, EIC y ayudas de la UE | Ullswater Investments" if ES()
             else f"{SITE['short']} · Horizon Europe, EIC and EU grants | Ullswater Investments")
    write(P("/"), page(title, S("description"), "/", home, site_ld))

    # Categories
    for k in CATEGORIES:
        name, desc = CAT(k)
        items = [a for a in arts if a["category"] == k]
        if not items: continue  # no thin, empty category pages
        body = (f'<section class="hero"><div class="wrap"><p class="kicker">{T("Category")}</p><h1>{E(name)}</h1><p class="lead">{E(desc)}</p></div></section>'
                f'<div class="wrap"><div class="grid">{"".join(card(a) for a in items)}</div></div>')
        ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{name} · {S('short')}", "url": url(f"/{k}/"), "description": desc, "inLanguage": LANG, "publisher": org_ld()}]
        write(P(f"/{k}/"), page(f"{name} · {S('short')} | Ullswater Investments", desc, f"/{k}/", body, ld, cur=k))

    # ---- Videos ----
    if vids:
        vdesc = ("Vídeos oficiales sobre investigación, innovación y financiación europea: grabaciones de eventos y jornadas informativas de la Comisión Europea, seleccionadas por Ullswater Investments." if ES()
                 else "Official videos on EU research, innovation and funding: recordings of European Commission events and info days, selected by Ullswater Investments.")
        vh1 = "Vídeos sobre financiación europea" if ES() else "EU Funding Videos"
        body = (f'<section class="hero"><div class="wrap"><p class="kicker">{T("Videos")}</p><h1>{vh1}</h1><p class="lead">{E(vdesc)}</p></div></section>'
                f'<div class="wrap"><div class="grid">{"".join(vcard(v) for v in vids)}</div></div>')
        ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{T('Videos')} · {S('short')}", "url": url("/videos/"), "description": vdesc, "inLanguage": LANG, "publisher": org_ld(),
               "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": url(v["path"]), "name": F(v, "title")} for i, v in enumerate(vids)]}}]
        write(P("/videos/"), page(f"{T('Videos')} · {S('short')} | Ullswater Investments", vdesc, "/videos/", body, ld, cur="videos"))
        for v in vids:
            body = "".join(f"<p>{E(p)}</p>" for p in F(v, "body", []))
            why = f'<section class="why"><h2>{T("Why watch it")}</h2><p>{E(F(v, "why"))}</p></section>' if v.get("why") else ""
            tags = "".join(f"<span>{E(t)}</span>" for t in F(v, "tags", []))
            ev = f' · {T("Event")}: <a href="{E(v["event_url"])}" rel="noopener">{E(v["event"])}</a>' if v.get("event_url") else ""
            more = [w for w in vids if w is not v][:5]
            rel = "".join(f'<li><a href="{P(w["path"])}">{E(F(w, "title"))}</a> <span class="meta">· {nice(w["d"])}</span></li>' for w in more)
            src_txt = (f'Vídeo publicado por <a href="{E(v["channel_url"])}" rel="noopener">{E(v["channel_name"])}</a> en YouTube: <a href="{v["watch"]}" rel="noopener">{v["watch"]}</a>.' + (f' Página del evento: <a href="{E(v["event_url"])}" rel="noopener">{E(v["event"])}</a>.' if v.get("event_url") else "")) if ES() else \
                      (f'Video published by <a href="{E(v["channel_url"])}" rel="noopener">{E(v["channel_name"])}</a> on YouTube: <a href="{v["watch"]}" rel="noopener">{v["watch"]}</a>.' + (f' Event page: <a href="{E(v["event_url"])}" rel="noopener">{E(v["event"])}</a>.' if v.get("event_url") else ""))
            html_ = f"""<article class="post">
<div class="crumbs"><a href="{P('/')}">{T('News')}</a> › <a href="{P('/videos/')}">{T('Videos')}</a></div>
{only_en(v)}<p class="kicker">{T('Video')}</p>
<h1>{E(F(v, 'title'))}</h1>
<p class="dek">{E(F(v, 'summary'))}</p>
<div class="meta">{T('Published')} <time datetime="{v['date']}">{nice(v['d'])}</time> · {T('Video by')} <a href="{E(v['channel_url'])}" rel="noopener">{E(v['channel_name'])}</a>{ev}</div>
<div class="player"><iframe src="https://www.youtube-nocookie.com/embed/{E(v['youtube_id'])}" title="{E(F(v, 'title'))}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
<p class="meta">{T('Embedded from YouTube.')} <a href="{v['watch']}" rel="noopener">{T('Watch on YouTube ↗')}</a></p>
<div class="body">{body}</div>
{why}
<section class="src"><h2>{T('Official source')}</h2><p>{src_txt}</p></section>
<div class="tags">{tags}</div>
{cta}
{f'<section class="why"><h2>{T("More videos")}</h2><ul>{rel}</ul></section>' if rel else ''}
</article>"""
            ld = [{"@context": "https://schema.org", "@type": "VideoObject", "name": F(v, "title"), "description": F(v, "summary"), "thumbnailUrl": [v["thumb"]],
                   "uploadDate": v["date"], "embedUrl": f"https://www.youtube.com/embed/{v['youtube_id']}", "url": url(v["path"]), "inLanguage": "en",
                   "author": {"@type": "Organization", "name": v["channel_name"], "url": v["channel_url"]}},
                  {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                      {"@type": "ListItem", "position": 1, "name": T("News"), "item": url("/")},
                      {"@type": "ListItem", "position": 2, "name": T("Videos"), "item": url("/videos/")},
                      {"@type": "ListItem", "position": 3, "name": F(v, "title"), "item": url(v["path"])}]}]
            write(P(v["path"]), page(f"{F(v, 'title')} · {T('Video')} · {S('short')}", F(v, "summary"), v["path"], html_, ld, "video.other", "", "videos"))

    # ---- Author ----
    my = arts[:20]
    auth = (f'<div class="about"><p class="kicker">{T("Author")}</p><h1>{E(AUTHOR["name"])}</h1><p class="lead">{E(A("role"))}</p>'
            + "".join(f"<p>{E(p)}</p>" for p in A("bio"))
            + f'<p>{T("Contact")}: <a href="mailto:{SITE["email"]}">{SITE["email"]}</a> · <a href="{SITE["org_url"]}{"/es/" if ES() else ""}">ullswaterinvestments.com</a> · <a href="https://www.linkedin.com/in/emilio-mulet-esade/" target="_blank" rel="noopener me">LinkedIn ↗</a></p>'
            + f'<h2>{T("Latest articles")}</h2><ul>' + "".join(f'<li><a href="{P(a["path"])}">{E(F(a, "title"))}</a> <span class="meta">· {nice(a["d"])}</span></li>' for a in my) + '</ul></div>')
    adesc = (f"{AUTHOR['name']}, {A('role')}: asesor de financiación europea especializado en Horizonte Europa, ayudas españolas de I+D y espacios de datos federados." if ES()
             else f"{AUTHOR['name']}, {AUTHOR['role']}: EU funding advisor specialised in Horizon Europe, Spanish R&D grants and federated data spaces.")
    write(P(AUTHOR_PATH), page(f"{AUTHOR['name']} · {A('role')} · {S('short')}", adesc, AUTHOR_PATH, auth,
                            [{"@context": "https://schema.org", "@type": "ProfilePage", "url": url(AUTHOR_PATH), "mainEntity": person_ld()}]))

    # About / editorial policy
    if ES():
        about = f"""<div class="about"><p class="kicker">Quiénes somos</p><h1>Sobre Noticias de financiación europea</h1>
<p>Noticias de financiación europea es una publicación de <a href="{SITE['org_url']}/es/">{E(SITE['org_legal'])}</a>, firma de asesoramiento en financiación europea y creación de empresas con sede en Madrid. Cubrimos la financiación europea y española para la innovación: Horizonte Europa, el Consejo Europeo de Innovación, Europa Digital, los instrumentos de defensa y doble uso, los fondos de cohesión y de recuperación, y las ayudas nacionales de I+D.</p>
<h2>Política editorial</h2>
<ul>
<li>Cada noticia se basa en una fuente oficial (Comisión Europea, agencias e instituciones de la UE u organismos públicos españoles), que se enlaza en la propia noticia.</li>
<li>Las cifras, fechas y plazos se comprueban con esa fuente antes de publicar. No publicamos estimaciones como si fueran hechos.</li>
<li>Las noticias están redactadas con palabras propias. La sección «Por qué importa» es el análisis de Ullswater Investments y está claramente separada de los hechos.</li>
<li>Cada noticia se publica en inglés y en español; la versión en español es una traducción fiel de la inglesa.</li>
<li>Si nos equivocamos, lo corregimos y actualizamos la fecha de modificación de la noticia. Correcciones: <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</li>
<li>Confirma siempre la elegibilidad, los presupuestos y los plazos en la página oficial de la convocatoria antes de solicitar.</li>
</ul></div>"""
        atitle, adesc = f"Quiénes somos y política editorial · {S('short')}", "Quién publica Noticias de financiación europea y cómo se documentan, verifican y corrigen las noticias."
    else:
        about = f"""<div class="about"><p class="kicker">About</p><h1>About EU Funding News</h1>
<p>EU Funding News is published by <a href="{SITE['org_url']}">{E(SITE['org_legal'])}</a>, a Madrid-based European funding advisory and venture-building firm. We cover EU and Spanish funding for innovation: Horizon Europe, the European Innovation Council, Digital Europe, defence and dual-use instruments, cohesion and recovery funds, and national R&amp;D grants.</p>
<h2>Editorial policy</h2>
<ul>
<li>Every article is based on an official source (European Commission, EU agencies, EU institutions or Spanish public bodies), which is linked in the article.</li>
<li>Figures, dates and deadlines are checked against that source before publication. We do not publish estimates as facts.</li>
<li>Articles are written in our own words. The “Why it matters” section is Ullswater Investments' analysis and is clearly separated from the facts.</li>
<li>Every article is published in English and Spanish; the Spanish version is a faithful translation of the English one.</li>
<li>If we get something wrong, we correct it and update the article's modification date. Corrections: <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</li>
<li>Always confirm eligibility, budgets and deadlines on the official call page before applying.</li>
</ul></div>"""
        atitle, adesc = f"About & editorial policy · {SITE['short']}", "Who publishes EU Funding News and how articles are sourced, verified and corrected."
    write(P("/about/"), page(atitle, adesc, "/about/", about, [{"@context": "https://schema.org", "@type": "AboutPage", "url": url("/about/"), "inLanguage": LANG, "publisher": org_ld()}]))


def build():
    global HAS_VIDEOS
    arts = load()
    vids = load_videos()
    HAS_VIDEOS = bool(vids)
    ACTIVE.update(a["category"] for a in arts)
    TODAY = datetime.date.today()
    calls, feed_updated = load_calls(TODAY, offline=bool(os.environ.get("OFFLINE")))
    live = [c for c in calls if not c["closed"]]
    ids = live_ids(offline=bool(os.environ.get("OFFLINE")))
    for c in calls:
        c["href"] = call_url(c, ids)
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    if (SRC / "assets").exists(): shutil.copytree(SRC / "assets", OUT / "assets")
    (OUT / "CNAME").write_text(SITE["domain"] + "\n")
    from indexnow import KEY as INDEXNOW_KEY
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    (OUT / ".nojekyll").write_text("")
    today = datetime.date.today().isoformat()

    # Call pages live only on calls.ullswaterinvestments.com: every old /calls/... address becomes a redirect page.
    for c in calls:
        write(c["path"], stub(c["href"], c["code"]))
    write("/calls/", stub(CALLS + "/", "EU funding calls"))
    for k in GROUPS:
        write(f"/calls/programme/{k}/", stub(theme_url(k), GROUPS[k][0]))
    write("/calls/deadlines/", stub(CALLS + "/closing-soon/", "EU funding deadlines"))

    # Language pages: English at /, Spanish at /es/
    global LANG
    for LANG in ("en", "es"):
        lang_pages(arts, vids, live)
    LANG = "en"

    # 404
    (OUT / "404.html").write_text(page(f"Page not found · {SITE['short']}", "Page not found.", "/404.html",
        '<div class="about"><h1>Page not found</h1><p>The page you are looking for does not exist. Go to the <a href="/">latest EU funding news</a> · <a href="/es/">últimas noticias en español</a>.</p></div>', bilingual=False).replace(
        '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">', '<meta name="robots" content="noindex">'), encoding="utf-8")

    # RSS (English at /feed.xml, Spanish at /es/feed.xml)
    now = format_datetime(datetime.datetime.now(datetime.timezone.utc))
    for LANG in ("en", "es"):
        items = "".join(
            f"<item><title>{E(F(a, 'title'))}</title><link>{SITE['url']}{P(a['path'])}</link><guid isPermaLink=\"true\">{SITE['url']}{P(a['path'])}</guid>"
            f"<pubDate>{format_datetime(datetime.datetime.combine(a['d'], datetime.time(9, 0), datetime.timezone.utc))}</pubDate>"
            f"<category>{E(CAT(a['category'])[0])}</category><description>{E(F(a, 'dek'))}</description></item>" for a in arts[:50] if not ES() or has_es(a))
        (OUT / P("/feed.xml").lstrip("/")).write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            f'<title>{E(S("name"))}</title><link>{SITE["url"]}{P("/")}</link><description>{E(S("description"))}</description><language>{LANG}</language>'
            f'<lastBuildDate>{now}</lastBuildDate><atom:link href="{SITE["url"]}{P("/feed.xml")}" rel="self" type="application/rss+xml"/>{items}</channel></rss>\n', encoding="utf-8")
    LANG = "en"

    # Sitemaps (regular + Google News for the last 2 days)
    urls = [("/", arts[0]["updated"] if arts else today), ("/about/", today)] + [(f"/{k}/", next(a["updated"] for a in arts if a["category"] == k)) for k in CATEGORIES if k in ACTIVE] + [(a["path"], a["updated"]) for a in arts] \
        + [(AUTHOR_PATH, arts[0]["updated"] if arts else today)] \
        + ([("/videos/", vids[0]["date"])] + [(v["path"], v["date"]) for v in vids] if vids else [])
    alts = lambda p: (f'<xhtml:link rel="alternate" hreflang="en" href="{SITE["url"]}{p}"/><xhtml:link rel="alternate" hreflang="es" href="{SITE["url"]}/es{p}"/>'
                      f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE["url"]}{p}"/>')
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        + "".join(f"<url><loc>{SITE['url']}{pre}{p}</loc><lastmod>{d}</lastmod>{alts(p)}</url>" for p, d in urls for pre in ("", "/es")) + "</urlset>\n", encoding="utf-8")
    recent = [a for a in arts if (datetime.date.today() - a["d"]).days <= 2]
    (OUT / "news-sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
        + "".join(f"<url><loc>{SITE['url']}{a['path']}</loc><news:news><news:publication><news:name>{E(SITE['short'])}</news:name><news:language>en</news:language></news:publication>"
                  f"<news:publication_date>{a['date']}</news:publication_date><news:title>{E(a['title'])}</news:title></news:news></url>" for a in recent) + "</urlset>\n", encoding="utf-8")

    # robots.txt — open to search engines and AI search/answer crawlers
    bots = ["Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "GPTBot", "PerplexityBot", "Perplexity-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "Google-Extended", "Applebot", "Applebot-Extended", "DuckDuckBot", "meta-externalagent", "MistralAI-User"]
    (OUT / "robots.txt").write_text("# EU Funding News · Ullswater Investments\n# Open to search engines and AI assistants so our articles can be found and cited.\n\n"
        "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
        + f"Sitemap: {SITE['url']}/sitemap.xml\nSitemap: {SITE['url']}/news-sitemap.xml\n", encoding="utf-8")

    # llms.txt + llms-full.txt (plain-text versions for AI assistants)
    llms = [f"# {SITE['name']}", "", f"> {SITE['description']} Published by {SITE['org_legal']} (Madrid), EU funding advisors. Every article cites and links an official source.", "",
            "Key facts:", f"- Publisher: {SITE['org_legal']} · {SITE['org_url']}", f"- Contact: {SITE['email']} · Madrid: {SITE['address']} · Brussels: {SITE['address_brussels']}", f"- Languages: English (this site) and Spanish ({SITE['url']}/es/, RSS {SITE['url']}/es/feed.xml). Updated on working days.", "",
            "## Sections", ""] + [f"- [{v[0]}]({SITE['url']}/{k}/): {v[1]}" for k, v in CATEGORIES.items() if k in ACTIVE] + ["", "## EU funding calls (updated daily)", "", f"- [All open and forthcoming EU calls]({CALLS}/): one page per call with deadline, budget, partners and official links, updated daily.", f"- [Closing soon]({CALLS}/closing-soon/)", f"- [Calls by theme]({CALLS}/theme/)"] + (["", "## Videos", "", f"- [All videos]({SITE['url']}/videos/): official recordings of EU research, innovation and funding events."] + [f"- [{v['title']}]({SITE['url']}{v['path']}) ({v['date']}): {v['summary']}" for v in vids[:20]] if vids else []) + ["", f"## Author", "", f"- [{AUTHOR['name']}]({SITE['url']}{AUTHOR_PATH}): {AUTHOR['role']}"] + ["", "## Latest articles", ""] + \
           [f"- [{a['title']}]({SITE['url']}{a['path']}) ({a['date']}): {a['dek']}" for a in arts[:50]] + ["", "## Optional", "", f"- [Full text of recent articles]({SITE['url']}/llms-full.txt)", f"- [Editorial policy]({SITE['url']}/about/)", f"- [RSS feed]({SITE['url']}/feed.xml)"]
    (OUT / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    full = [f"# {SITE['name']} — full text of recent articles", ""]
    for a in arts[:50]:
        full += [f"## {a['title']}", f"URL: {SITE['url']}{a['path']}", f"Date: {a['date']} · Category: {CATEGORIES[a['category']][0]} · Source: {a['source_name']} ({a['source_url']})", "", a["dek"], ""]
        full += [f"- {k}: {v}" for k, v in a.get("key_facts", [])] + [""] + a["body"] + ([""] + [f"Why it matters (Ullswater Investments analysis): {a['why']}"] if a.get("why") else []) + ["", "---", ""]
    (OUT / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")
    (OUT / "calls.txt").write_text(f"# Open and forthcoming EU funding calls · {SITE['name']}\n# Checked {TODAY.isoformat()} from the EU Funding & Tenders Portal. Columns: identifier | title | status | opens | deadline | budget | page\n\n"
        + "".join(f"{c['code']} | {c['title']} | {c['state']} | {(c.get('opens') or '')[:10]} | {c['deadline'][:10]} | {c.get('budget') or '-'} | {c['href']}\n" for c in live), encoding="utf-8")
    print(f"Calls: {len(calls)} pages ({len(live)} live)")
    print(f"Built {len(arts)} articles, {len(vids)} videos, {len(CATEGORIES)} categories → {OUT}")

if __name__ == "__main__":
    build()
