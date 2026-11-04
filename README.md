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

## Call alerts (automatic)

`src/calls.py` reads the Ullswater worker feed (EU Funding & Tenders Portal) and builds one page per call
(`/calls/<identifier>/`), programme pages (`/calls/programme/<key>/`), the deadlines calendar
(`/calls/deadlines/`) and `calls.txt`. `src/data/calls.json` keeps every call ever seen, so closed calls keep
their page (marked Closed, noindex 90 days after the deadline) instead of returning 404.

`.github/workflows/daily-build.yml` rebuilds and publishes the site every morning. If the feed fails, the
build keeps the last good data. Build without network: `OFFLINE=1 python3 src/build.py`.

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
Optional: `"updated": "YYYY-MM-DD"` when an article is corrected.

2. Run `python3 src/build.py`.
3. Commit and push. GitHub Pages republishes in about a minute.

## Editorial rules (mandatory)

- English only. Own words, never copied text.
- Every figure, date and deadline must appear in the linked official source.
- The `why` field is analysis and must not add facts that are not in the source.
- Publish only after Emilio's OK.
