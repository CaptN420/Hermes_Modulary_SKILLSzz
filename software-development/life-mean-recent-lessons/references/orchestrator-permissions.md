# Orchestrateur Hermes — surface HTTP, authentification, Security Gate

Carte vérifiée par exécution réelle (requêtes HTTP + lecture du code compilé). Sert à diagnostiquer
un refus de permission sans deviner, et à ne pas promettre une capacité qui n'existe pas.

## Ce qui écoute

- `hermes-orchestrator` (Node) : `node dist/index.js`, port **3000**, bindé sur **127.0.0.1** seulement.
  Conséquence : un dashboard en conteneur ne peut pas l'atteindre — il faudrait un bind non-loopback
  *et* `host.docker.internal`. Ne jamais supposer que « ça devrait se joindre ».
- Route publique : `GET /health` uniquement.
- Routes protégées : `POST /inference` (RUNNER+), `GET /models`, `POST /models/:id/load|unload` (ADMIN),
  et tout `/codelab/*`.
- Hiérarchie `OBSERVER < RUNNER < ADMIN`. Rôle trop faible →
  `403 {"error":"Insufficient permissions. Required: ADMIN"}` (comportement correct).

## Authentification

- Format du jeton : `<base64url(payload JSON)>.<hex hmac_sha256(secret, base64url)>`.
- Payload : `{sub, role, iat, exp, jti}` ; `iat`/`exp` sont comparés à `Date.now()` donc **en millisecondes**.
  Marge d'horloge acceptée sur `iat` : 5 min. Rôles valides : `OBSERVER`, `RUNNER`, `ADMIN`.
- Secret : `AUTH_SECRET` (≥ 32 caractères) sinon fichier `.auth-secret` dans le cwd du serveur
  (git-ignoré, 64 hex, généré au premier appel authentifié). Sans secret : fail-closed, tout est rejeté.
- **Aucune route n'émet de jeton.** Tout appelant sans jeton reçoit
  `401 {"error":"Authorization header required"}` ; jeton invalide → `401 {"error":"Invalid or expired token"}`.

### Forger un jeton localement (audit uniquement)

Lire le fichier `.auth-secret`, signer le payload, ne **jamais** afficher ni journaliser le secret
ou le jeton produit. Vérifier ensuite qu'un rôle insuffisant renvoie bien 403 (preuve que l'auth marche).

```python
import base64, hashlib, hmac, json, time, uuid
from pathlib import Path
secret = Path("hermes-orchestrator/.auth-secret").read_text().strip().encode()
now = int(time.time() * 1000)
payload = {"sub": "audit", "role": "ADMIN", "iat": now, "exp": now + 3_600_000, "jti": uuid.uuid4().hex}
body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
token = body + "." + hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
```

## `/codelab` — valeurs acceptées et décisions

- `origin` ∈ `dashboard | api | hermes | rpc` (autre valeur → 400).
- `mode` ∈ `AUDIT | DEV | APPROVAL` (`AUTO` → 400).
- `APPROVAL` : `202 {"message":"Task registered, awaiting Security Gate approval"}` puis
  `POST /codelab/approve/:id` → `200 {"approved":true,"execution":"blocked_isolation_required"}`.
  Statut final : `blocked_isolation_required` avec
  `errors: ["ISOLATION_REQUIRED: security gate provides no effective isolation; refusing to execute
  arbitrary code. Set ALLOW_UNSANDBOXED_EXECUTION=1 ONLY to run with NO isolation (explicit, documented risk)."]`.
- **Approuver ≠ exécuter.** Tant que ce refus existe, le Code Lab via l'orchestrateur ne produit aucun diff
  ni aucune exécution : ne jamais le présenter comme fonctionnel.
- `allowed_paths: []` est codé en dur dans `codelab_adapter.ts` : le champ est déclaré, jamais rempli,
  jamais vérifié par le gate. La notion de « chemins autorisés » est décorative.

## Chemins simulés (à ne pas certifier comme réels)

- `POST /inference` → `Response based on <school> perspective: <message>`.
  Source : `RequestQueue.generateResponse`, commentaire « In production, this would call the loaded model ».
  Les tests passent, la route répond 200, et pourtant aucun modèle n'est appelé.
- Routage : `CLOUDFLARE_ACCOUNT_ID` / `CLOUDFLARE_AUTH_TOKEN` de 15 caractères = placeholders →
  `[Router] Using simulated routing`. Un identifiant d'account Cloudflare réel fait 32 hex, un token 40+.

## Prouver d'où vient un message « permission »

- **Un littéral présent dans un seul composant identifie l'émetteur.**
  `grep -rln "Authorization header required"` → uniquement `hermes-orchestrator/src|dist` : donc un 401
  « vu dans le dashboard » ne peut venir que de `:3000`.
- Le dashboard Python est innocent par construction : `grep -n "urlopen\|requests\.\|http://" experiments/dashboard.py`
  → **aucun appel HTTP sortant** ; chemins inconnus → `404 {"error": "Not found", "code": "error", "request_id": …}`,
  il ne renvoie jamais 401 et n'expose pas de route `/api/orchestrator/*`.
- Refus CSRF reproductible (côté dashboard) : `POST /api/experiments` sans en-tête →
  `403 {"error":"Forbidden: CSRF token missing or mismatched","code":"csrf_failed"}` ; avec
  `X-Lifemean-CSRF: <valeur du cookie lifemean_csrf>` → `200 {"status":"created"}`.
  Le wrapper `fetch` du dashboard pose bien l'en-tête (`dashboard.html`, `headers.set('X-Lifemean-CSRF', token)`) :
  un 403 CSRF signale un appel qui contourne ce wrapper, pas une absence de câblage.

## Corollaire de diagnostic

Trois ruptures distinctes produisent la même plainte « erreur de permission » :
(1) aucun jeton → 401 ; (2) rôle trop faible → 403 « Required: ADMIN » ;
(3) gate d'isolation → tâche approuvée mais `blocked_isolation_required`.
Toujours identifier laquelle avant de proposer un correctif — les remèdes n'ont rien en commun.
