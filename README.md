# EU Funding News · Ullswater Investments

Static news site published with GitHub Pages at **https://news.ullswaterinvestments.com**.
Same model as www.softwareinabox.eu: plain HTML files, no JavaScript needed to read them, Cloudflare DNS in front.

## How it works

- `src/articles/*.json` — one file per article (the only thing you edit to publish news).
- `src/build.py` — generates the whole site into `docs/`.
- `docs/` — the published site (GitHub Pages: branch `main`, folder `/docs`). Never edit by hand.

Every build regenerates: home, article pages (`/YYYY/MM/slug/`), category pages, `about/`,
`feed.xml` (RSS), `sitemap.xml`, `news-sitemap.xml` (Google News, last 48 h), `robots.txt`,
`llms.txt`, `llms-full.txt`, `404.html` and `CNAME`.

## Calls: moved to calls.ullswaterinvestments.com (Nov 2026)

Call pages live only on **https://calls.ullswaterinvestments.com** (single source, avoids duplicate pages in search).
`src/calls.py` still reads the feed, but every old address here (`/calls/<id>/`, `/calls/programme/<key>/`, `/calls/deadlines/`)
is now a redirect page (`src/redirects.py`: canonical + meta refresh, noindex) to the matching call or theme page on the calls site,
and none of them is in the sitemap. The "Closing soon" table on the home page links straight to the calls site.

## Links to calls and shared menu
- Optional article field `"calls": ["<call id>"]` adds a "Related calls" box linking each call page on the calls site.
- Each category links to its theme on the calls site (`CAT_CALLS` in `src/build.py`; reference list: calls site `/data/taxonomy.json`).
- The header carries the shared network menu (Home · EU calls · News · Events · Projects · About), identical on www, calls, news and events.

## Publishing a new article

1. Add `src/articles/YYYY-MM-DD-slug.json`:

```json
{
  "slug": "short-url-slug",
  "date": "2026-11-05",
  "category": "horizon-europe",
  "title": "Headline in English, max ~70 characters",
  "dek": "One-sentence summary (used as meta description, ~150 characters).",
  "key_facts": [["Programme", "..."], ["Budget", "€... million"], ["Deadline", "..."]],
  "body": ["Paragraph 1.", "Paragraph 2."],
  "why": "Ullswater Investments analysis: what it means for applicants. No new figures here.",
  "tags": ["Horizon Europe", "..."],
  "source_name": "European Commission – Research and Innovation",
  "source_url": "https://official-source..."
}
```

Categories: `horizon-europe`, `digital-ai`, `eic-defence`, `research-policy`, `budget-policy`, `spain`, `climate-energy`, `health`.
Optional: `"action": {"label": "Register for the info day", "url": "https://<official registration or application page>"}` adds a button with a direct link to the official registration/application form (only official pages; verify the link). Optional: `"updated": "YYYY-MM-DD"` when an article is corrected.

2. Run `python3 src/build.py`.
3. Commit and push. GitHub Pages republishes in about a minute.

## Spanish version (/es/) — mandatory for every new article and video

The site is bilingual: English at `/`, Spanish at `/es/` (same paths with the `/es` prefix), linked with hreflang and an EN | ES switcher in the header. Every article JSON must carry an `"es"` block with the Spanish translation:

```json
"es": {
  "title": "…", "dek": "…",
  "key_facts": [["Programa", "…"], ["Presupuesto", "…"]],
  "body": ["Párrafo 1.", "Párrafo 2."],
  "why": "…",
  "tags": ["Horizonte Europa", "…"],
  "action_label": "Inscríbete en la jornada informativa"
}
```

Rules: a faithful translation of the English text (no new facts, same figures and dates, same number of `key_facts` and `body` paragraphs). Spanish number format (1.800 millones de euros, 12,75 millones). Official Spanish terms: Horizon Europe → Horizonte Europa, call → convocatoria, topic → tema, work programme → programa de trabajo, Cluster → Clúster, EIB → BEI, EIF → FEI, ERDF → FEDER, SME → pyme, info day → jornada informativa. Programme and instrument names stay in English (EIC Accelerator, Pathfinder, STEP, call codes). "Ullswater Investments analysis:" → "Análisis de Ullswater Investments:". Videos take `"es": {"title", "summary", "body", "why", "tags"}`. An article with `"action"` may also set `"es": {"action_url": "…"}` so the Spanish button points to the Spanish page (e.g. the /es/ event page). If the block is missing, the Spanish page shows the English text with a notice, so always add it.

## Videos section (/videos/)

Add `src/videos/YYYY-MM-DD-slug.json` to publish an official video at `/videos/<slug>/` (also listed on `/videos/`, in the sitemap and in llms.txt; a "Videos" link appears in the category bar):

```json
{
  "slug": "short-url-slug",
  "date": "2026-11-11",
  "title": "Video title in English",
  "summary": "One-sentence summary (meta description).",
  "youtube_id": "WnqXluHPH0k",
  "channel_name": "EU Science & Innovation (European Commission)",
  "channel_url": "https://www.youtube.com/channel/...",
  "event": "Optional event name", "event_url": "https://official-event-page",
  "body": ["Context paragraph in our own words."],
  "why": "Optional Ullswater note, no new facts.",
  "tags": ["..."]
}
```

Videos are embedded with the YouTube player (youtube-nocookie.com) and always credit and link the original channel: never download or re-upload them. Only official channels (Commission, EU agencies, Spanish public bodies) or Ullswater's own.

## Editorial rules (mandatory)

- English only. Own words, never copied text.
- Every figure, date and deadline must appear in the linked official source.
- The `why` field is analysis and must not add facts that are not in the source.
- Publish only after verification against the official source. Emilio gave standing approval (16 Nov 2026) for the daily news agent to publish verified articles directly; anything that cannot be verified stays in a drafts/ branch.

## External links open in a new tab (Nov 2026)
`src/extlinks.py` runs at the end of every build: links outside the Ullswater network get `target="_blank" rel="noopener noreferrer"`, a small ↗ icon and a hidden "(opens in a new tab)" / "(se abre en una pestaña nueva)" label. Links between our own sites (`*.ullswaterinvestments.com`) stay in the same tab, and links marked `data-noext` are skipped. Check with `python3 src/extlinks.py docs --check`. Same file as in events-site.

## Dossiers (topic folders with news + key dates) — Nov 2026
`src/dossiers/<slug>.json` creates a topic page at `/dossier/<slug>/` (and `/es/dossier/<slug>/`) with an intro, a "Key dates and events" table and every article whose JSON has `"dossier": "<slug>"`. Dossiers appear first in the category bar (gold), get a "Part of the dossier" box on each article, and are added to the sitemap and llms.txt.
Fields: `slug`, `nav`, `title`, `intro` (list), `timeline` (list of `{sort: YYYY-MM-DD, when, status: done|upcoming, text, url, source}`, kept in date order), and `es` with `nav`, `title`, `intro`, plus `timeline` and `when` lists in the same order. Every timeline item links to its source; update `status` when a date passes.
First dossier: `plan-ia360` (Plan IA360, Red NEURONA, AI voucher, EuroHPC AI Gigafactories).
