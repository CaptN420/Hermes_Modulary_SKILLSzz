# Durabilité, reproductibilité & honnêteté des artefacts

Recettes vérifiées en exécution sur le dashboard Docker de Life_mean_realm
(`127.0.0.1:8080`). Chaque bloc a servi à produire une preuve réelle, pas une
relecture de code.

## 1. Créer et lancer un run via l'API (CSRF obligatoire)

Le cookie et l'en-tête CSRF viennent de `GET /dashboard` ; un POST sans
`X-Lifemean-CSRF` renvoie 403 (voir la règle du double-submit dans SKILL.md).

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

## 2. Prouver la durabilité par un restart

```bash
docker compose restart dashboard && sleep 12
docker ps --format "{{.Names}} {{.Status}}"     # Up … (healthy)
```

Puis relire l'état — c'est **ça** la preuve, pas le test unitaire :

```python
status, body = call("/api/experiments")
d = json.loads(body)
run = d["experiments"][exp]
assert run["status"] == "COMPLETED" and run["rehydrated"] is True
status, body = call(f"/api/experiments/{exp}/manifest")
manifest = json.loads(body)
assert manifest["rehydrated"] is True and manifest["config"]["seed"] == 21
```

Un run réhydraté reste `COMPLETED` (jamais `running`) et son manifeste porte
`rehydrated: true`, `restored_totals: {events, traces, agents}`, `truncated:` et
`traces_absent_reason` quand le build ne produit pas de traces.

`POST /api/experiments` **crée** le run (`status: created`) : il faut ensuite
`POST /api/experiments/{id}/start`. Un run « terminé » avec `tasks_completed: 0`
vu juste après la création vient de là, pas du moteur.

## 2bis. Sonder l'observabilité persistée (avant / après restart)

```python
# 1. lancer, attendre la fin
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
# 2. le fichier de run contient le bloc borné
docker exec life_mean_realm-dashboard-1 sh -c 'python - <<EOF'
import json
d = json.load(open("/app/data/experiments/runs/<exp>.json"))
o = d["observability"]
print(len(o["events"]), len(o["traces"]), len(o["agents"]), o["totals"], o["truncated"], o["limits"])
EOF

# 3. restart puis relire : c'est la seule preuve de réhydratation
docker compose restart dashboard && sleep 14
```

Attendu après restart : `rehydrated: true`, les mêmes `events` qu'avant
(`experiment_started` / `experiment_completed`), `agents: {agent_1..3}`,
`progress.status: COMPLETED`, et une note du type
`(2 of 2 events, 0 of 0 traces)`. Un `traces_absent_reason` présent est la
réponse correcte — pas un bug à « réparer » en inventant des traces.

## 2ter. Registres d'auto-extension : la persistance se prouve aussi par restart

```python
call("/api/extensions/tools", "POST", {"description": "Volume d'une sphère"})   # -> persisted: True
call(f"/api/extensions/tools/{tool_id}/approve", "PUT", {"by": "human"})      # -> 200 approved
```

Puis `docker compose restart dashboard` et `GET /api/extensions/tools` : les
entrées doivent être là (`data/extensions/registries.json` sur le volume).
Deux propositions de descriptions différentes doivent produire **deux ids**
distincts — un id identique signifie que les propositions s'écrasent.

## 3. Champs attendus dans le manifeste de reproductibilité

`engine{name,version}`, `environment{python,system,machine}`,
`dependencies{combined_sha256}` (pyproject + uv.lock), `git{commit,dirty}`,
`seed`, `deterministic`, `models`, `tools`, `generator_version`,
`prompt_version`, et `reproducibility_fingerprint` (hash stable des conditions).
Aucun secret : versions, ids et hashes seulement — il existe un test qui piège
les variables d'environnement pour le prouver.

## 4. A/B sur le même seed (preuve d'un correctif de pipeline)

1. Rejouer le **même** seed avant le correctif, noter `pass_rate` et les lignes
   fautives du RAW.
2. Appliquer le correctif, relancer le même seed.
3. Comparer `pass_rate` (0.333 → 1.0 dans le cas réel) puis, ligne par ligne,
   `answer` / `ground_truth` / `valid` / `error` :

```bash
docker exec life_mean_realm-dashboard-1 sh -c 'python - <<EOF'
import json
for line in open("/app/data/raw_debates/<exp>.jsonl", encoding="utf8"):
    d = json.loads(line)
    v = d.get("validation_result") or {}
    print(d.get("answer"), "|", d.get("ground_truth"), "|", v.get("valid"), "|", d.get("error"))
EOF'
```

Un seed différent ne prouve rien : les tâches changent avec le seed.

## 5. Auditer les affirmations d'un README avant publication

Trois vérifications qui ont réellement démenti le README existant :

| Affirmation | Vérification | Verdict |
|---|---|---|
| `GET /api/experiments/{id}/raw` | `grep -n 'endswith("/raw")' experiments/dashboard.py` | **inexistant** (seul code-lab a `/raw`) |
| « 22 outils » | compter les dicts `*_TOOLS` par famille | **60** (22 math, 15 physics, 14 chemistry, 3 logic, 6 coding) |
| nombre de tests | `.venv/Scripts/python -m pytest tests/ -q` | 1694 passed / 13 skipped, pas 713 |

Règle : aucune affirmation de compteur, d'endpoint ou de statut ne part dans un
README sans la commande qui l'a produite. Après publication, relire ce que GitHub
sert réellement (`curl -s https://raw.githubusercontent.com/<owner>/<repo>/main/README.md`).
