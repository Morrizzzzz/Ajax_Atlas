# Ajax Atlas · 1950–2025

A dark interactive 3D globe and space-time player atlas. Starts with Amsterdam's three Saint Andrew's crosses. Static HTML, CSS and JavaScript: no installation, API keys, account or backend required to run the website.

## Publish on GitHub Pages

1. Extract this ZIP on your computer.
2. Create a GitHub repository (for example `ajax-atlas`).
3. Upload the extracted **contents**, keeping `index.html` in the repository root and keeping the `data` and `vendor` folders intact. Do not upload only the ZIP.
4. Open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, then **main** and **/(root)**, and save.
5. GitHub shows the published URL when deployment completes. All asset paths are relative, so a repository subpath works.

Official instructions: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

This package has not been pushed to or published on your GitHub account.

## Explore

- Enter from the XXX title screen.
- Drag the globe to rotate. Scroll or use +/− to zoom. Orbit toggles automatic rotation.
- Red dots mark birthplaces. A shared-location dot opens a list of its players.
- Search by player or senior club, or filter by position.
- Select a player for their birthplace, Ajax spells, and senior club history up to 2025. White dots mark mapped clubs, red dots Ajax. Connections are schematic.
- Click a timeline bar or move the slider to select an Ajax calendar year. **All years** restores the full period; **Play history** advances through years.
- **3D timeline** places players by their first Ajax year (X), birthplace latitude (Y) and longitude (Z). First years before 1950 are clamped to the left edge. This is a geographic timeline, not a performance chart.
- **Reset filters** clears search, position, year and birthplace selection. Reset view resets only the camera.
- Press `/` to focus search and Escape to close a player card.

## Data coverage and limitations

The included roster derives from Wikipedia's List of AFC Ajax players, with Ajax career overlap in 1950–2025. It is **not a verified complete register of all first-team appearances**. The source includes some contracted or reserve players with no league appearances, and it can omit players. Zero league appearances does not prove zero first-team appearances in other competitions. This project does not silently filter those records out.

Player profiles supply birthplace, birth date and senior club spells. Youth and national teams and managerial careers are excluded. Club careers may include reserve teams, amateur clubs and loans listed as senior career entries. Overlapping loan and parent-club periods are retained. Ajax date ranges from the roster are used where a parsed profile is unavailable, and are identified by `datesSource`.

Birthplace coordinates describe the linked settlement, not a hospital or address. Club coordinates describe the article's mapped location or a sourced stadium/headquarters where documented, which can reflect a modern rather than historical ground. Missing coordinates are null, never invented, and missing players remain in search. Dates are calendar years rather than season dates; the histogram counts roster career overlaps, not match-day squads.

The records were retrieved on 26 October 2026 and club histories are clipped to 2025. They are not an archived snapshot of what Wikipedia said on 31 December 2025. Every player and club has a source URL. Data provenance and coverage are also available through the in-app information button.

## Files and editing

- `index.html`, `style.css`, `app.js`: application.
- `data/players.json`: editable dataset with metadata and source URLs.
- `data/players.js`: same data wrapped as `window.AJAX_DATA=…;` so local file opening also works.
- `data/coordinate_sources.json`: coordinate sources.
- `data/world.js`: bundled Natural Earth country outlines.
- `data/coverage.json`: missing-record inventory and coverage counts.
- `scripts/`: optional data maintenance tools, not required by visitors.
- `vendor/`: Three.js and OrbitControls, bundled locally.

After editing `players.json`, run `python scripts/sync_data.py` to refresh `players.js` and the coverage report. The site does not contact Wikipedia at runtime. Google Fonts is an optional cosmetic request; local system fonts work if it is unavailable. The 3D renderer uses WebGL where available and an interactive Canvas projection fallback otherwise.

To serve locally: `python -m http.server 8000` in this directory, then open http://localhost:8000. Double-clicking `index.html` also works in browsers that permit local scripts.

To rebuild source data, install Python 3 and lxml (`python -m pip install lxml`) and ensure `curl` is on PATH. Run `python scripts/build_data.py --resume` to reuse the supplied parsed profiles, or omit `--resume` to reparse the roster snapshot and player pages. `python scripts/enrich_coordinates.py` performs batched MediaWiki lookups. The rebuild can take several minutes, and source changes or failed requests must be reviewed. Cached pages are reusable; do not publish the `.cache` directory.

## Credits and licence

- Wikipedia contributors: https://en.wikipedia.org/wiki/List_of_AFC_Ajax_players and individual URLs in the dataset. Reused text and this derived factual compilation: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/. Content has been extracted, normalised, filtered and geocoded.
- Natural Earth 1:110m countries: public domain, https://www.naturalearthdata.com/about/terms-of-use/.
- Wikidata stadium links and coordinates (P115/P625): CC0, with per-club coordinate source links.
- Three.js r128 and OrbitControls: MIT licence, see `vendor/THREE-LICENSE.txt`.
- Original application code: MIT, see `LICENSE.txt`.
- Visual interaction inspiration: https://paris.bogachev.fr/. No code or assets copied from that website.

Independent fan project. Not affiliated with or endorsed by AFC Ajax or the City of Amsterdam.
