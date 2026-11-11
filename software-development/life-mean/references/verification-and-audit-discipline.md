# Verification & audit discipline (Life_mean / Life-Mean-Labs)

Rules for proving a claim about this repo. Every one of them exists because a
cheaper method produced a confident wrong answer.

## 0. Where the work lives

Active repo: `C:/Users/celes/Documents/Hermes-Workspace/Life_mean_realm` (GitHub
`CaptN420/Life-Mean-Labs`); the older `Life_mean` tree is legacy. Docker service
`life_mean_realm-dashboard-1` on `127.0.0.1:8080` (fallback host run on 8082,
since 8080 can be taken by another container).

## 1. Probe from inside the environment that runs the app

`LIFE_MEAN_LLM_BASE_URL` is typically `http://host.docker.internal:1234/v1`.
That name resolves **only inside the container**, and the API key arrives through
`env_file: .env`. A probe from the host shell therefore fails twice — unresolvable
host in bash, and no `Authorization` header — and returns `HTTP 000` or `401`.

```bash
docker exec life_mean_realm-dashboard-1 sh -c 'cd /app && python - <<EOF
import os, urllib.request
base = os.environ["LIFE_MEAN_LLM_BASE_URL"].rstrip("/")
key  = os.environ.get("LIFE_MEAN_LLM_API_KEY", "")
req  = urllib.request.Request(base + "/models", headers={"Authorization": "Bearer " + key})
print(urllib.request.urlopen(req, timeout=10).status)
EOF'
```

Never write "provider broken" from a host-side probe. A 401 from outside says
nothing about the app path.

## 2. Prove the container serves the current commit

The image `COPY`s the source (no bind mount). After any code change the running
container keeps the old revision until `docker compose build dashboard && up -d`,
and every end-to-end test silently measures yesterday's code.

```bash
docker exec life_mean_realm-dashboard-1 sh -c 'grep -c "<symbol added by the latest commit>" /app/<path>.py'
# 0  -> stale image, rebuild before testing anything
```

Pick a symbol that only exists in the newest commit; `grep -c` of an old symbol
proves nothing.

## 3. A `404` on GET is not a missing route

Several routes are POST-only (`/api/pipeline/reports`, `/api/pipeline/export`).
Before declaring an endpoint absent, look at `do_POST` in
`experiments/dashboard.py` and retry with the CSRF pair:

```
GET /api/pipeline/reports  -> 404
POST /api/pipeline/reports -> 200
```

State-changing calls need the `lifemean_csrf` cookie plus the
`X-Lifemean-CSRF` header, both issued by `GET /dashboard`.

## 4. Literal-grep of the frontend under-counts endpoints

The UI builds URLs by concatenation (`const PI_BASE = '/api/pipeline'`, then
`PI_BASE + '/stats'`). Grepping for `"/api/pipeline/<name>"` returns zero hits
while the UI is fully wired. Grep for the base constant, then read the call sites.

## 5. Classify, don't re-fix

When auditing an existing project, tag every known issue before touching code,
using exactly one of: `FIXED_AND_VERIFIED`, `CONFIRMED_BROKEN`, `PARTIAL`,
`UNVERIFIED`, `BLOCKED_EXTERNAL`, `NOT_APPLICABLE`. Re-fixing a `FIXED_AND_VERIFIED`
item wastes a cycle and can regress it. A claim is only `FIXED_AND_VERIFIED` with a
reproduction (run, endpoint, test), never from "the code looks right".

When an earlier claim of your own turns out wrong, correct the report in place and
say so explicitly; do not quietly drop the paragraph.

Long reports (`CURRENT_STATE_AUDIT.md`) take targeted patches only. A "rebuild the
file from parsed lines" script silently reorders sections and drops table rows; when
that happens, restore with `git checkout -- <file>` (the last commit is the backup),
reapply the two or three real edits, then check the structure with
`grep -n '^## \|^### \|^| [0-9]'` before committing.

## 6. Separate simulation from execution

- `core/workers/task_scheduler` is a **virtual-clock simulator**: durations are
  abstract units, no threads, no asyncio. Its totals are not measured wall time.
- `continue_experiment` now resumes for real (per-task checkpoint + content
  fingerprint); it refuses an absent, finished or config-mismatched run instead of
  restarting. Re-verify instead of trusting either the old docstring or this line —
  recipe in `references/experiment-resume-and-checkpoints.md`.
- `torch`, `llama_cpp`, `transformers`, `onnxruntime` are not installed: only
  `CPU_ONLY` + `REMOTE_PROVIDER` profiles are exercisable. Never report GPU numbers.
- `psutil`, `win32evtlog`, `win32service` are not installed: OS collectors are
  `UNAVAILABLE`, not "in progress".

Capabilities named in a spec but absent from the code (skills registry content,
evolve, experiment emulation, telemetry module) get reported `PLANNED`/empty.
Their HTTP route existing and returning `total: 0` is not evidence they work.

## 7. `.lmpack` has two layouts; both are supported

| Layout | Where | Reader |
|---|---|---|
| `personas/personas.json` + `providers/` + `models/` | written by `core/packager` | canonical |
| `manifest.json` + `agents/<id>.json` + optional `README.txt` | written by Studio, used by every pack in `lmpack/` | fallback |

Agent entry keys: `id`, `name`, `persona`, `role`, `provider`, `system_prompt`,
`config`. `persona: "general"` has no `PersonaType` member — it maps to `OTHER`
and the raw value is kept in `metadata["raw_persona_type"]`. An unrecognised
archive must raise `PackageFormatError`; a pack that loads as "zero personas"
produces a misleading "pack without personas" at validation time.

## 8. Git and authorization

Large correction mandates can require **local commits only** — no `git push`
without explicit authorization. The untracked tree usually carries probe scripts
(`_*.py`), `feature_pool_*.json`, `artifacts/` and a growing
`captn_runtime/captn_experiences.jsonl`; those are runtime noise, never commit
them as part of a fix.
