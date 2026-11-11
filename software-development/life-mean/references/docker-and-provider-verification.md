# Verifying Life_mean against reality (Docker, providers, API, packages)

Depth for the moment when a claim about the running system must be proven rather
than inferred. Read this before telling the user a feature "works" or "is
broken".

## 1. Prove the container serves the current code

The dashboard image **bakes the source in** (`COPY . .`, no bind mount), so the
running container keeps serving an older revision until rebuilt. Rebuilding is
not optional after a code change, and it must be *verified*, not assumed:

```bash
docker compose build dashboard && docker compose up -d
# pick a symbol that exists ONLY in the new code
docker exec life_mean_realm-dashboard-1 sh -c 'grep -c MyNewSymbol /app/path/module.py'
```

`0` means the image predates the change — every end-to-end result gathered after
that point describes old code. Rebuild, re-grep, then test.

## 2. Probe providers from inside the container, never from the host

`LIFE_MEAN_LLM_BASE_URL` points at `host.docker.internal`, which only resolves
inside the container, and the API token lives in `.env` (injected through
`env_file`). A host-side `curl` therefore fails with a connection error or a
`401`, which says nothing about the app:

```bash
docker exec life_mean_realm-dashboard-1 sh -c 'python - <<EOF
import os, json, urllib.request
base = os.environ["LIFE_MEAN_LLM_BASE_URL"].rstrip("/")
key = os.environ.get("LIFE_MEAN_LLM_API_KEY", "")
req = urllib.request.Request(base + "/models",
                             headers={"Authorization": "Bearer " + key})
print(len(json.loads(urllib.request.urlopen(req, timeout=10).read())["data"]))
EOF'
```

Report a provider as unavailable only after this in-container probe fails. A
host-side 401 is a probe artifact, not a defect — and a defect claim that turns
out to be an artifact must be corrected in the report explicitly, not quietly
dropped.

## 3. Never print secret values; read key names only

`.env` files are credential-bearing and should not be echoed, attached or
committed. When you need to know what is configured:

```bash
sed -E 's/^([A-Za-z0-9_]+)=.*/\1=<redacted>/' .env | grep -v '^#' | grep -v '^$'
```

Verify presence with booleans/lengths (`bool(key)`, `len(key)`), never by
printing. Tool output can itself mask token-shaped strings, so **never judge a
secret by eyeballing a printed string** — assert `token in redacted_text` and
print the boolean instead (this is how the redaction gaps were actually found).

## 4. A 404 is not a missing route until the verb is checked

Several dashboard routes are POST-only (`/api/pipeline/reports`,
`/api/pipeline/export`, `/api/packages/validate`). A GET probe returns 404 and
looks like an absent endpoint. Before declaring a route missing:

```bash
grep -n '"/api/the/route"' experiments/dashboard.py
```

and check whether it sits in `do_GET`, `do_POST` or both. POSTs need the CSRF
pair (`lifemean_csrf` cookie + `X-Lifemean-CSRF` header) issued by
`GET /dashboard`.

## 5. "Readable" is not "valid"

Opening a `.lmpack` ZIP is not validation: a pack can open and ship zero
agents. Two independent readers exist — `life_mean_studio.engine.package_manager`
(`manifest.json` + `agents/<id>.json`, the shipped layout) and `core.packager`
(`personas/personas.json`, plus `agents/` since the compatibility fix). Report
their verdicts **side by side** with an explicit agreement flag; never average
them, and require at least one agent before calling a pack valid.

## 6. Do not dress simulation up as measurement

`core/workers/task_scheduler` runs on a **virtual clock**: no threads, no
asyncio. Its `duration` values are abstract units. Chaining, priority, failure
propagation, retries and cycle detection are real and testable; elapsed time is
not. Say "simulated ordering", never "took N seconds". Likewise the missing
pieces (timeouts, resume-after-interruption, scheduler persistence) are real
absences — document them instead of implying them.

## 7. Classify evidence, never a filename

A component counts as `OPERATIONAL` only when an import succeeds **and** a route
or handler is identified **and** a test or a real call exercised it. Otherwise
use `PARTIAL` / `PLANNED` / `UNAVAILABLE` / `BLOCKED_EXTERNAL`. Capabilities that
do not exist in the code (Skills registry, Evolve, experiment emulation,
telemetry module) must be reported as absent — inventing them is the one failure
the user will not forgive.

## 8. Flaky tests: report, never weaken

A test that fails once inside the full suite and passes alone, in its group and
on a rerun is `UNVERIFIED_FLAKE`. Record it with exactly that evidence, leave the
assertion untouched, and schedule the isolation work; do not relax `assert` to
make a run green.
