"""Call alerts: one page per EU funding call, built from the live Funding & Tenders feed.

Data flow: the Ullswater worker (fh-topics) exposes the open and forthcoming topics of the
EU Funding & Tenders Portal. Every build merges that feed into src/data/calls.json, so calls
that close or disappear keep their page (marked Closed) instead of turning into a 404.
"""
import json, re, datetime, urllib.request, pathlib

FEED = "https://fh-topics.emilio-mulet.workers.dev/"
DATA = pathlib.Path(__file__).resolve().parent / "data" / "calls.json"
NOINDEX_AFTER_DAYS = 90   # closed calls stay online but leave the index after this

# (group key, label, short description) — derived from the call identifier
HE = "Horizon Europe"
GROUPS = {
    "he-cl1": (f"{HE} · Cluster 1 Health", "Horizon Europe health research and innovation calls (Cluster 1, HLTH)."),
    "he-cl2": (f"{HE} · Cluster 2 Culture, Creativity & Inclusive Society", "Horizon Europe Cluster 2 calls on democracy, cultural heritage and social transformation."),
    "he-cl3": (f"{HE} · Cluster 3 Civil Security for Society", "Horizon Europe Cluster 3 calls on security, disaster resilience and cybersecurity."),
    "he-cl4": (f"{HE} · Cluster 4 Digital, Industry & Space", "Horizon Europe Cluster 4 calls on AI, data, digital technologies, industry and space."),
    "he-cl5": (f"{HE} · Cluster 5 Climate, Energy & Mobility", "Horizon Europe Cluster 5 calls on climate, energy and transport."),
    "he-cl6": (f"{HE} · Cluster 6 Food, Bioeconomy & Environment", "Horizon Europe Cluster 6 calls on food systems, biodiversity, agriculture and natural resources."),
    "he-eic": ("European Innovation Council (EIC)", "EIC Accelerator, Pathfinder, Transition, STEP and EIC prizes."),
    "he-msca": (f"{HE} · Marie Skłodowska-Curie Actions", "MSCA calls for doctoral networks, postdoctoral fellowships, COFUND and staff exchanges."),
    "he-erc": ("European Research Council (ERC)", "ERC frontier research grants."),
    "he-infra": (f"{HE} · Research Infrastructures", "Horizon Europe calls for research infrastructures."),
    "he-widera": (f"{HE} · Widening & European Research Area", "Widening participation and ERA calls."),
    "he-miss": (f"{HE} · EU Missions", "Calls of the EU Missions (cancer, climate adaptation, oceans, cities, soil)."),
    "he-eie": (f"{HE} · European Innovation Ecosystems", "Calls to connect and strengthen European innovation ecosystems."),
    "he-ju": (f"{HE} · Joint Undertakings & Partnerships", "Calls of the European partnerships and Joint Undertakings (IHI, Chips, Clean Hydrogen, SNS, CBE, EuroHPC and others)."),
    "he-raise": (f"{HE} · RAISE (AI in science)", "Calls under RAISE, the Resource for AI Science in Europe."),
    "he-other": (f"{HE} · Other calls", "Other Horizon Europe calls."),
    "digital": ("Digital Europe Programme", "Digital Europe calls on AI, data, cybersecurity, advanced digital skills and digital innovation hubs."),
    "edf": ("European Defence Fund", "European Defence Fund calls for defence research and capability development."),
    "i3": ("Interregional Innovation Investments (I3)", "I3 calls for interregional innovation projects."),
    "crea": ("Creative Europe", "Creative Europe calls for the cultural and creative sectors."),
    "cerv": ("Citizens, Equality, Rights and Values (CERV)", "CERV programme calls."),
    "erasmus": ("Erasmus+", "Erasmus+ calls."),
    "cef": ("Connecting Europe Facility", "CEF calls for transport, energy and digital infrastructure."),
    "other": ("Other EU programmes", "Calls from other EU funding programmes."),
}
HE_MAP = {"HLTH": "he-cl1", "CL1": "he-cl1", "CL2": "he-cl2", "CL3": "he-cl3", "CL4": "he-cl4", "CL5": "he-cl5", "CL6": "he-cl6",
          "EIC": "he-eic", "MSCA": "he-msca", "ERC": "he-erc", "INFRA": "he-infra", "WIDERA": "he-widera", "MISS": "he-miss",
          "EIE": "he-eie", "JU": "he-ju", "RAISE": "he-raise"}
OTHER_MAP = {"DIGITAL": "digital", "EDF": "edf", "I3": "i3", "CREA": "crea", "CERV": "cerv", "ERASMUS": "erasmus", "CEF": "cef", "ERC": "he-erc"}

def group_of(code):
    p = code.upper().split("-")
    if p[0] == "HORIZON" and len(p) > 1:
        return HE_MAP.get(p[1], "he-other")
    return OTHER_MAP.get(p[0], "other")

def slug_of(code):
    return re.sub(r"[^a-z0-9-]+", "-", code.lower()).strip("-")

def fetch_feed():
    req = urllib.request.Request(FEED, headers={"User-Agent": "ullswater-news-builder/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    topics = d.get("topics") or []
    if len(topics) < 100:
        raise RuntimeError(f"feed returned only {len(topics)} topics")
    return topics, d.get("updated")

def load_calls(today, offline=False):
    """Merge the live feed into the archive and return (calls, feed_updated)."""
    arch = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"calls": {}, "feed_updated": None}
    calls = arch["calls"]
    feed_updated = arch.get("feed_updated")
    if not offline:
        try:
            topics, feed_updated = fetch_feed()
            live = set()
            for t in topics:
                code = (t.get("codigo") or "").strip()
                if not code or not t.get("cierre"): continue
                live.add(code)
                b = t.get("presupuesto") or {}
                c = calls.get(code, {"first_seen": today.isoformat()})
                c.update(code=code, title=(t.get("titulo") or code).strip(), opens=t.get("apertura"), deadline=t.get("cierre"),
                         status="open" if t.get("estado") in ("Abierta", "Open") else "forthcoming",
                         budget=(b.get("en") if isinstance(b, dict) else None), keywords=t.get("palabrasClave") or [],
                         url=t.get("enlace"), last_seen=today.isoformat(), listed=True)
                calls[code] = c
            for code, c in calls.items():
                if code not in live: c["listed"] = False
            arch = {"calls": calls, "feed_updated": feed_updated}
            DATA.parent.mkdir(parents=True, exist_ok=True)
            DATA.write_text(json.dumps(arch, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        except Exception as e:  # keep the last good archive; never wipe the site
            print("WARNING: feed not updated:", e)
    out = []
    for c in calls.values():
        c = dict(c)
        dl = datetime.date.fromisoformat(c["deadline"][:10])
        c["dl"] = dl
        c["closed"] = dl < today or not c.get("listed", True)
        if c["closed"]: c["state"] = "Closed"
        elif c["status"] == "open": c["state"] = "Open"
        else: c["state"] = "Forthcoming"
        c["days"] = (dl - today).days
        c["noindex"] = c["closed"] and (today - dl).days > NOINDEX_AFTER_DAYS
        c["group"] = group_of(c["code"])
        c["slug"] = slug_of(c["code"])
        c["path"] = f"/calls/{c['slug']}/"
        out.append(c)
    out.sort(key=lambda c: (c["closed"], c["dl"], c["code"]))
    return out, feed_updated
