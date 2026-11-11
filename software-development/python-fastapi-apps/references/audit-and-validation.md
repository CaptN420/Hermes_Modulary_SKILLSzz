# In-app audit / validation module

Recipe for adding a real project-audit feature to a FastAPI app (routes inventory,
module contracts, static source scan, external scanners, aggregate verdict)
without breaking the live app.

## Structure
- `route_inventory(app)` — enumerate `app.routes`. **`Mount` (StaticFiles) has no
  `.endpoint`** and `methods` can be `None`: use `getattr(r, "endpoint", None)` and
  `getattr(r, "methods", None) or []`, else you raise AttributeError on the mount route.
- `module_contracts()` — import each module in-process (`__import__(mod, fromlist=["*"]`),
  assert expected public attrs exist and are callable; separately check class methods
  (`getattr(mod.Cls, m)`), they are NOT module attrs. Add a static AST pass over sibling
  imports to detect circular imports (DFS with colour marking).
- `source_scan()` — regex the package `.py` files for eval/exec, `os.system`, `subprocess
  shell=True`, hardcoded-secret assignment, `pickle.loads`, path-traversal write patterns.
  Keep each rule's pattern PRECISE: a broad pattern like `work_dir / f"...{var}"` false-
  positive on legitimate safer uses (a validated doc_id, `Path(...).suffix`). Match the
  actual vulnerable shape only (e.g. `upload_...{name}`), so the rule goes silent when the
  vuln is fixed — that silence is the evidence the fix worked.
- Wrap external tools as subprocess with graceful absence: build the arg list with
  `sys.executable`, run, parse JSON, return `available: false + error` when the module is
  missing or the output isn't JSON.
- Aggregate + persist to a JSON file (e.g. `studio_data/audit.json`) and load-last for the UI.
- **Gate capacity-exceeding actions behind an env flag** (`AUDIT_ALLOWED`, default on for
  a local-loopback tool): tests + subprocess execution switch off with `AUDIT_ALLOWED=0`
  while read-only views (routes/modules) stay live.

## Scanner exit-code gotchas (they mislead fast)
- **`pip-audit` exits code 3 when it FINDS vulnerabilities** — that is a SUCCESSFUL audit
  with findings, not an unavailable/failed run. Parsing `returncode != 0` as "error"
  silently hides real CVEs. Parse `stdout` as JSON FIRST regardless of exit code; fall back
  to an error result only when JSON parsing fails.
- **Bandit returns exit 1 when it has findings**, exit 0 when clean — treat both as available;
  2 (error) as unavailable. Bandit's `B404`/`B603` on your `subprocess.run` arg lists are
  usually benign (static arg lists, the scanner tool itself) — downgrade to informational,
  keep the real findings. `B104` fires on a literal `"0.0.0.0"` bind: fix by making the
  host a CLI parameter defaulting to `127.0.0.1`, then re-scan the file to confirm 0 findings.
- **Normalize severity vocab before aggregating heterogeneous scanners.** Bandit emits
  `critical/high/medium/low`, your app may use another vocabulary (e.g. French
  `critique/elevee/moyenne/faible/info`). If you don't map one to the other, `by_severity`
  gains stray keys and the `overall` verdict thresholds (`seeing` <= N) silently never fire.
  Map English->canonical at conversion time, then aggregate on the single vocabulary. If you don't, the `overall` verdict, computed by ranking each issue against severity thresholds, silently never rises.

## Test-writing pitfalls seen with these modules
- A `class _F:` inside a function does NOT close over the enclosing function's locals
  (`class _F: filename = filename` -> NameError); use `types.SimpleNamespace(filename=...,
  file=io.BytesIO(...))` as fake UploadFile.
- `_PKG_DIR / rel.split(".",1)[1].replace(".", "/") + ".py"` — `+` binds tighter than `/`,
  so `str + Path` raises `TypeError`. Compute the relative path into a variable string, then
  join: `_PKG_DIR / "config.py"`.
- Verify HTTP audit endpoints with `httpx.AsyncClient(ASGITransport(app))` inside
  `asyncio.run()`; a plain sync test is enough and needs no anyio marker.

## Verify by real execution
Run the module headless first (`run_full_audit(include_external=False)` -> routes/modules/
source), then hit the live endpoint with a full run and assert the aggregate verdict,
counters and persisted file. Confirm the UI wiring in a real browser: click the action
button, then poll the DOM for the rendered table (never a fixed sleep).
