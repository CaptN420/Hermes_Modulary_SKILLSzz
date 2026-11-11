# Docker — volumes de runs, propriété et vérification

Concerne le déploiement Docker du dashboard Life_mean (`docker-compose.yml`, `life-mean-dashboard:local`).

## 1. Symptôme typique

Dans le panneau CONVERSATION du dashboard :

```
System  SYSTEM_ERROR
[Erreur 13] Permission denied: '/app/debate_lab_runs/debatelab_<id>'
```

Le message d'origine, côté application, est encore plus net :

```json
{"type": "RUN_FAILED", "error": "[Errno 13] Permission denied: '/app/debate_lab_runs/debatelab_006dd026d2'",
 "error_type": "worker_crash"}
```

`/app/...` ⇒ c'est **dans le conteneur**. `Errno 13` ⇒ `EACCES`, système de fichiers — rien à voir avec l'authentification ni avec `PolicyGuard`.

## 2. Échelle de diagnostic (dans cet ordre)

```bash
D=life_mean_realm-dashboard-1

# a) qui tourne dedans ?
docker exec $D id

# b) comparer un volume sain et un volume fautif
docker exec $D sh -c 'ls -ld /app/data /app/overrides /app/code_lab_runs /app/debate_lab_runs'

# c) sonde A/B : même commande, deux volumes (aucune donnée touchée)
docker exec -u app $D sh -c 'mkdir /app/data/probe && rmdir /app/data/probe && echo "data OK"; \
  mkdir /app/debate_lab_runs/debatelab_probe'

# d) pourquoi un chown interne échoue
docker inspect $D --format 'User={{.Config.User}} CapDrop={{.HostConfig.CapDrop}} ReadOnly={{.HostConfig.ReadonlyRootfs}}'
docker exec -u root $D sh -c 'grep Cap /proc/self/status'
```

Résultat attendu sur un conteneur durci : `uid=999(app)`, `CapDrop=[ALL]`, `CapEff=0000000000000000` → `chown` renvoie `Operation not permitted` **même en root**.

## 3. Réparation immédiate (sans arrêter le dashboard)

Le démon Docker, lui, a les capacités : un conteneur jetable aux capacités par défaut monte les volumes et corrige l'ownership.

```bash
docker run --rm --user 0 --entrypoint sh \
  -v life_mean_realm_life_mean_debate_lab_runs:/x \
  -v life_mean_realm_life_mean_code_lab_runs:/y \
  life-mean-dashboard:local -c 'chown -R 999:999 /x /y && ls -ld /x /y'
```

Les noms de volumes se lisent sur le conteneur en cours :

```bash
docker inspect $D --format '{{range .Mounts}}{{.Name}} -> {{.Destination}}{{"\n"}}{{end}}'
```

Vérification : `docker exec -u app $D sh -c 'mkdir /app/debate_lab_runs/probe_ok && rmdir /app/debate_lab_runs/probe_ok'` doit passer.

## 4. Correctif durable : service d'init root

Un volume nommé n'est initialisé qu'une fois : corriger à la main ne protège pas un déploiement neuf. Ajouter un service qui répare l'ownership avant le démarrage du dashboard, **sans** toucher à son durcissement :

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

Validation **sans** recréer le dashboard (donc sans tuer un run en cours) :

```bash
docker compose config -q && docker compose run --rm volumes-init
```

`docker compose up -d` recrée le conteneur dashboard : à réserver au moment où aucun débat ne tourne.

## 5. Entrypoint : le garde qui ne s'exécute jamais

```sh
# MORT : l'image déclare USER app, donc id -u vaut 999 et la branche est ignorée
if [ "$(id -u)" = "0" ]; then chmod 777 /app/debate_lab_runs …; fi
```

Remplacer par un avertissement explicite si un volume n'est pas inscriptible (`[ ! -w "$d" ]`), qui pointe vers `docker compose up -d volumes-init`. `chmod 777` était de toute façon la mauvaise réponse : c'est `chown` vers l'uid applicatif qu'il faut.

## 6. Prouver qu'un run produit vraiment

Le statut de l'API (`running`) est déclaratif. La preuve est dans la base du run :

```bash
docker exec $D python -c "import sqlite3;\
 c=sqlite3.connect('/app/debate_lab_runs/<run_id>/debate.db');\
 print(c.execute('select count(*) from turns').fetchone()[0])"
```

Colonnes utiles de `turns` : `turn_id, round, speaker, speaker_role, moderator_question, moderator_reason, response, model, duration_seconds, finish_reason, was_truncated`. Un débat de 20 tours avec un modèle local ~27B prend 10–15 min (≈10–15 s de génération par tour + modération) : sonder toutes les 20 s, pas toutes les 2 s.

Le dossier du run (`debate.db`) n'apparaît qu'au démarrage du worker, quelques secondes après `start` : un `test -d` immédiat renvoie « absent » sans que ce soit une erreur.

## 7. LLM local depuis le conteneur

```bash
docker exec $D python -c "import urllib.request,json;\
 raw=open('/app/overrides/llm.env').read();\
 kv=dict(l.split('=',1) for l in raw.strip().splitlines() if '=' in l);\
 url=[v for k,v in kv.items() if 'BASE' in k][0]; key=[v for k,v in kv.items() if 'KEY' in k][0];\
 req=urllib.request.Request(url.rstrip('/')+'/models', headers={'Authorization':'Bearer '+key});\
 print(json.loads(urllib.request.urlopen(req,timeout=6).read())['data'][0]['id'])"
```

Attendu : un identifiant de modèle (`kwaipilot_kat-coder-v2.5-dev`, `qwen3.5-2b`, …). Base `http://host.docker.internal:1234/v1` : `localhost` **dans** le conteneur ne désigne pas la machine hôte. Ne jamais imprimer la clé — seulement sa longueur ou un booléen.

## 8. Pièges de diagnostic

- Un message `/app/...` ne peut pas venir d'un script lancé sur l'hôte : chercher le binaire fautif côté conteneur d'abord.
- L'erreur peut ne pas être persistée : elle a été rendue en direct puis perdue. La retrouver par l'API (`/api/debate/timeline`, `/api/debate/runs`) plutôt que par `grep` dans les fichiers.
- `docker exec` sans `MSYS2_ARG_CONV_EXCL='*'` sur git-bash réécrit les chemins des arguments : préfixer les commandes Docker contenant `-v`, `--format` ou des chemins `/app/...`.
