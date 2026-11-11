---
name: life-mean-recent-lessons
category: software-development
description: Use when working on Life_mean lessons. Dated Oct 2026 log, temporary and archivable.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [python, multi-agent, synthetic-data, sentinel, provenance]
    related_skills: [life-mean]
---

# Life_mean — Recent Lessons (Oct 2026)

## When to Use

Load this skill when a task touches Life_mean / Life_mean_realm on the following topics:
Pipeline Inspector, log ingestion, Feature Pool and its statuses, HTML dashboard and its tabs,
validation reports, orchestrator and permissions, or Docker deployment of the dashboard. The lessons in this file are
durable rules verified in execution; the detailed ingestion mechanics are in
`references/incremental-ingestion-offsets.md`, pool discovery in
`references/feature-pool-discovery.md`, the orchestrator's HTTP surface/authentication in
`references/orchestrator-permissions.md`, and the procedure for adding a tab/view to the dashboard in
`references/dashboard-tabs.md`.

## Agent Builder (2026-10-31)
- **Storage**: Added `agents` table to `StudioStorage` with CRUD ops (create, get, list, update, delete, duplicate, search).
- **AgentManager**: New class at `life_mean_studio/engine/agent_manager.py` — manages agent lifecycle + LLM integration via LM Studio.
- **UI**: Replaced "Not Implemented" placeholder in Dev Studio > Agent Builder tab with full functional UI (list/create/edit/delete/duplicate/test).
- **Personas**: Added `life_mean_studio/engine/personas.py` with 7 scientific personas (Lavoisier, Mendeleev, Dalton, J.J. Thomson, Rutherford, Bohr, Molecular Model Teacher).
- **Tests**: `tests/test_agent_manager.py` — 9 tests passing (CRUD, config, enabled toggle).
- **Test command**: `uv run pytest tests/test_agent_manager.py -v`.

## Historical Thinkers & Patterns (2026-10-31)
- **Patterns module**: `life_mean_studio/engine/patterns.py` — 10 prompts for physical geometrical patterns (fractals, spirals, symmetry, Turing patterns, etc.).
- **Historical thinkers**: `life_mean_studio/engine/historical_thinkers.py` — 10 prompts for thinkers between alchemy and scientific revolution (Paracelsus, Agrippa, Bruno, Kepler, Newton, etc.) + comparison table.
- **AgentManager extended**: Added `load_persona()`, `load_pattern_prompt()`, `load_thinker()`, `list_available_personas()` methods.
- **Total personas available**: 27 (7 scientists + 10 patterns + 10 thinkers).

## Sentinel model configuration
- **Default model**: `SentinelConfig.model_id = "qwen3.5-2b"` (`core/safety/sentinel.py`). Used for Layer B LLM analysis. If not loaded in LM Studio, degrades to deterministic-only.
- **Provider derivation**: `_derive_provider()` inspects `llm.base_url` to detect lm-studio/openai/anthropic/etc. Returns None if LLM client not wired.
- **Test command**: `cd /c/Users/celes/Documents/Hermes-Workspace/Life_mean && uv run pytest tests/test_sentinel.py -v` (31 tests pass).
- **Dashboard without Docker**: `python -m experiments.dashboard --port 8080`. Docker Desktop not running on this machine.
- **API endpoint**: `GET /api/sentinel/status` returns `{enabled, provider, model_id, analysis_mode, queue_size, alert_count, llm_available}`.

## Provider provenance fix (2026-10-31)
- **What was fixed**: `Turn.to_dict()` now serializes `model` and `provider` fields when available, matching RAW events and SQLite records.
- **Files changed**: `philosophical_council/core/turn_manager.py` added `provider` field and parameter to `complete_turn()`. `philosophical_council/core/debate_engine.py` added `_derive_provider()` and passes both to `complete_turn()`.
- **Tests**: `tests/test_turn_model_provenance.py` has 11 tests covering serialization, backward compat, SQLite+JSON round-trip, and two-different-models E2E.
- **Historical runs unchanged** per immutable RAW rule. New runs have consistent provenance across all three layers.
- **Test command**: `uv run pytest tests/test_turn_model_provenance.py -v`.

## GitHub access note
- Network blocked by Tailscale. DNS resolution fails for github.com.
- To make repo private: use browser at https://github.com/CaptN420/Life-Mean-Labs then Settings Danger Zone Change repository visibility to Private.
- Or when network allows: `gh repo edit Life-Mean-Labs --private`.

## CaptN Runtime v1 (2026-10-31)
- **Location**: `captn_runtime/captn/runtime/__init__.py`
- **Architecture**: Routing, Context (Compression), Experience, Telemetry engines.
- **Feature 1 — Adaptive Context Compression**: Integrated with `code_lab.compression.ContextBudget` via lazy initialization. Falls back to recency-based compression when unavailable.
- **Feature 2 — Intelligent Model Routing**: `ModelRouter` with difficulty classification (0-4), worker scoring, fairness boost, opposition mode for diversity.
- **Feature 3 — Experience Memory System**: JSONL persistence, derivation trees, query expansion for better matching.
- **Feature 4 — Telemetry & Observability**: Per-model stats, alerting on latency/cost anomalies, dashboard integration.
- **Test command**: `cd /c/Users/celes/Documents/Hermes-Workspace/Life_mean_realm && python -m py_compile captn_runtime/captn/runtime/__init__.py`

## Pipeline Inspector & Feature Pool — durable rules

- **A BROKEN/BLOCKED status is never inferred from a character count.** Validate the syntax with `ast.parse(source, filename=...)` and a per-file cache. Comparing `content.count('(')` to `content.count(')')` produces massive false positives (docstrings, f-strings, regex) and buries healthy code. If an audit announces N broken features, replay the check with a real parser before believing the audit.
- **VALIDATED requires test evidence.** `READY` = the code parses and its dependencies resolve; `VALIDATED` = at least one associated test file. Never promote a status because a feature was discovered or analyzed: `no_tests` is a *coverage gap* (`feature.coverage_gaps`), never a defect of the code nor a reason for BROKEN.
- **Two file names for the same report = the stale one wins.** When a producer writes `feature_pool_report.json` and a consumer reads `.feature_pool_report.json`, the consumer now picks the most recent file by mtime and exposes `generated_at`; the export writes the same payload to both locations (no deletion). Always check *which* file a consumer actually loaded before interpreting its numbers.
- **Analysis counters must declare their sample.** Analyses that read "the last N events" carry their payload with `sample: {events_scanned, limit, truncated, note}`; without that, a sample counter is read as an exhaustive total.
- **Masking: a length threshold is a security hole.** Require a non-empty value, not a minimum length (`password=hunter2`, 7 characters, passed in clear). Also cover `access_key`, `AKIA…` keys and PEM blocks.
- **A single `SyntaxError` neutralizes a whole `<script>`.** Two causes encountered in the dashboard: `const` redeclared in the same scope, and a literal string cut by a real newline. Symptom seen by the user: "the tabs don't change". Check each block in isolation with `node --check` (script provided in `scripts/audit-js-blocks.py`) — a duplicated `const` cannot pass, so an OK proves the fix.
- **Life_mean dashboard: the POST requires the `X-Lifemean-CSRF` header** (double-submit of the `lifemean_csrf` cookie), not `X-CSRF-Token`. A 403 on a POST from a manual test most often comes from there. Validate routes with real requests (GET + POST with cookie) rather than by re-reading the handler.
- **In Docker, `/app/data` is a volume**: it masks `data/raw_debates`. The container inspector only sees mounted volumes and looks "empty" while the local machine has hundreds of thousands of events. Explicitly distinguish local and container figures in every report.
- **`docker compose up` is refused in foreground** by the "long-lived server" guard: to apply a new image, run `docker stop/rm` then `docker compose create dashboard` then `docker start`, and then check `docker inspect … {{.State.Health.Status}}`.

## Docker: run directory permissions (Errno 13)

- **Named volumes keep the owner they were created with.** A volume initialized by root stays `root:root` after every image rebuild; the app runs as `uid=999(app)` → the worker crashes when creating its directory with `[Errno 13] Permission denied: '/app/debate_lab_runs/debatelab_<id>'` (`error_type: worker_crash`), on every attempt and with a new id each time. Always compare a healthy volume to a faulty one: `docker exec <c> ls -ld /app/data /app/overrides /app/debate_lab_runs /app/code_lab_runs`.
- **`chown` is impossible from the hardened container** (`cap_drop: [ALL]` + `no-new-privileges` + `read_only` → `CapEff=0000000000000000`): `chown: … Operation not permitted` even with `-u root`. Repair from a throwaway container with default capabilities, then make the fix durable with a root init service — without weakening the dashboard's profile.
- **An `if [ "$(id -u)" = "0" ]` in the entrypoint is dead code** when the image declares `USER app`: check every privilege guard against `docker inspect <c> --format '{{.Config.User}}'`, otherwise it never runs and the failure stays invisible for weeks.
- **`status: running` proves nothing**: count the `turns` rows in `/app/debate_lab_runs/<run>/debate.db` via `docker exec` to prove a debate actually produces (20 turns ≈ 10–15 min with a local 27B).
- **`:1234` answering "An LM Studio API token is required" is not down**: that is a 401, the server is running. From the container the base is `http://host.docker.internal:1234/v1` and the key lives in `/app/overrides/llm.env` (`LIFE_MEAN_LLM_API_KEY`). Reserve "offline" for a real `Connection refused`.
- **`docker compose up -d` recreates the dashboard and kills any running run**; to validate a new init service without interrupting, `docker compose config -q` then `docker compose run --rm <service-init>`.

Full recipes (A/B probe, repair one-liner, `volumes-init` service, SQLite check, LLM key test): `references/docker-run-volumes.md`.

## Studio that "does nothing" at launch (2026-10-31)

- **Symptom**: `start_studio.bat` prints its 3 `[INFO]` lines then nothing — no window, no visible process, no error message. **It is not the .bat**: the window hangs inside the `LifeMeanStudioApp` constructor, before `app.exec()`.
- **Diagnosis**: `faulthandler.dump_traceback_later(8, repeat=True)` in a wrapper script that runs `runpy.run_module("life_mean_studio", run_name="__main__")`. An external timeout says nothing; the stack dump says exactly where it hangs.
- **Cause found**: `feature_pool/analyzer.py::_find_tests` did `Path.rglob("test_*.py")` **per feature** (187 features) while reading every file. `rglob` descends into `.venv`/`node_modules` before any filter → ~2600 `test_*.py`, ~minutes to infinity. The `_is_excluded` filter applied after the walk, so it was useless.
- **Fix**: an index built **once** with `os.walk` pruning excluded directories (`dirnames[:] = [...]`), contents read once and cached at class level. `analyze_all` goes from >10 min to 0.75 s.
- **Rule**: any analysis started from a Qt page constructor must be either indexed/cached or deferred (`QTimer.singleShot(0, ...)`) so the window paints first. The network probes in `health.py` (3 s timeout, and the Docker dashboard port *accepts a connection without ever answering*) go through a `threading.Thread` + `Signal(object)` — otherwise the window appears but stays frozen for several seconds.
- **Verification**: `QT_QPA_PLATFORM=offscreen` + `QTimer.singleShot(15000, check)` that prints `fp_table.rowCount()` (must equal the number of discovered features: **989** since discovery was widened, 187 before) and `service_table.rowCount()` (4). The .bat is validated by checking `netstat -ano | grep :3000` **and** the presence of a visible window via `EnumWindows` (title `Life_mean Studio`).
- **`.bat`**: `cmd /c "cd /d \"%ROOT%path\" && npm start"` does not work — cmd has no `\"` escaping. Use `start "Titre" /D "%ROOT%hermes-orchestrator" cmd /c "npm start"`. Always write `.bat` files in CRLF and read `%ERRORLEVEL%` right after `python -m ...` to display the error instead of closing the window.

Detailed mechanics of incremental ingestion (absolute offsets, cap, `truncated` flag, deduplication): see `references/incremental-ingestion-offsets.md`.

## Feature Pool: coverage is not the inventory (2026-11-01)

- **`feature_pool` does not see all the code, and its silence is not proof.** `scanner.py::_build_scan_paths` contains a **hard-coded list of directories** (core, experiments, life_mean_studio, captn_runtime, philosophical_council, debate_lab, code_lab, autopilot, hermes-debate, historical, experimental, life_mean_lab, library, compare, analysis): `pipeline_inspector`, `feature_pool`, `data`, `life_mean_extensions`, `hermes_cronjob_manager` are absent from it. Then `_classify_feature` keeps only classes whose name contains a keyword (router, provider, safety, sentinel, debate, validator…) or a suffix (engine, controller, manager, worker, agent). Measured: **187 features for 1817 classes (10.3 %)**; 42 security/permission classes invisible, including `PolicyGuard`, `ResourceGuard`, `ExperimentExecutionGate`. Practical conclusion: **never conclude "this capability does not exist" from 0 pool hits** — check with `grep`/`ast` in the code.
- **Widening applied (procedure and control figures).** `_build_scan_paths` now discovers every top-level package except a denylist; `_classify_feature` falls back to a path-based classification (`PATH_KEYWORDS`), then `TOOLS`. Measured result: **989 features** (1280 classes − 70 private/test − 221 merges by name), **0 BROKEN**, `PolicyGuard`/`ResourceGuard`/`ExperimentExecutionGate` present, Studio built in 0.13 s with the table at 989 rows, `analyze_all` 1.75 s. Full recipe and breakdown: `references/feature-pool-discovery.md`.
- **The denylist must name the generated workspaces, otherwise they get indexed.** First attempt without `code_lab_runs/`: **1943 files scanned** instead of 839, 1004 features including copies of runs. Always count the files retained by `_build_scan_paths()` **before** validating a discovery change; a runs directory can contain more `.py` files than all the produced code.
- **Never calibrate an acceptance threshold on a naive class count.** The "1439 expected features" threshold (1817 classes − 378 from `tests/`) was wrong: `_register_feature` merges homonyms and private classes are ignored. The metric that holds is **100 % of non-private class names indexed** (1055 distinct names → 1055 indexed, 221 of them multi-location), not a raw feature count.
- **VALIDATED ≠ validated**: the evidence is a **substring** search for the feature name in the test file (`analyzer._find_tests`) — a test from `legacy/`, `historical/` or `hermes-debate/` is enough. Before widening: 138 VALIDATED of which **27** had a foreign project as their only evidence; after widening: **632 VALIDATED including 129** in that case (20.4 %). The widening does not worsen the proportion but **multiplies the absolute number**: fix `_find_tests` (require a module import or a `module.Symbol` reference) before presenting these statuses as decision-making, or leave the features as `READY` with `coverage_gaps=["test_evidence_unverified"]`.
- **Pool conflicts are a Cartesian product**: 8190 = 70 legacy × 117 modern, 0 high/medium. `orphans: 187` = the dependency graph links nothing. Do not rely on `ready_for_integration` before repairing `dependencies`.

## The Pipeline Inspector ↔ Feature Pool bridge already exists

`pipeline_inspector/feature_pool_bridge.py` reads the most recent report by mtime, normalizes the names (`MathValidationWorker` ≈ `math_validation_worker`) and **separates observed usage from validation status**. Do not write a new explorer: fix the discovery coverage and add the Studio page (no `pipeline_inspector` page in `life_mean_studio/launcher/app.py`).

## "Permission error": classify the literal before theorizing

- **Three families, never interchangeable.** `[Errno 13] Permission denied` / `EACCES` = **filesystem** permission (a path under `/app/...` means the container); `401 Authorization header required` = Node authentication layer; `403 Forbidden: CSRF token missing` = dashboard CSRF. When the user says "I got a permission error", they most often mean the first one: **get the screenshot or the exact message before building a theory**, otherwise you repair a system the error never touched (a complete theory of the 401 was built while the real message was an `Errno 13`).
- **An option offered in a form is not evidence**: if the user selects one option among candidate error messages, re-read it against the actual screenshot — and flag the discrepancy instead of following the wrong lead.

## Orchestrator & permissions: two systems, neither wired to clients

- **Two independent layers.** Python: `core/safety/policy_guard.py` (179 l., tested) is called on **one** operation only (`start_debate`, `core/debate/engine.py`), and `core/debate/experiment_gate.py::_check_safety_guards` only checks numeric bounds ("In a real system, this would check PolicyGuard, ResourceGuard"). Node: HMAC + Security Gate on every route except `/health`. Never describe "the permission system" in the singular.
- **The 401 is structural, not an incident**: no route issues a token and no Life_mean client sends one → `Authorization header required` on every call to `:3000`. Route matrix, HMAC format (iat/exp in **milliseconds**) and local token forging: `references/orchestrator-permissions.md`.
- **Approve ≠ execute**: a `/codelab` task in `APPROVAL` mode is accepted (202), approved (200 `approved:true`) then blocked `blocked_isolation_required`. As long as this refusal exists, do not present Code Lab through the orchestrator as functional, and do not propose to "wire" the dashboard to it before the isolation is handled.
- **The `:8080` dashboard does not talk to the orchestrator**: zero outgoing HTTP call in `experiments/dashboard.py`, no `/api/orchestrator/*` route, and `:3000` only listens on loopback. A 401 "seen in the dashboard" therefore comes from `:3000` called directly.
- **A unique literal in the repository identifies the emitter**: before looking for the cause of an error message, `grep -rln "<exact message>"`. If it exists in only one component, the others are innocent by construction — that avoids debugging the wrong service.

## Self-extension registries (P5) — four traps inside a "total: 0"

- **An empty registry can hide 60 real tools.** `library/tools` provides 60 deterministic tools used on every run by `ToolWorker`; the extension registry saw none of them. Any list response must separate `catalog` (what exists, `in_registry: false`) from `all`/`stats` (what is approved) — discovering is not enabling, and writing it into the payload avoids passing an absence of approval for an absence of capability.
- **An API success without storage is a delayed lie.** The registries lived in memory: `POST /api/extensions/tools` returned `proposed` then everything vanished on restart. Persist (`data/extensions/registries.json`, atomic write + `.bak`, reloaded when the layer is created) and answer `500 persistence_failed` ("applied in memory but NOT persisted") when the write fails.
- **`do_PUT` only routed `/api/settings`** and `_ID_RE` (`/(skills|tools)/([^/]+)$`) did not accept the action suffix: `/approve`, `/activate`, `/disable` returned **404 on both POST and PUT**. Any "human approval gate" is validated with a real `PUT` on the documented URL, not by re-reading the mixin.
- **An `OSError` escaping a handler does not produce a 500: it cuts the connection** (`RemoteDisconnected` on the client side). The sandbox for generated tools lived in the read-only image (`/app/sandbox`) → `EROFS` on every proposal. Move it under `data/sandbox/` (volume) and wrap the creation in `try/except` → `500 proposal_failed`. And proposals without `need_id` must derive their id from a hash of the description, otherwise they all share `tool-generated-tool` and overwrite each other's version.
- **A test that proposes a tool writes into the repository if it does not redirect its sandbox.** The default path lives under `data/`: any fixture calling `POST /api/extensions/tools` must set `LIFE_MEAN_SANDBOX_DIR` (and `LIFE_MEAN_EXTENSIONS_DIR`) to `tmp_path`, otherwise `git status` gets dirty with `sandbox/tools/tool-*` and one test's proposals pollute the next ones.

## Persisted observability: do not announce a section that is always empty (P6)

- **A declared capability that is never called is a schema lie.** Before presenting a payload section as evidence, look for its emitter: `grep -rn "record_transition\|record_rule_application\|update_progress" --include=*.py . | grep -v observability`. With no caller, only two outcomes: wire the source, or declare the absence in the payload (`traces_absent_reason`) — never a field that is always empty and passes for a measurement. Wiring goes through an **optional sink** (`runner.trace_sink = callable`) that only emits, with a `try/except` on the consumer side: a trace must never make a task fail. Then verify on a real run (`traces: 6` for 3 tasks, `tasks_completed: 3`), not by re-reading the schema.
- **Persist observability with its bounds, in the same file as the state.** The run summary (`data/experiments/runs/<id>.json`) carries `observability: {agents, events, traces, totals, truncated, limits}`; the caps come from env (`LIFE_MEAN_PERSIST_EVENTS`, `LIFE_MEAN_PERSIST_TRACES`) so they are testable. An observability snapshot must never fail a completed run: `try/except` + log, like the summary write.
- **A test that asserted the old limitation must be rewritten, not worked around.** `test_run_durability` checked `events == []` (true when nothing was persisted). When the contract changes, update the assertion **and** write in the test docstring that it replaces the former limitation — otherwise the next reader takes the old behaviour as the reference.

## "Blocked by a dependency": first check that the code exists

- **Before accepting a `BLOCKED_EXTERNAL`, run two greps**: the dependency name AND the feature name. Here `psutil`/`win32evtlog` were absent **and** no Defender/Event Log collector existed in the repository: the real status was "not written", not "blocked". A missing dependency only blocks code that calls it.
- **Windows already provides a lot without pip**: `powershell -NoProfile -Command "Get-MpComputerStatus | ConvertTo-Json -Compress"` gives the real Defender state, `wevtutil qe <journal> /c:N /rd:true /f:xml` gives the events (the `json` format does not exist, `text` is not parsable — parse the XML with `xml.etree` after wrapping the output in a root).
- **A collector must say it cannot**: on a Linux/WSL2 container, `platform.system()` is `Linux` → return `ok:false, error:"not a Windows host"` and `degraded: [...]`, never an invented plausible state.
- **Test against the real machine** for these collectors (they are environment facts), with `skipif(not is_windows())`, and test the error cases everywhere (missing binary, timeout, unknown journal).

## Math tools: parse the expression, never scan the digits

- **`re.findall(r"\d+", description)` manufactures false answers.** `sqrt(-1)` returned `1.0` (sign lost) and a decimal became its truncation. For any expression, parse a closed grammar (`nom(args)`, `a^b` on literals + `pi`/`e`), never `eval`, never digit scanning.
- **An error dict must not be able to become an answer.** `ln(0)` returned `{'valid': False, 'error': 'value>0'}` as `answer` because extraction fell back to `answer = raw_answer`. Check `valid is False` **before** extraction, not after.
- **A tool refusal is a verdict, not "no answer".** Distinguish `UNSUPPORTED_MATH_OPERATION` (we do not know how to do it) from `MATH_DOMAIN_ERROR` (the tool rejects the input); both keep the expression and the reason.
- **`tan` of an angle where cos = 0: `tan: None` + `tan_undefined`.** Rejecting the whole call made `sin(90°)`, perfectly computable, impossible; returning `"inf"` or `1.6e16` invents a value.
- **Pass `tool_name` to the worker.** `ToolWorker` re-detects when `tool_name` is absent: an expression without a keyword (`2^8`) answered "no tool" and the runner returned `None` without error.
- **Explicit units and bases, never guessed.** `angle_deg` and `angle_rad` are two distinct inputs; a log base is always passed (`ln`/`log` = e, `log10` = 10).

## Tabs and host telemetry

- **A flex tab bar without `flex-wrap` hides the last tabs.** They stay in the DOM (`visible: true`, non-zero width) but leave the viewport: present, invisible, not clickable. Check `scrollWidth > clientWidth` or the number of rows (`new Set([...children].map(b => round(top)))`), not just `offsetParent`.
- **A Linux container cannot read the Windows host**: explicit bridge (host agent + client that never raises). The client must validate the payload (expected sections) and return a reason, otherwise a partial response passes for valid. Without an agent, `degraded: [host_agent]` + the URL attempted + the command to run.
- **A collector never executed is not a verified collector.** `os_collectors` does without `psutil`/`win32evtlog` (`powershell Get-MpComputerStatus`, `wevtutil`) — the proof is made on the host, not in the Linux container where `supported` is `false`.

## Wiring a tool is not supporting it

- **A tool without a generator is dead.** Verify the full chain: the generator emits the task, the ground truth comes from the same tool, the run resolves it, validation declares it good. Measure coverage per family (description counter) — otherwise you believe you support 9 operations and 2 are produced.
- **Ground truth = tool output.** Recomputing the answer with a parallel formula (same `math.log`, same convention) recreates the divergence you are trying to eliminate: call the tool.
- **The default `reasoning_type` must not be overwritten.** `"calculation"` is the default value: routing it to a subtype (`sin`/`cos`/`tan`) turns all math tasks into trigonometry (measured: 300 tasks, 3 families).
- **Only generate defined domains:** `tan` angles outside 90° + k·180°, `log` on > 1, `sqrt` ≥ 0. A generated task outside the domain guarantees a noisy deterministic failure.
- **`/manifest` must carry the verdict, not just the counter.** `tasks_completed` without `tasks_valid`/`pass_rate` forces cross-referencing three sources; and `pass_rate` must be `None` (not 0) as long as nothing is validated.
- **Aggregate errors by machine code** (`MATH_DOMAIN_ERROR×3`) rather than as a raw list: that is the information that says what to fix.

## Runtime usage journal: observe execution, not logs

- **A log usage counter measures ingestion, not execution.** Depending on files already ingested makes the figure dependent on what the log pipeline kept (and on the retention policy). Writing an append-only execution journal (`data/usage/feature_usage.jsonl`, one line per component actually executed, with `experiment_id`/`task_id`) makes the evidence independent.
- **Emit where the decision is taken.** First version: all five tools of the router family were journaled while only one ran (×5 inflation). The right emission point is the line where `detect_tool()` answered.
- **A silent persona does not count.** In a debate, the usage line must be emitted per turn **with content** (the repetition guard can produce empty turns); counting registered agents measures the cast, not the execution.
- **`ok=None` = "executed, verdict elsewhere".** Never write an invented boolean; the verdict comes from the `ValidationRule` traces.
- **Match by substring: "unique" rather than "long".** A rule "≥ 6 characters on both sides" fixes the false positive (`math_gcd` → feature "C") but blocks a legitimate short name (`Stoic` did not find `StoicAgent`). The rule that holds: candidate ≥ 4 characters **and only one possible candidate** (ambiguity ⇒ no match). Verify with named cases: `Nihilist→NihilistAgent`, `Stoic→StoicAgent`, `math_gcd→none`.
- **Length guard on both sides in a substring matcher.** `candidate_key in key` without a guard on `candidate_key` makes a feature named "C" (or any acronym) absorb `math_gcd` — measured: 14 observed features of which 1 false positive, 13 after the fix. A usage counter is only credible if name matching is verified on short cases.

## Git on this repository

- **No backtick in `git commit -m "..."` via bash**: the shell performs the substitution (`answer: command not found`) and the word disappears from the message. Write the message to a file and use `git commit -F` / `--amend -F`.

## "2 features observed out of 989": the recent window is not a sample

- **An analysis that reads "the last N events per type" measures the last producer, not the pipeline.** Out of 837 k local events, the recent window (5 005 lines) was 100 % `captn_experiences`: the 815 k `raw_debates` events carrying `tool_worker`/`math_validation_worker`/`router` were never read, hence "2 observed" instead of 14.
- **Sample by population**: `EventStore.distinct_values(column)` (column in an **allowlist** — an API value never becomes an SQL column name) then an identical quota per group (agent, then source). Measured cost: 4.4 s on 1.1 M events.
- **Every sample counter must publish its coverage** (`coverage: {strategy, groups_sampled, per_group_limit, events_sampled, events_in_sampled_populations, truncated}`); otherwise "14" reads as a total.
- **Local ≠ container figures, and that is legitimate**: the container database has only 18 k events (`text_log` + `captn_experiences`) because `/app/data` is a volume that masks `data/raw_debates`. Always give both sets and name the cause.
- **Low coverage is not always a bug**: 987 unobserved features out of 989 correspond to classes (Qt widgets, stores) that these pipelines never instantiate. Saying so is better than forcing a figure.

## A 403 returned before reading the body = connection aborted on Windows

- **Symptom**: a CSRF test fails ~1 time out of 12 with `ConnectionAbortedError: [WinError 10053]`, never reproducibly on demand. The client receives no response while the server did send the 403.
- **Cause**: `do_POST`/`do_PUT`/`do_DELETE` rejected before `self.rfile.read(Content-Length)`. Windows resets a closed socket with unread data; depending on when the client finishes writing, the response is lost.
- **Fix**: `_drain_request_body()` (read then discard, capped at 1 MB) before **every** 403/401 response of the mutating verbs. A/B measured on 60 POST with 4 KB: 53/60 responses before, 60/60 after.
- **Rule**: any early error response (auth, CSRF, 404, quota) must drain the request body, otherwise HTTP tests become "flaky" while the bug is deterministic on the socket side.

## A "flaky" test that reads source: `inspect.getsource` lies after a rewrite

- **`inspect.getsource` describes the file as it was at import, not as it is on disk.** Rewriting a file while a process runs invalidates all recorded `co_firstlineno`; linecache re-reads the **new** file and slices it at the **old** lines → the returned function is another function. Measured on `experiments/dashboard.py`: assertion `True` before the rewrite, `False` during (the returned body was the `_training_start` error path), file restored with an identical sha256.
- **Typical symptom**: a test asserting on source text fails once in 500 executions, passes alone and in every subset, and the line quoted in the report does not look at all like the target function. It is not a concurrency flake: it is the line cache.
- **Fix**: re-read the file and find the definition **by name** with `ast` (`ast.get_source_segment`) — see `tests/source_utils.py::current_source()`; or assert the **real contract** (`inspect.signature(fn).parameters["host"].default`). Never "relax" the assertion in front of this false flake.
- **Method corollary**: never edit a `.py` file of the repository while a pytest suite is running on it — that is exactly what produced the single non-reproduced failure of a full audit.

## Verification gate before the next patch (required by the creator)

- **Imposed sequence**: `Feature Pool First` (prove a capability exists before creating one) then `Verify Before Next Patch` (no further fix as long as the previous one has no verification record).
- **Git checkpoint = controlled operation, never `git add .`**: (1) `git status` + diff summary, (2) secret scan on the candidate files (`sk-`/`gho_`/`AKIA` keys, PEM blocks, `password=`), (3) **explicit** file list in `git add -- …`, (4) exclusion of generated artifacts (report exports, `dashboard_debug.html`, `_*.py`, state `spec.json`, execution `*.jsonl`), (5) `git diff --cached --numstat` to check for the absence of binaries, (6) commit message that **cites the numerical test baseline**. The large excluded artifacts stay on disk with their `sha256` recorded in a versioned `MANIFEST.txt`.
- **A triggered stop criterion stops the work even if it is badly calibrated.** Note the trigger, explain the numerical breakdown, then hand the decision back to the creator (keep / relax / `git checkout --`). Never silently rewrite your own threshold so you can continue.
- **Count the files the scanner retains before concluding on a discovery change**, and verify that no feature disappears without being named (`FakeController` = test fixture, correct disappearance).
- **"It works" requires distinguishing real from simulated.** Green tests and an HTTP 200 prove nothing if the handler is a stub: look for "In production, this would…" comments, canonical responses (`Response based on <school> perspective:`), and placeholder credentials (abnormal length: 15 characters for a Cloudflare account). An audit ends with an explicit section **"what could not be verified"** (LLM backend down, execution blocked) — never with a global claim that everything works.

## Durability, reproducibility & artifact honesty

- **A Docker image that `COPY`s the code has no bind mount: rebuild required before any verification.** Otherwise the container serves the old revision and recent routes return 404. Check `docker images life-mean-dashboard:local --format "created={{.CreatedSince}}"` **and** `docker ps` (`Up … (healthy)`) before concluding; a `docker compose up -d` without `build` is a test of the previous image.
- **Durability is proven by a restart, not by a test.** A test on `tmp_path` validates the code, not the volume + rehydration wiring: create a run via the API, `docker compose restart dashboard`, then re-read `GET /api/experiments` (run present, `rehydrated: true`, final status) and `GET /api/experiments/{id}/manifest` (200).
- **A rehydrated manifest carries what was persisted, and declares what never existed.** The run summary now contains an `observability` block (agents, events ≤ 500, traces ≤ 200) plus `totals`/`truncated`/`limits`; after a restart the manifest and `/observability` serve the same shape as a live tracker with `rehydrated: true` and a note quantifying the restored data ("2 of 2 events, 0 of 0 traces"). An empty list without explanation is a defect: if the build does not produce a datum, the payload carries `traces_absent_reason` — never an empty array that suggests a lost file.
- **A pipeline fix is proven by A/B on the same seed.** Replay exactly the same seed before/after and compare the artifacts: `pass_rate` (0.333 → 1.0 here) then the RAW rows (`answer`, `ground_truth`, `valid`, `error`). A different run proves nothing.
- **An unserved task must fail explicitly, never answer `None`.** `answer=None` conflates "no tool covers this task" and "wrong answer". Raise an error carrying a code (`UNSUPPORTED_TASK` / `NO_ANSWER`) and make it land in the serialized result, hence in the RAW.
- **Detection must cover every family the generator produces.** Any family added to the generator requires a pattern in `detect_tool` **and** a `DOMAIN_MAP` entry; verify with `detect_tool("<real example>")` for each family before declaring coverage, otherwise the task goes to a silent `None`.
- **The generator's ground truth takes precedence over the tool's default.** Read how the generator computes `ground_truth` before wiring a tool: `log(28)` means `math.log` (natural, 3.332205), a `log10` default gave 1.447 with no visible error. Pass the base/units explicitly rather than relying on a default.
- **The README is a surface of claims: every counter and every endpoint is verified before publication.** `grep` the route in the handler, `curl` the live API, count the real objects. A stale README announced 713 tests, a non-existent `/api/experiments/{id}/raw` endpoint and "22 tools" for 60.

Full recipes (creating a run via the API with CSRF, check after restart, manifest fields, same-seed A/B, audit of README claims): `references/durability-reproducibility.md`.

## Packaging: editing `pyproject.toml` is not enough

- The editable finder (PEP 660, `__editable__*.pth` + `__editable___*_finder.py`) is **generated at install time**: adding patterns to `packages.find.include` does not make the packages importable. After editing, replay `pip install -e . --no-deps --no-build-isolation`, then verify the import **from another cwd** (`cd "$LOCALAPPDATA/Temp" && python -c "import feature_pool, life_mean_studio"`). `--no-deps` avoids moving the environment.

## Repository test baseline (2026-11-01, re-verify before concluding)

`pytest tests -q` → **1797 passed, 13 skipped, 0 failed, ~360 s** (last reading; `tests/` + `pipeline_inspector/tests` make ~1806. The blocks below describe the historical state to understand the regressions already fixed). Verify the real count before citing a figure in a commit or a README. Historical baseline groups: 5 `test_autopilot_llm_adapter` (LM Studio down, they fail instead of `skip`), 16 `test_workspace_ui` (`experiments/ui/workspace.{html,css,js}` absent), 4 `test_error_memory` (`code_lab/error_memory.py` empty), 1 `test_phase7_weakness` (`KeyError: 'domain'`), 1 `test_qa_fixes` (DELETE 403 vs 200: CSRF mandatory), 1 `test_dashboard_ui` (`el` alias gone from dashboard.html), 1 `test_code_lab_visibility`. Tests per package: studio 110, sentinel 31, pipeline_inspector 27, feature_pool 9 (13 since the 4 discovery tests were added). **Three independent runs gave the same counts** (434.17 s / 439.30 s / 437.03 s): this is a reproducible baseline, not a snapshot. The 5 `test_autopilot_llm_adapter` failures are **environmental** (local LLM unreachable from the test) and should `skip` instead of failing; do not conclude "LM Studio down" from them — it may be running and requiring a token (`An LM Studio API token is required`), which is a 401 and not a stopped server.

## Test commands reference
```bash
cd /c/Users/celes/Documents/Hermes-Workspace/Life_mean
uv run pytest tests/test_sentinel.py -v
uv run pytest tests/test_turn_model_provenance.py -v
uv run pytest -q
```
