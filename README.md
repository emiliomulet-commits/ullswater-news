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

## Webinars (Nov 2026)
- `/webinars/` is the webinars hub: upcoming live webinars (events with `"type": "webinar"` in `src/events/`) plus a **library** of past sessions.
- Library items: one file per webinar in `src/webinars/*.json` with `slug`, `title`, `date`, `time`, `topic` (proposal, eligibility, grant, management), `programme`, `organiser`, `summary`, `covers` (list), `materials`, `why`, `tags`, `official_url`, `source_name`, `source_url`, optional `superseded_by` (slug of a newer edition).
- Optional `videos`: list of official recordings `{youtube, channel, seconds, uploaded, label?, chapters?: [[seconds, "title"]], chapters_source: "official" | "ullswater"}`. Only recordings from the organiser's own channel and linked from its event page. The page shows our thumbnail and loads the youtube-nocookie.com player only when the visitor presses play; chapters jump to that minute. Each build checks the video with YouTube oEmbed and falls back to the slides if it was removed or embedding was disabled. VideoObject + Clip structured data is generated for search engines.
- Chapter indexes marked `ullswater` were prepared from the recording's transcript; `official` ones are copied from the video description.
- Editorial rules as for events: own words, every fact on the official page, materials are linked and never re-hosted.
- Sources to scan for new webinars: Research & Innovation community platform (EC), Funding & Tenders Portal events, EIC/EISMEA, HaDEA, CINEA, REA, Digital Europe, NCP networks, Enterprise Europe Network, EUREKA/ITEA, Gaia-X and IDSA.

## External links open in a new tab (Nov 2026)
`src/extlinks.py` runs at the end of every build: links outside the Ullswater network get `target="_blank" rel="noopener noreferrer"`, a small ↗ icon and a hidden "(opens in a new tab)" label. Links between our own sites (`*.ullswaterinvestments.com`) stay in the same tab. Check any folder with `python3 src/extlinks.py docs --check`. The same file is used in www, calls, news and the project landings.
