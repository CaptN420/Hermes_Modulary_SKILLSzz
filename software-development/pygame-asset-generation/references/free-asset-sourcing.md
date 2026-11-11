# Sourcing Free Game Assets (CC0 / commercial-use)

Workflow for finding external art/sound assets compatible with a project's style, when the user wants free assets with verified licenses. NEVER download before the license is verified on the source page.

## Procedure

1. **Audit the project's current visual state first** (read the renderer/level/menu code, don't assume):
   - grep for `pygame.image.load`, `pygame.draw`, `Surface(`, `convert_alpha` to find how things are actually drawn.
   - List any existing image/audio files (`find . -type f \( -iname "*.png" -o -iname "*.wav" -o ... \)`). Many projects are 100% procedural rects — that defines the target style (or its absence).
   - Note the user's stated target style from memory/profile (e.g. authentic 16-bit pixel art, 32x32 / 96x128).
2. **Search in parallel** across the reliable CC0 hubs (one web_search per category: characters, enemies, tiles, UI, effects, sounds, music). Batch independent searches in one turn.
3. **Verify the license on the source page before listing or downloading**:
   - Kenney (kenney.nl / kenney-assets.itch.io): everything is CC0 — commercial OK, no attribution required.
   - itch.io free packs: read the page's License & Usage block; `Creative Commons Zero (CC0)` is the green light. Watch for extras: "no NFT", "don't resell the asset alone", "free version = fewer animations, paid has the rest" (e.g. Mattz Art samurai: free = 4 anims, $3 = 19).
   - OpenGameArt (opengameart.org): license shown per item — CC0, OGA-BY, CC-BY 3.0, CC-BY-SA. CC-BY 3.0 = commercial OK but ATTRIBUTION REQUIRED → keep a `CREDITS.txt` in assets/.
   - `web_extract` on OpenGameArt often returns a login wall / empty body → fall back to the search-result snippet which carries the license line, and state that the license came from the search snippet.
4. **Flag AI-generated packs** (FreeGameSprites, SPRITEARTS-style itch packs, anything with "AI Disclosure: AI Assisted"): CC0 but NOT authentic hand-made pixel art → exclude when the user wants authentic style; if included, mark it.
5. **Present the shortlist grouped by category** with columns: asset name · source URL · license · proposed project location (e.g. `assets/images/characters/player/`, `assets/sounds/`, `assets/music/`). Map assets to actual in-game needs (bosses, archetypes, map themes, missing music file references).
6. **Get user confirmation before downloading** — they may want a subset.
7. **Download per-site with the protocols below** — verify the zip's embedded License.txt (`unzip -p <file> License.txt`) BEFORE extracting, and confirm the file is a real zip (magic bytes `504b0304`).
8. **Verify install**: load a sample of the PNGs through the project's venv python (`pygame.image.load`) — catches corrupt/truncated downloads.

## Downloading (verified protocols)

Use curl/Python HTTP, not the browser, for asset downloads — the sites serve them fine over plain HTTP with a browser User-Agent header. (The Hermes browser may be unavailable when a real browser profile is locked; plain HTTP sidesteps that entirely.)

### Kenney — direct zip link in the page HTML
Grep the asset page for the zip: `curl -sL -A "<UA>" https://kenney.nl/assets/<slug> | grep -oE 'kenney\.nl/media[^"\']*\.zip'` → gives a `kenney.nl/media/pages/assets/<slug>/<hash>/kenney_<slug>.zip` URL. Every Kenney pack embeds `License.txt` = CC0.

### OpenGameArt — curl works where web_extract hits the login wall
`curl -sL -A "<UA>" https://opengameart.org/content/<slug>` returns the page; grep `href="[^"]*\.(zip|png|PNG|mp3|ogg|mid)"` for `opengameart.org/sites/default/files/` file URLs. Extract the license from the same HTML: `grep -oiE "CC[- ]?[0-9A-Z-]+|OGA[- ]?BY"`. Some packs ship as `.7z` (e.g. Ardentryst) → extract with `pip install py7zr`; verify the file magic bytes (`377zbcaf` for 7z).

### itch.io — POST to `/file/{upload_id}`, NOT the `download_url` endpoint
This is the reverse-engineered flow that actually works (the `download_url` → `accept_nda` + `download_key` path is a rabbit hole: CSRF tokens expire per attempt and the key is double-URL-encoded).
1. GET the game page → extract `csrf_token` (meta tag `name="csrf_token"`).
2. POST `{page_url}/file/{upload_id}` with body `csrf_token=<csrf>&source=game_download` → returns JSON `{"url": "<s3-direct-url>"}`.
3. GET that S3 URL → the actual file.
Getting `upload_id`: free packs often expose it as `data-upload_id="<id>"` on the game page; if absent (name-your-price flow), POST to `{page_url}/download_url` with just the csrf, GET the returned one-time URL, and read `data-upload_id` from THAT page.
**Do the whole chain in ONE Python process with a shared cookie jar** — the CSRF token is replaced between steps and each one-time URL is single-use. `scripts/itch_download.py` implements this end-to-end.

## Known-good CC0 sources (verified)
- Kenney: Pixel Platformer (200+ sprites: tiles, chars, enemies, HUD, items), UI Pack (430 pieces), Impact Sounds (130 combat hits), New Platformer Pack. All CC0.
- Brackeys' Platformer Bundle (itch.io): knight + slime + 16x16 tilesets + coins, CC0.
- LuizMelo Martial Hero / Martial Hero 2 (itch.io): animated fighter, CC0.
- OpenGameArt: 16-bit Battle Theme I (HydroGene, CC0), Factory / Lava Dungeon Battle (CC0) — good per-map music swaps.

## Pitfalls
- Verify license on the source page, not on aggregator blurbs — one pack can differ from the marketplace it's mirrored on.
- itch.io "free" is not a license: read the License & Usage block every time; name-your-price packs with a minimum price are paid.
- Keep CC-BY assets out of CC0 projects unless you record attribution — a `CREDITS.txt` per pack in assets/ prevents silent license drift.
- itch.io free downloads often have NO upload_id on the game page and NO License.txt inside the zip — the license lives only on the itch page's License & Usage block. Read it before downloading and record it in CREDITS.txt.
- Chain CSRF-token steps in a single HTTP session; itch.io CSRF tokens expire between curl invocations (separate processes each get their own cookie jar), so per-step curl round-trips fail with `token expired`/`missing download key`.
- curl on Windows bash can die with exit 23 (write error) when `$TMPDIR` is an unusable path — pass an explicit scratch output directory (e.g. `$LOCALAPPDATA/hermes/profiles/def/cache/scratch/...`), and always send a browser User-Agent or some sites 403/return garbage.
- Verify `pygame.image.load` succeeds on a sample before declaring a pack installed — truncated downloads fail at runtime, not at `unzip`.

## Related scripts
- `scripts/itch_download.py` — end-to-end itch.io free-asset downloader (game slug + page URL + upload_id → file). Reusable for any itch.io CC0 pack.
