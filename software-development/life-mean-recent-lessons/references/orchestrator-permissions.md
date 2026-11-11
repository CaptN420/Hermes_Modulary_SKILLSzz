# Hermes orchestrator — HTTP surface, authentication, Security Gate

Map verified by real execution (HTTP requests + reading the compiled code). Used to diagnose
a permission refusal without guessing, and to avoid promising a capability that does not exist.

## What is listening

- `hermes-orchestrator` (Node): `node dist/index.js`, port **3000**, bound to **127.0.0.1** only.
  Consequence: a containerised dashboard cannot reach it — that would require a non-loopback bind
  *and* `host.docker.internal`. Never assume that "it should be able to connect".
- Public route: `GET /health` only.
- Protected routes: `POST /inference` (RUNNER+), `GET /models`, `POST /models/:id/load|unload` (ADMIN),
  and every `/codelab/*`.
- Hierarchy `OBSERVER < RUNNER < ADMIN`. Role too low →
  `403 {"error":"Insufficient permissions. Required: ADMIN"}` (correct behaviour).

## Authentication

- Token format: `<base64url(payload JSON)>.<hex hmac_sha256(secret, base64url)>`.
- Payload: `{sub, role, iat, exp, jti}`; `iat`/`exp` are compared against `Date.now()` so they are **in milliseconds**.
  Clock margin accepted on `iat`: 5 min. Valid roles: `OBSERVER`, `RUNNER`, `ADMIN`.
- Secret: `AUTH_SECRET` (≥ 32 characters) otherwise the `.auth-secret` file in the server's cwd
  (git-ignored, 64 hex, generated on the first authenticated call). Without a secret: fail-closed, everything is rejected.
- **No route issues a token.** Any caller without a token receives
  `401 {"error":"Authorization header required"}`; invalid token → `401 {"error":"Invalid or expired token"}`.

### Forge a token locally (audit only)

Read the `.auth-secret` file, sign the payload, and **never** display or log the secret
or the token produced. Then check that an insufficient role does return 403 (proof that auth works).

```python
import base64, hashlib, hmac, json, time, uuid
from pathlib import Path
secret = Path("hermes-orchestrator/.auth-secret").read_text().strip().encode()
now = int(time.time() * 1000)
payload = {"sub": "audit", "role": "ADMIN", "iat": now, "exp": now + 3_600_000, "jti": uuid.uuid4().hex}
body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
token = body + "." + hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
```

## `/codelab` — accepted values and decisions

- `origin` ∈ `dashboard | api | hermes | rpc` (any other value → 400).
- `mode` ∈ `AUDIT | DEV | APPROVAL` (`AUTO` → 400).
- `APPROVAL`: `202 {"message":"Task registered, awaiting Security Gate approval"}` then
  `POST /codelab/approve/:id` → `200 {"approved":true,"execution":"blocked_isolation_required"}`.
  Final status: `blocked_isolation_required` with
  `errors: ["ISOLATION_REQUIRED: security gate provides no effective isolation; refusing to execute
  arbitrary code. Set ALLOW_UNSANDBOXED_EXECUTION=1 ONLY to run with NO isolation (explicit, documented risk)."]`.
- **Approving ≠ executing.** As long as this refusal exists, the Code Lab through the orchestrator produces no diff
  and no execution: never present it as functional.
- `allowed_paths: []` is hard-coded in `codelab_adapter.ts`: the field is declared, never filled,
  never checked by the gate. The notion of "allowed paths" is decorative.

## Simulated paths (do not certify as real)

- `POST /inference` → `Response based on <school> perspective: <message>`.
  Source: `RequestQueue.generateResponse`, comment "In production, this would call the loaded model".
  The tests pass, the route returns 200, and yet no model is called.
- Routing: `CLOUDFLARE_ACCOUNT_ID` / `CLOUDFLARE_AUTH_TOKEN` of 15 characters = placeholders →
  `[Router] Using simulated routing`. A real Cloudflare account id is 32 hex, a token 40+.

## Proving where a "permission" message comes from

- **A literal present in a single component identifies the emitter.**
  `grep -rln "Authorization header required"` → only `hermes-orchestrator/src|dist`: so a 401
  "seen in the dashboard" can only come from `:3000`.
- The Python dashboard is innocent by construction: `grep -n "urlopen\|requests\.\|http://" experiments/dashboard.py`
  → **no outbound HTTP call**; unknown paths → `404 {"error": "Not found", "code": "error", "request_id": …}`,
  it never returns 401 and exposes no `/api/orchestrator/*` route.
- Reproducible CSRF refusal (dashboard side): `POST /api/experiments` without the header →
  `403 {"error":"Forbidden: CSRF token missing or mismatched","code":"csrf_failed"}`; with
  `X-Lifemean-CSRF: <value of the lifemean_csrf cookie>` → `200 {"status":"created"}`.
  The dashboard's `fetch` wrapper does set the header (`dashboard.html`, `headers.set('X-Lifemean-CSRF', token)`):
  a CSRF 403 signals a call that bypasses this wrapper, not missing wiring.

## Diagnostic corollary

Three distinct breaks produce the same "permission error" complaint:
(1) no token → 401; (2) role too low → 403 "Required: ADMIN";
(3) isolation gate → task approved but `blocked_isolation_required`.
Always identify which one before proposing a fix — the remedies have nothing in common.
