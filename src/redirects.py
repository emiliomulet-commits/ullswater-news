"""Call pages now live only on calls.ullswaterinvestments.com (single source, Nov 2026).

news.ullswaterinvestments.com/calls/... keeps a tiny redirect page at every old address
(canonical + meta refresh + JS) so links and search results move to the calls site.
"""
import json, re, urllib.request
from html import escape as E

CALLS = "https://calls.ullswaterinvestments.com"

# news programme groups -> calls.ullswaterinvestments.com theme pages
GROUP_THEME = {
    "he-cl1": "health", "he-cl2": "culture-society", "he-cl3": "civil-security", "he-cl4": "digital-industry-space",
    "he-cl5": "climate-energy-mobility", "he-cl6": "food-environment", "he-eic": "eic",
    "he-msca": "science-widening", "he-erc": "science-widening", "he-infra": "science-widening", "he-widera": "science-widening",
    "he-miss": "missions-bridging", "digital": "digital-europe-defence", "edf": "digital-europe-defence",
}


def calls_slug(code):
    return re.sub(r"[^a-z0-9]+", "-", code.lower()).strip("-")


def live_ids(offline=False):
    """Slugs of the call pages that exist on the calls site (None if unknown)."""
    if offline:
        return None
    try:
        req = urllib.request.Request(CALLS + "/data/calls.json", headers={"User-Agent": "ullswater-news-builder/1.0"})
        d = json.load(urllib.request.urlopen(req, timeout=60))
        return {calls_slug(c["id"]) for c in d["calls"]}
    except Exception as e:
        print("WARNING: calls site list unavailable:", e)
        return None


def theme_url(group):
    t = GROUP_THEME.get(group)
    return f"{CALLS}/theme/{t}/" if t else f"{CALLS}/"


def call_url(c, ids):
    s = calls_slug(c["code"])
    if (ids is not None and s in ids) or (ids is None and not c["closed"]):
        return f"{CALLS}/call/{s}/"
    return theme_url(c["group"])


def stub(target, title):
    t = E(target)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{E(title)}</title>'
            f'<link rel="canonical" href="{t}"><meta name="robots" content="noindex,follow">'
            f'<meta http-equiv="refresh" content="0; url={t}"><script>location.replace({json.dumps(target)})</script></head>'
            f'<body><p>This page has moved to <a href="{t}">{t}</a>.</p></body></html>')
