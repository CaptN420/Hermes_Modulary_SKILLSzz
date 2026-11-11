---
name: life-mean-dashboard-qa
category: root
description: Use when QA-testing the Life_mean dashboard.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [qa, dashboard, sqlite, testing, docker]
    related_skills: [life-mean, life-mean-recent-lessons, dogfood-python]
---

# Life_mean Dashboard QA

Target: `http://127.0.0.1:8080/dashboard`. Canonical launcher: `run_server.bat` at the project root (kills zombie listeners on the port, then starts the server). It forwards `--host`/`--port` — `dashboard.py`'s `__main__` now takes those via argparse, so start with `run_server.bat` or `run_server.bat 9099` for a custom port. Manual equivalent: `python -m experiments.dashboard --port 8080`.

## Security Hardening (Audit Requirements)
- **SQL Security**: Replace concatenated queries with parameterized queries; validate all inputs.
- **Frontend Safety**: Use `textContent` for LLM responses; avoid `innerHTML` for non-sanitized content.
- **Network/CSP**: Implement a strict Content Security Policy (CSP); default to `127.0.0.1` and disable ports when dashboard is inactive.
- **Agent Isolation**: Ensure tools are isolated; logs/outputs are untrusted; sensitive actions require backend-side controls.
- **Sandbox Hardening**: In `LabOrchestrator`, avoid `os.environ.copy()` for full environment inheritance; use a whitelist of required variables to minimize the sandbox attack surface.

## Architectural Evolution (MIA v0 -> Life_mean)
- **Brain/Hands Model**: MIA v0's `BaseDebateCore` (Brain) and `Orchestrators` (Hands) evolved into the `core` logic and `LabOrchestrator`.
- **Deterministic Runtime**: The `SandboxWorkspace`, `ResourceLimits`, and `AbortRegistry` in `LabOrchestrator` are the modern implementation of the Captn framework's session isolation and rollback guarantees.
- **Bloodstream**: JSON message passing between the core and workers remains the primary data flow mechanism.

## Pitfalls
- **"List renders empty but curl returns data"**: This is a backend-serialization or stale-HTML bug, NOT a fetch bug. Debug order: (1) `curl` the endpoint; (2) register `error`+`unhandledrejection` listeners and reload; (3) byte-check the dataclass `to_dict()`; (4) `location.reload()` to clear cached HTML.
- **Zombie Servers**: Old servers persist across sessions; a stale listener serves the PREVIOUS code, so your change looks like it did nothing (or a newly added route 404s although the source clearly has it). Before verifying anything: `netstat -ano | grep LISTENING | grep <port>` → owning PID → `taskkill /F /PID <pid>`. Then restart and confirm the owning PID CHANGED — a server that fails to bind exits quietly in the background while the old one keeps answering.
- **Route registered in the wrong HTTP method**: each branch lives inside `do_GET` / `do_POST` / `do_DELETE`. A handler method can exist and still be unreachable (e.g. `/api/training/runs` answering 404 on GET because its branch sat in `do_DELETE`). Find the enclosing method by line number — `grep -n "^    def do_" experiments/dashboard.py`, take the last one above the route line — instead of assuming, and pin it with an HTTP-level regression test that GETs the route.
- **Sandbox Env Leak**: Using `os.environ.copy()` in `LabOrchestrator` inherits potentially sensitive host variables; prefer explicit whitelisting for production-grade hardening.
- **Windows `.bat` execution**: Invoke directly (`./run_server.bat`) from git-bash, NOT via `cmd //c`, to avoid interactive prompt hangs.

## How to run QA
- The cloud browser backend can't reach `127.0.0.1`. Use the LOCAL browser driver (browser_exec local=true).
- **The container's `data/` is a NAMED VOLUME (`life_mean_data:/app/data`), NOT a mirror of the host `data/` tree.** The dashboard reads `/app/data/subjects` and `/app/data/raw_debates` INSIDE the container. Empty-volume symptoms: `/api/compare/tree` crashing with `FileNotFoundError: /app/data/subjects`, and `/api/compare/browser` returning `count: 0` with a stale `generated_at` while the host tree holds hundreds of runs. Sync host→container with `docker cp data/subjects/. <container>:/app/data/subjects/` and `docker cp data/raw_debates/. <container>:/app/data/raw_debates/` (docker cp writes into mounted volumes even when the image rootfs is read-only — `docker build`/`docker cp` into the image root is refused, volumes are not). Then force an index rebuild via `GET /api/compare/browser?refresh=true` (rebuild only fires when RAW mtime is newer or refresh is set — the sync alone leaves the old empty `compare_index.json` in place). Keep the defensive `if not base.is_dir(): return node` guard in `compare/subjects.py _walk()` so a missing subjects dir degrades to an empty tree instead of a 500.
- The real-profile Brave lock can block the browser: quit Brave or run `hermes browser close-profile`.
- To restart the server: kill PIDs listening on the port via `netstat -ano | findstr :8080` + `Stop-Process`, then relaunch (`run_server.bat` does this for you). After changing `dashboard.py`, ALWAYS kill the old listener first — a stale process serves the previous code and looks like your change did nothing.
- Decide the port before launching and probe THAT port: check it is free first (`netstat -ano | grep LISTENING | grep <port>`); if an unrelated app holds it, start on another port and keep probing the same one. Never assume the printed default is what your process actually bound.
- The full test suite runs several minutes; a default 300 s foreground `pytest` call gets killed mid-run and reports nothing. Pass a larger `timeout=` or run it with `background=true, notify=true` and read the tail. `--timeout=60` is not available unless pytest-timeout is installed — don't add it to the command line blind.
- **Invoke a Windows `.bat` from git-bash by running the file directly (`./run_server.bat 9099`), NOT via `cmd //c run_server.bat 9099`.** `cmd //c` on a pty opens an interactive prompt that hangs instead of running the script — the process sits there and the port stays closed. Direct invocation executes and returns correct logs.
- Create/start/delete experiments via `POST /api/experiments`, `POST /api/experiments/{id}/start|stop`, `DELETE /api/experiments/{id}`.
- Packages LM (read-only): `GET /api/packages` (catalogue + `valid_count`), `GET /api/packages/inspect?path=<file>` (manifest, agents, two verdicts), `POST /api/packages/validate {path}`. Paths resolve inside `lmpack/`; anything absolute or containing `..` must answer `404 package_not_found`. QA rule: a ZIP that opens is `readable`, not `valid` — a pack with zero agents must report `valid: false`.
- Code Lab runs via `POST /api/code-lab/runs` (creates+starts), `GET /api/code-lab/runs`, `/runs/{id}`, `/runs/{id}/files`, `/runs/{id}/events`, `POST /runs/{id}/start|stop`, `DELETE /runs/{id}`.
- Register `window.addEventListener('error')` + `unhandledrejection` collectors BEFORE `location.reload()`, and re-render with synthetic data (`renderCodeLabRuns([{run_id:'t',status:'passed',config:{prompt:'x'}}])`) to isolate "fetch failed" vs "render threw" — see the to_dict pitfall below.

## Known architecture (as of 2026-10)
- `dashboard.html` — single page; tabs are `<button class="tab-btn" data-tab="X">` and `switchTab(name, el)` toggles `.tab-panel.active` then dispatches the per-tab loader (`piLoadAll()` for Pipeline, `pkLoad()` for Packages). Adding a tab means touching three places: the nav button, `<div id="panel-X" class="tab-panel">`, and the loader dispatch inside `switchTab` — miss the third and the tab opens empty. Debate tab runs the old experiment flow (`setInterval(loadExperiments, 5000)`); Code Lab tab polls `loadCodeLab()` every 3s while active.
- `experiments/ui_controller.py` — ExperimentUIController: states, metrics, delete_experiment().
- `experiments/dashboard.py` — HTTP server + DashboardHandler (do_GET/POST/DELETE). Shares routes for experiments AND code lab on the same handler; `start_dashboard()` accepts an optional `code_lab_controller`.
- `code_lab/` — CodeLabController (runs registry), CodeLabEngine (PLANNER→generator→real pytest→compile-validate→RAW), CodeLabWorkspace (isolated runs/<id>/). Dashboard auto-creates a CodeLabController when the import succeeds.
- `experiments/runner.py` — ExperimentRunner._execute_task: tool param extraction by keyword (math gcd/lcm/fact/prime/fib; physics force→mass/acceleration; chemistry molar_mass→formula) + answer-key mapping.
- `experiments/generation/task_generator.py` — deterministic GT; chemistry GT now calls the real molar_mass tool (real atomic masses) so answer and GT always agree.

## Metrics gotcha
- `_run_experiment_loop` reports tasks_valid/tasks_invalid/counts; update_metrics only changes a field if the key is present. Keep all counters in the same update_metrics call.

## Pitfalls
- **"List renders empty but curl returns data and console shows zero JS errors" is a backend-serialization or stale-HTML bug, NOT a fetch bug.** Debug order: (1) `curl`/raw `fetch` the endpoint — if it returns N items the server is fine; (2) register an `error`+`unhandledrejection` listener and reload — a missing field like `r.config.prompt` throws inside the async render and gets logged only if you captured it; (3) byte-check the dataclass `to_dict()` — the network payload may simply omit a key the JS expects; (4) after fixing the backend, `location.reload()` the browser — re-calling the same JS with cached HTML keeps showing the stale empty state.
- Dashboard server needs `if __name__ == "__main__"` block to run via `python -m` (was a past bug).
- Old zombie servers on 8080 persist across sessions; always kill listeners before restart, else curl hits the stale process.
- chemistry/physics ground truth MUST come from the executing tool (real atomic masses O=15.999), not the description's simplified masses.
- `difficulty_range` and `num_tasks` are validated in `dashboard.py _create_experiment` (num_tasks>0, ascending range, clean messages).

## Files
- QA report: `dogfood-output/report.md`, screenshots in `dogfood-output/screenshots/`.
- Regression tests: `tests/test_qa_fixes.py` (10 tests).
