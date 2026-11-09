# EU Funding Events · Ullswater Investments

Static events site for **https://events.ullswaterinvestments.com**. Same model as the news site: one JSON file per item, a Python generator with no dependencies, plain HTML output.

- `src/events/*.json`: one file per event (the only thing you edit to publish).
- `src/build.py`: generates the site into `docs/` (not committed).

Cloudflare Pages settings: production branch `events-site`, build command `python3 src/build.py`, output directory `docs`.

Fields: `slug`, `title`, `start`, `end`, `type` (info-day, brokerage, conference, training, webinar), `programme`, `mode` (online, onsite, hybrid), `city`, `location`, `organiser`, `status` (scheduled, applications-closed, cancelled, postponed), `summary`, `details`, `why`, `tags`, `registration_url`, `source_name`, `source_url`.

Editorial rules: English only, own words, every date and place must appear in the linked source, `why` adds no facts, publish only after Emilio's OK.

## Structure (Nov 2026)
- Event pages live at `/events/<slug>/` (no date in the URL, so a postponed event keeps its address). Old `/YYYY/MM/<slug>/` addresses get a 301 through `docs/_redirects` (Cloudflare Pages).
- Optional fields: `calls` (list of call ids from calls.ullswaterinvestments.com, linked as "Call page"), `series` + `series_title` (groups sessions of the same programme under `/series/<series>/`).
- `programme` keys map to theme pages of calls.ullswaterinvestments.com (`THEME` in `src/build.py`, reference list in `/data/taxonomy.json` of the calls site). `events.json` now also carries `theme` and `calls`.
- The header carries the shared network menu (Home · EU calls · News · Events · Projects · About), identical on www, calls, news and events.
