# Extending the Life_mean dashboard (API surface + UI tab)

Recipe and pitfalls for adding a new capability to `experiments/dashboard.py`.
Validated on the packages surface (`/api/packages*`), where a reader existed but no
route did, so the whole feature was unreachable.

## Layout of an extension

1. New module `experiments/<topic>_api.py` exposing a `<Topic>ApiMixin` class.
   Keep helpers as module-level functions so tests can call them without a server.
2. Wire it: add the mixin to `DashboardHandler`'s bases, one GET branch and one POST
   branch in `do_GET`/`do_POST`. Handlers answer via `self._send_json(...)` /
   `self._send_error(status, msg, code="...")` — use the shared helpers, never
   raw `wfile` writes.
3. UI: a `<button class="tab-btn" data-tab="x">` next to the existing tabs, a
   `panel-<x>` div, and a `switchTab` hook (`if (name === 'x') { xLoad(); }`).
   Put the JS in its own `<script>` block at the end of the body, prefixed names
   `pkLoad`, `pkInspect`) to avoid colliding with existing globals. Hook the loader
   into `switchTab`; a panel whose loader runs only at boot shows stale emptiness.
4. Tests: a `_FakeHandler` subclass of the mixin capturing `_json` / `_code` /
   `_err_code` — a full HTTP server is only needed for CSRF or routing-order tests.
   For handlers that live on `DashboardHandler` (not a mixin), bind them onto a plain
   class (`_agents_list = DashboardHandler._agents_list`) and bind every dependency
   they call, e.g. `_storage = PackagesApiMixin._storage` — a missing one shows up as
   `handler.json is None`, not as a clear error.
5. Storage cache: `studio_storage()` caches one handle per database path (SQLite +
   Windows file locks). Tests that point `LIFE_MEAN_STUDIO_DB` at a temp file must
   call `reset_studio_storage()` before and after, or they read the previous DB.

## Pitfalls that cost real time

- **A conflict check that looks up an id the store generates itself can never match.**
  `create_agent()` mints a UUID, so `get_agent(package_agent_id)` was always None and
  re-importing the same pack silently doubled the registry. Detect identity by a
  natural key (name, case-insensitive), not by an id you did not create.
- **Prove idempotence by doing the operation twice and counting rows.** First import
  → N rows; second import of the same source → still N rows and an explicit
  conflict list. A single successful call says nothing about duplicates.
- **Never let a status message collapse two different truths.** "No content imported"
  when every item already exists is a false report; say "Nothing new: N item(s)
  already present" and return success=false with the conflicts attached.
- **`readable` and `valid` are different fields.** An archive that opens is not a
  valid package: require a reader's verdict *and* at least one usable item, and
  test a manifest-only pack to pin the distinction.
- **Report each reader's verdict separately, never averaged.** Two independent
  readers (Studio `PackageManager`, core `LLMPackager`) plus an `agreement` flag;
  a disagreement is displayed, not merged into one boolean.
- **Confine every user-supplied path.** Reject absolute paths and `..`, resolve and
  verify the root is a parent, then test at least: `../x`, `../../.env`,
  `C:/Windows/win.ini`, `/etc/passwd`, nested traversal, empty string.
- **The image is `read_only: true`, so writes in the container go nowhere.** A write
  endpoint needs an overridable path (`LIFE_MEAN_STUDIO_DB`), a named volume, and a
  `chown` in the `volumes-init` service. Prove durability with
  `docker compose restart` then re-read the DB (`docker exec … python -c "sqlite3 …"`)
  — a 200 is not persistence. Report the database path in the response so the caller
  can see where data landed.
- **Preview and redact, never dump.** Prompts and readmes come back truncated
  (~160 chars) after passing `pipeline_inspector.redaction.redact_text`.

## Wiring a write endpoint to real storage

Order that works: reproduce the defect against a temp database → fix the store →
expose the route → live POST + read-back → only then touch the UI.

- **A route branch in the wrong dispatch method survives every mixin test.** Fake
  handlers call `_agents_toggle(...)` directly, so parser-level mistakes are
  invisible: a branch dropped into `do_GET` answered 404 on a real `POST` while the
  suite stayed green. Finish with a real `POST http://127.0.0.1:8080/api/...`
  against the rebuilt container, for both the success and the 404/409 paths.
- **`status: "created"` plus a generated id and no write is a fake success.** Grep
  the handler for fabricated ids (`f"agent_{uuid4().hex[:8]}"`) and hardcoded
  template lists before trusting it. Create through the store, then `get_<entity>(id)`
  and answer only if the row comes back (`persisted: true, verified: true`); otherwise
  500. Same for a list endpoint: it must read the registry, not a literal.
- **Toggles/updates re-read the row before answering** and expose
  `verified: <stored == requested>`. Unknown id → 404 `<entity>_not_found`, duplicate
  natural key → 409 `<entity>_exists`, storage refusal → 409. Never report a change
  you did not read back, and never delete to resolve a duplicate (NO DELETE).
- **Replacing a hardcoded list keeps the fields the UI already reads.** The registry
  payload kept the legacy `type` alias so the existing Agent Builder kept rendering:
  no breaking change without a migration.
- **Mapping source JSON into storage silently drops unmapped fields.** Pack agents
  carried `role` ("Transformation") that the importer discarded, leaving eleven
  identical cards; map it onto a real column (`description`) rather than inventing a
  taxonomy. Do not backfill rows written before the fix — rewriting stored user data
  unasked violates no-silent-rewrite; state the gap in the report instead.

## Editing inline JS/HTML without wrecking the diff

- Read with universal newlines and write back in the file's own style
  (`nl = "\r\n" if "\r\n" in raw else "\n"`). A hardcoded `newline="\r\n"` write
  converted a whole LF file and turned a 60-line change into a whole-file diff.
- The `patch` tool can miss long JS blocks whose blank lines carry trailing spaces;
  fall back to Python span surgery (`src.index("def x(")` … `src.index("def y(")`)
  instead of retyping the block.
- Re-run the inline-script syntax probe after **every** edit: a regex replacement
  that leaves one extra `}` gives `all_ok: false` and a silently blank tab.

## Verifying the UI for real

- Syntax-check every inline `<script>` block before rebuilding; a single stray brace
  blanks the whole tab.
- Rebuild the image (code is copied in, no bind mount), then drive a real browser:
  click the tab, read the panel's `innerText`, click the action button, read the
  status line, and take a screenshot. Reading the HTML source is not evidence that
  the tab renders.
- When a confirm/alert would block a headless click, patch it first:
  `js("window.confirm = () => true")`.
