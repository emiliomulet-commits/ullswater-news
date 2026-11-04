# EU Funding Events · Ullswater Investments

Static events site for **https://events.ullswaterinvestments.com**. Same model as the news site: one JSON file per item, a Python generator with no dependencies, plain HTML output.

- `src/events/*.json`: one file per event (the only thing you edit to publish).
- `src/build.py`: generates the site into `docs/` (not committed).

Cloudflare Pages settings: production branch `events-site`, build command `python3 src/build.py`, output directory `docs`.

Fields: `slug`, `title`, `start`, `end`, `type` (info-day, brokerage, conference, training, webinar), `programme`, `mode` (online, onsite, hybrid), `city`, `location`, `organiser`, `status` (scheduled, applications-closed, cancelled, postponed), `summary`, `details`, `why`, `tags`, `registration_url`, `source_name`, `source_url`.

Editorial rules: English only, own words, every date and place must appear in the linked source, `why` adds no facts, publish only after Emilio's OK.
