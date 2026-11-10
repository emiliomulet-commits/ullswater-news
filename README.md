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

## Editorial rules (mandatory)

- English only. Own words, never copied text.
- Every figure, date and deadline must appear in the linked official source.
- The `why` field is analysis and must not add facts that are not in the source.
- Publish only after Emilio's OK.

## External links open in a new tab (Nov 2026)
`src/extlinks.py` runs at the end of every build: links outside the Ullswater network get `target="_blank" rel="noopener noreferrer"`, a small ↗ icon and a hidden "(opens in a new tab)" label. Links between our own sites (`*.ullswaterinvestments.com`) stay in the same tab. Check with `python3 src/extlinks.py docs --check`.
