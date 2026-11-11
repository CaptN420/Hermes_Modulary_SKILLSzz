# Docker — run volumes, ownership and verification

Applies to the Docker deployment of the Life_mean dashboard (`docker-compose.yml`, `life-mean-dashboard:local`).

## 1. Typical symptom

In the CONVERSATION panel of the dashboard:

```
System  SYSTEM_ERROR
[Erreur 13] Permission denied: '/app/debate_lab_runs/debatelab_<id>'
```

The original message, on the application side, is even clearer:

```json
{"type": "RUN_FAILED", "error": "[Errno 13] Permission denied: '/app/debate_lab_runs/debatelab_006dd026d2'",
 "error_type": "worker_crash"}
```

`/app/...` ⇒ this is **inside the container**. `Errno 13` ⇒ `EACCES`, filesystem — nothing to do with authentication or with `PolicyGuard`.

## 2. Diagnostic ladder (in this order)

```bash
D=life_mean_realm-dashboard-1

# a) who runs inside it?
docker exec $D id

# b) compare a healthy volume and a faulty one
docker exec $D sh -c 'ls -ld /app/data /app/overrides /app/code_lab_runs /app/debate_lab_runs'

# c) A/B probe: same command, two volumes (no data touched)
docker exec -u app $D sh -c 'mkdir /app/data/probe && rmdir /app/data/probe && echo "data OK"; \
  mkdir /app/debate_lab_runs/debatelab_probe'

# d) why an in-container chown fails
docker inspect $D --format 'User={{.Config.User}} CapDrop={{.HostConfig.CapDrop}} ReadOnly={{.HostConfig.ReadonlyRootfs}}'
docker exec -u root $D sh -c 'grep Cap /proc/self/status'
```

Expected result on a hardened container: `uid=999(app)`, `CapDrop=[ALL]`, `CapEff=0000000000000000` → `chown` returns `Operation not permitted` **even as root**.

## 3. Immediate repair (without stopping the dashboard)

The Docker daemon itself has the capabilities: a throwaway container with default capabilities mounts the volumes and fixes the ownership.

```bash
docker run --rm --user 0 --entrypoint sh \
  -v life_mean_realm_life_mean_debate_lab_runs:/x \
  -v life_mean_realm_life_mean_code_lab_runs:/y \
  life-mean-dashboard:local -c 'chown -R 999:999 /x /y && ls -ld /x /y'
```

Volume names are read from the running container:

```bash
docker inspect $D --format '{{range .Mounts}}{{.Name}} -> {{.Destination}}{{"\n"}}{{end}}'
```

Verification: `docker exec -u app $D sh -c 'mkdir /app/debate_lab_runs/probe_ok && rmdir /app/debate_lab_runs/probe_ok'` must succeed.

## 4. Durable fix: a root init service

A named volume is initialised only once: fixing it by hand does not protect a fresh deployment. Add a service that repairs the ownership before the dashboard starts, **without** touching its hardening:

```yaml
services:
  volumes-init:
    image: life-mean-dashboard:local
    user: "0"
    entrypoint: ["sh", "-c"]
    command:
      - >-
        chown -R 999:999 /app/debate_lab_runs /app/code_lab_runs
        /app/philosophical_council/storage/raw_data;
        echo "ownership fixed"; ls -ld /app/debate_lab_runs /app/code_lab_runs
    security_opt:
      - no-new-privileges:true
    volumes:
      - life_mean_code_lab_runs:/app/code_lab_runs
      - life_mean_debate_lab_runs:/app/debate_lab_runs
      - life_mean_philosophical_council:/app/philosophical_council/storage/raw_data
    restart: "no"

  dashboard:
    depends_on:
      volumes-init:
        condition: service_completed_successfully
```

Validation **without** recreating the dashboard (hence without killing a run in progress):

```bash
docker compose config -q && docker compose run --rm volumes-init
```

`docker compose up -d` recreates the dashboard container: reserve it for a moment when no debate is running.

## 5. Entrypoint: the guard that never runs

```sh
# DEAD: the image declares USER app, so id -u is 999 and the branch is skipped
if [ "$(id -u)" = "0" ]; then chmod 777 /app/debate_lab_runs …; fi
```

Replace it with an explicit warning when a volume is not writable (`[ ! -w "$d" ]`), pointing to `docker compose up -d volumes-init`. `chmod 777` was the wrong answer anyway: what is needed is `chown` to the application uid.

## 6. Proving that a run actually produces output

The API status (`running`) is declarative. The proof is in the run database:

```bash
docker exec $D python -c "import sqlite3;\
 c=sqlite3.connect('/app/debate_lab_runs/<run_id>/debate.db');\
 print(c.execute('select count(*) from turns').fetchone()[0])"
```

Useful `turns` columns: `turn_id, round, speaker, speaker_role, moderator_question, moderator_reason, response, model, duration_seconds, finish_reason, was_truncated`. A 20-turn debate with a local ~27B model takes 10–15 min (≈10–15 s of generation per turn + moderation): probe every 20 s, not every 2 s.

The run directory (`debate.db`) only appears when the worker starts, a few seconds after `start`: an immediate `test -d` returns "absent" without that being an error.

## 7. Local LLM from the container

```bash
docker exec $D python -c "import urllib.request,json;\
 raw=open('/app/overrides/llm.env').read();\
 kv=dict(l.split('=',1) for l in raw.strip().splitlines() if '=' in l);\
 url=[v for k,v in kv.items() if 'BASE' in k][0]; key=[v for k,v in kv.items() if 'KEY' in k][0];\
 req=urllib.request.Request(url.rstrip('/')+'/models', headers={'Authorization':'Bearer '+key});\
 print(json.loads(urllib.request.urlopen(req,timeout=6).read())['data'][0]['id'])"
```

Expected: a model identifier (`kwaipilot_kat-coder-v2.5-dev`, `qwen3.5-2b`, …). Base `http://host.docker.internal:1234/v1`: `localhost` **inside** the container does not designate the host machine. Never print the key — only its length or a boolean.

## 8. Diagnostic pitfalls

- A `/app/...` message cannot come from a script launched on the host: look for the faulty binary on the container side first.
- The error may not be persisted: it was rendered live and then lost. Retrieve it through the API (`/api/debate/timeline`, `/api/debate/runs`) rather than through `grep` in the files.
- `docker exec` without `MSYS2_ARG_CONV_EXCL='*'` on git-bash rewrites the argument paths: prefix Docker commands that contain `-v`, `--format` or `/app/...` paths.
