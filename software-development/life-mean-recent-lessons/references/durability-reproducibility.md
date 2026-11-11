# Durability, reproducibility & artefact honesty

Recipes verified by execution against the Life_mean_realm Docker dashboard
(`127.0.0.1:8080`). Each block served to produce real proof, not a code
re-read.

## 1. Create and start a run through the API (CSRF mandatory)

The cookie and the CSRF header come from `GET /dashboard`; a POST without
`X-Lifemean-CSRF` returns 403 (see the double-submit rule in SKILL.md).

```python
import urllib.request, urllib.parse, re, json
BASE = "http://127.0.0.1:8080"

with urllib.request.urlopen(BASE + "/dashboard", timeout=90) as r:
    cookie_header = r.headers.get("Set-Cookie", "")
m = re.search(r"lifemean_csrf=([^;]+)", cookie_header)
token = urllib.parse.unquote(m.group(1))
cookie = "lifemean_csrf=" + m.group(1)

def call(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    req.add_header("Cookie", cookie)
    if method != "GET":
        req.add_header("X-Lifemean-CSRF", token)
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.status, resp.read().decode()

status, body = call("/api/experiments", "POST", {
    "prompt": "Compute GCD of two integers", "num_tasks": 3, "seed": 21,
    "deterministic": True, "domain": "math", "difficulty_range": [1, 2],
    "mode": "deterministic",
})
exp = json.loads(body)["experiment_id"]
call(f"/api/experiments/{exp}/start", "POST", {})
```

## 2. Prove durability by a restart

```bash
docker compose restart dashboard && sleep 12
docker ps --format "{{.Names}} {{.Status}}"     # Up … (healthy)
```

Then read the state back — **that** is the proof, not the unit test:

```python
status, body = call("/api/experiments")
d = json.loads(body)
run = d["experiments"][exp]
assert run["status"] == "COMPLETED" and run["rehydrated"] is True
status, body = call(f"/api/experiments/{exp}/manifest")
manifest = json.loads(body)
assert manifest["rehydrated"] is True and manifest["config"]["seed"] == 21
```

A rehydrated run stays `COMPLETED` (never `running`) and its manifest carries
`rehydrated: true`, `restored_totals: {events, traces, agents}`, `truncated:` and
`traces_absent_reason` when the build produces no traces.

`POST /api/experiments` **creates** the run (`status: created`): you must then
`POST /api/experiments/{id}/start`. A "finished" run with `tasks_completed: 0`
seen right after creation comes from that, not from the engine.

## 2bis. Probe persisted observability (before / after restart)

```python
# 1. start, wait for the end
call(f"/api/experiments/{exp}/start", "POST", {})
for _ in range(120):
    time.sleep(1)
    _, body = call(f"/api/experiments/{exp}/manifest")
    m = json.loads(body)
    if not (m.get("progress") or {}).get("is_running") and not m.get("rehydrated"):
        break
print(len(m["events"]), len(m["traces"]), m.get("traces_absent_reason"))
```

```bash
# 2. the run file holds the bounded block
docker exec life_mean_realm-dashboard-1 sh -c 'python - <<EOF'
import json
d = json.load(open("/app/data/experiments/runs/<exp>.json"))
o = d["observability"]
print(len(o["events"]), len(o["traces"]), len(o["agents"]), o["totals"], o["truncated"], o["limits"])
EOF

# 3. restart then read back: it is the only proof of rehydration
docker compose restart dashboard && sleep 14
```

Expected after restart: `rehydrated: true`, the same `events` as before
(`experiment_started` / `experiment_completed`), `agents: {agent_1..3}`,
`progress.status: COMPLETED`, and a note of the form
`(2 of 2 events, 0 of 0 traces)`. A present `traces_absent_reason` is the
correct answer — not a bug to "fix" by inventing traces.

## 2ter. Self-extension registries: persistence is proven by restart too

```python
call("/api/extensions/tools", "POST", {"description": "Volume of a sphere"})   # -> persisted: True
call(f"/api/extensions/tools/{tool_id}/approve", "PUT", {"by": "human"})      # -> 200 approved
```

Then `docker compose restart dashboard` and `GET /api/extensions/tools`: the
entries must be there (`data/extensions/registries.json` on the volume).
Two proposals with different descriptions must produce **two** distinct ids
— an identical id means the proposals overwrite each other.

## 3. Fields expected in the reproducibility manifest

`engine{name,version}`, `environment{python,system,machine}`,
`dependencies{combined_sha256}` (pyproject + uv.lock), `git{commit,dirty}`,
`seed`, `deterministic`, `models`, `tools`, `generator_version`,
`prompt_version`, and `reproducibility_fingerprint` (stable hash of the conditions).
No secrets: versions, ids and hashes only — there is a test that traps
environment variables to prove it.

## 4. A/B on the same seed (proof of a pipeline fix)

1. Replay the **same** seed before the fix, note `pass_rate` and the faulty
   RAW rows.
2. Apply the fix, rerun the same seed.
3. Compare `pass_rate` (0.333 → 1.0 in the real case), then, line by line,
   `answer` / `ground_truth` / `valid` / `error`:

```bash
docker exec life_mean_realm-dashboard-1 sh -c 'python - <<EOF'
import json
for line in open("/app/data/raw_debates/<exp>.jsonl", encoding="utf8"):
    d = json.loads(line)
    v = d.get("validation_result") or {}
    print(d.get("answer"), "|", d.get("ground_truth"), "|", v.get("valid"), "|", d.get("error"))
EOF'
```

A different seed proves nothing: the tasks change with the seed.

## 5. Audit a README's claims before publication

Three checks that genuinely contradicted the existing README:

| Claim | Check | Verdict |
|---|---|---|
| `GET /api/experiments/{id}/raw` | `grep -n 'endswith("/raw")' experiments/dashboard.py` | **does not exist** (only code-lab has `/raw`) |
| "22 tools" | count the `*_TOOLS` dicts per family | **60** (22 math, 15 physics, 14 chemistry, 3 logic, 6 coding) |
| number of tests | `.venv/Scripts/python -m pytest tests/ -q` | 1694 passed / 13 skipped, not 713 |

Rule: no claim about a counter, an endpoint or a status goes into a
README without the command that produced it. After publication, re-read what GitHub
actually serves (`curl -s https://raw.githubusercontent.com/<owner>/<repo>/main/README.md`).
