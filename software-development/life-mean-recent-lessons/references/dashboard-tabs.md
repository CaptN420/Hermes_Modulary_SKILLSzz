# Adding a tab to the Life_mean dashboard (`experiments/ui/dashboard.html`)

The dashboard is a single HTML file (~5,900 lines, 4 `<script>` blocks) that carries its own JS.
No framework, no build: each tab declares itself in **four places**, and one omission yields a
tab that does not open or a table that stays empty.

## 1. The four contact points

1. **Navigation button** in the bar:
   `<button class="tab-btn" data-tab="<name>" onclick="switchTab('<name>', this)">Label</button>`
2. **Panel**: `<div id="panel-<name>" class="tab-panel">…</div>` — the `id` must be
   `panel-` + the `data-tab`, otherwise `switchTab` finds nothing and the tab stays on the previous one.
3. **Hook in `switchTab(name, btn)`**: `if (name === '<name>') loadX();` — without it the panel
   appears but never loads its data (silently empty table).
4. **JS function** `loadX()` + a separate `render()` when there is a filter, so as not to redo a
   fetch on every filter change.

## 2. Conventions to reuse

- `API_BASE = '/api'`; `piGet(path)` / `piEsc(value)` already exist (HTML escaping is mandatory).
- Existing classes: `card`, `subtitle`, `pi-table`, `pi-badge`, `empty-state`, `tab-btn`.
  A `<td colspan="N" class="empty-state">` must always carry **a message**, never emptiness.
- "Provenance" pattern: show where the data comes from rather than the figure alone —
  "run rehydrated from the persisted summary — 4/4 traces kept",
  "14 observed / 989 loaded — 4500 events over 25 populations (truncated)".
  A counter without coverage reads as a total; an empty table without a reason reads as an outage.
- An unavailable source displays **its reason** (the payload's error text), not a plausible value.

## 3. Pitfalls that cost the most time

- **A `const`/`let` redeclared in the same `<script>` block neutralises the whole block**: the tabs
  stop responding with no visible error in the UI. Audit each block in isolation:
  `python "<skill_dir>/scripts/audit-js-blocks.py" experiments/ui/dashboard.html`
  (expected output: `[OK] bloc N` for each one). An OK proves a duplicate did not slip through.
- **Do not blame the UI before querying the API inside the page.**
  `js("fetch('/api/pipeline/features').then(r=>r.json()).then(d=>{window.__probe=JSON.stringify(...)})")`
  then read `window.__probe` back: that separates "the route returns nothing" from "the rendering does not apply".
  A heavy load (4–5 s on 1 M events) looks like a bug if you do not give it time.
- **The Docker image `COPY`s the code**: until the image is rebuilt, the browser serves
  the old HTML. `docker compose build dashboard && docker compose up -d`, then check that the
  expected content is actually being served.
- **Python tests do not validate rendering.** `test_dashboard_ui.py` checks strings/aliases, not
  that a tab works: the proof is a real browser (see §4).

## 4. Verification recipe (the one that counts)

1. `audit-js-blocks.py` on the HTML → all blocks `[OK]`.
2. Rebuild the image if the code changes, otherwise start the host dashboard:
   `.venv/Scripts/python -m experiments.dashboard --port 8082 --host 127.0.0.1`
   (port 8080 is taken by the container; the host additionally sees the real Windows collectors).
3. Drive the browser: `new_tab(url)`, then
   `js("switchTab('<name>', [...document.querySelectorAll('.tab-btn')].find(b=>b.dataset.tab==='<name>'))")`,
   wait (3–10 s depending on the API), and read the `innerText` of each zone:
   counter, provenance line, 2–3 rows of the table.
4. Test the filter in both directions (total → filtered) and check the displayed count, not just
   the presence of rows.
5. `capture_screenshot()` for the human eye — useful but **not** a proof in place of the `innerText` reads.

## 5. Real examples (structure to copy)

- **System** tab (`panel-system`, `sysLoad`): Defender cards + event table, `degraded` line
  when a source does not answer (`not a Windows host` in the Linux container).
- **Traces** tab (`panel-traces`, `trLoad`/`trFetch`/`trSetRule`/`trRender`): `<select>` of runs
  from `GET /api/experiments`, filter by rule, table `time · rule · task · input · output`,
  and provenance note (`d.rehydrated`, `restored_totals.traces`, `traces_absent_reason`).
