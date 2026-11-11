---
name: life-mean-recent-lessons
category: software-development
description: Journal daté Oct 2026 des leçons Life_mean — temporaire, archivable.
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

Charger cette skill quand une tâche touche Life_mean / Life_mean_realm sur les sujets suivants :
Pipeline Inspector, ingestion de logs, Feature Pool et ses statuts, dashboard HTML et ses onglets,
rapports de validation, orchestrateur et permissions, ou déploiement Docker du dashboard. Les leçons de ce fichier sont des
règles durables vérifiées en exécution ; la mécanique détaillée de l'ingestion est dans
`references/incremental-ingestion-offsets.md`, celle de la découverte du pool dans
`references/feature-pool-discovery.md`, la surface HTTP/authentification de l'orchestrateur dans
`references/orchestrator-permissions.md`, et la procédure d'ajout d'un onglet/vue au dashboard dans
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

## Pipeline Inspector & Feature Pool — règles durables

- **Un statut BROKEN/BLOCKED ne se déduit jamais d'un comptage de caractères.** Valider la syntaxe avec `ast.parse(source, filename=...)` et un cache par fichier. Comparer `content.count('(')` à `content.count(')')` produit des faux positifs massifs (docstrings, f-strings, regex) et enterre du code sain. Si un audit annonce N features cassées, rejouer la vérification avec un vrai parseur avant de croire l'audit.
- **VALIDATED exige une preuve de test.** `READY` = le code parse et ses dépendances se résolvent ; `VALIDATED` = au moins un fichier de test associé. Ne jamais promouvoir un statut parce qu'une feature a été découverte ou analysée : `no_tests` est un *coverage gap* (`feature.coverage_gaps`), jamais un défaut du code ni une raison de BROKEN.
- **Deux noms de fichier pour le même rapport = le périmé gagne.** Quand un producteur écrit `feature_pool_report.json` et un consommateur lit `.feature_pool_report.json`, le consommateur choisit désormais le fichier le plus récent par mtime et expose `generated_at` ; l'export écrit le même payload aux deux emplacements (aucune suppression). Toujours vérifier *quel* fichier un consommateur a réellement chargé avant d'interpréter ses chiffres.
- **Les compteurs d'analyse doivent déclarer leur échantillon.** Les analyses qui lisent « les N derniers événements » portent leur payload avec `sample: {events_scanned, limit, truncated, note}` ; sans ça, un compteur d'échantillon est lu comme un total exhaustif.
- **Masquage : seuil de longueur = trou de sécurité.** Exiger une valeur non vide, pas une longueur minimale (`password=hunter2`, 7 caractères, passait en clair). Couvrir aussi `access_key`, les clés `AKIA…` et les blocs PEM.
- **Un seul `SyntaxError` neutralise tout un `<script>`.** Deux causes rencontrées dans le dashboard : `const` redéclaré dans la même portée, et chaîne littérale coupée par un vrai retour à la ligne. Symptôme vu par l'utilisateur : « les onglets ne changent pas ». Vérifier chaque bloc isolément avec `node --check` (script fourni en `scripts/audit-js-blocks.py`) — un `const` dupliqué ne peut pas passer, donc un OK prouve la correction.
- **Dashboard Life_mean : le POST exige l'en-tête `X-Lifemean-CSRF`** (double-submit du cookie `lifemean_csrf`), pas `X-CSRF-Token`. Un 403 sur un POST depuis un test manuel vient le plus souvent de là. Valider les routes par de vraies requêtes (GET + POST avec cookie) plutôt qu'en relisant le handler.
- **Dans Docker, `/app/data` est un volume** : il masque `data/raw_debates`. L'inspector conteneur ne voit que les volumes montés et paraît « vide » alors que le poste local a des centaines de milliers d'événements. Distinguer explicitement les chiffres locaux et conteneur dans tout rapport.
- **`docker compose up` est refusé en foreground** par le garde-fou « long-lived server » : pour appliquer une nouvelle image, faire `docker stop/rm` puis `docker compose create dashboard` puis `docker start`, et vérifier ensuite `docker inspect … {{.State.Health.Status}}`.

## Docker : permissions des dossiers de runs (Errno 13)

- **Les volumes nommés gardent le propriétaire de leur création.** Un volume initialisé par root reste `root:root` après tous les rebuilds d'image ; l'app tourne en `uid=999(app)` → le worker crashe à la création de son dossier avec `[Errno 13] Permission denied: '/app/debate_lab_runs/debatelab_<id>'` (`error_type: worker_crash`), à chaque tentative et avec un nouvel id à chaque fois. Toujours comparer un volume sain à un volume fautif : `docker exec <c> ls -ld /app/data /app/overrides /app/debate_lab_runs /app/code_lab_runs`.
- **`chown` est impossible depuis le conteneur durci** (`cap_drop: [ALL]` + `no-new-privileges` + `read_only` → `CapEff=0000000000000000`) : `chown: … Operation not permitted` même avec `-u root`. Réparer depuis un conteneur jetable aux capacités par défaut, puis rendre la correction durable par un service d'init root — sans affaiblir le profil du dashboard.
- **Un `if [ "$(id -u)" = "0" ]` dans l'entrypoint est du code mort** quand l'image déclare `USER app` : vérifier tout garde de privilège contre `docker inspect <c> --format '{{.Config.User}}'`, sinon il ne s'exécute jamais et la panne reste invisible pendant des semaines.
- **`status: running` ne prouve rien** : compter les lignes de `turns` dans `/app/debate_lab_runs/<run>/debate.db` via `docker exec` pour prouver qu'un débat produit réellement (20 tours ≈ 10–15 min avec un 27B local).
- **`:1234` qui répond « An LM Studio API token is required » n'est pas éteint** : c'est un 401, le serveur tourne. Depuis le conteneur la base est `http://host.docker.internal:1234/v1` et la clé vit dans `/app/overrides/llm.env` (`LIFE_MEAN_LLM_API_KEY`). Réserver « hors ligne » à un vrai `Connection refused`.
- **`docker compose up -d` recrée le dashboard et tue tout run en cours** ; pour valider un nouveau service d'init sans interrompre, `docker compose config -q` puis `docker compose run --rm <service-init>`.

Recettes complètes (sonde A/B, one-liner de réparation, service `volumes-init`, vérification SQLite, test de la clé LLM) : `references/docker-run-volumes.md`.

## Studio qui « ne fait rien » au lancement (2026-10-31)

- **Symptôme** : `start_studio.bat` affiche ses 3 lignes `[INFO]` puis rien — aucune fenêtre, aucun process visible, aucun message d'erreur. **Ce n'est pas le .bat** : la fenêtre se bloque dans le constructeur de `LifeMeanStudioApp`, avant `app.exec()`.
- **Diagnostic** : `faulthandler.dump_traceback_later(8, repeat=True)` dans un script wrapper qui fait `runpy.run_module("life_mean_studio", run_name="__main__")`. Un timeout externe ne dit rien ; le dump de pile dit exactement où ça bloque.
- **Cause trouvée** : `feature_pool/analyzer.py::_find_tests` faisait `Path.rglob("test_*.py")` **par feature** (187 features) en lisant chaque fichier. `rglob` descend dans `.venv`/`node_modules` avant tout filtre → ~2600 `test_*.py`, ~minutes à l'infini. Le filtre `_is_excluded` s'appliquait après le parcours, donc ne servait à rien.
- **Correctif** : index construit **une seule fois** par `os.walk` avec élagage des dossiers exclus (`dirnames[:] = [...]`), contenus lus une fois et mis en cache de classe. `analyze_all` passe de >10 min à 0.75 s.
- **Règle** : toute analyse lancée depuis un constructeur de page Qt doit être soit indexée/cachée, soit déférée (`QTimer.singleShot(0, ...)`) pour que la fenêtre peigne avant. Les sondes réseau de `health.py` (timeout 3 s, et le port du dashboard Docker *accepte une connexion sans jamais répondre*) passent par un `threading.Thread` + `Signal(object)` — sinon la fenêtre apparaît mais reste gelée plusieurs secondes.
- **Vérification** : `QT_QPA_PLATFORM=offscreen` + `QTimer.singleShot(15000, check)` qui imprime `fp_table.rowCount()` (doit égaler le nombre de features découvertes : **989** depuis l'élargissement de la découverte, 187 avant) et `service_table.rowCount()` (4). Le .bat se valide en vérifiant `netstat -ano | grep :3000` **et** la présence d'une fenêtre visible via `EnumWindows` (titre `Life_mean Studio`).
- **`.bat`** : `cmd /c "cd /d \"%ROOT%path\" && npm start"` ne fonctionne pas — cmd n'a pas d'échappement `\"`. Utiliser `start "Titre" /D "%ROOT%hermes-orchestrator" cmd /c "npm start"`. Toujours écrire les `.bat` en CRLF et lire `%ERRORLEVEL%` juste après `python -m ...` pour afficher l'erreur au lieu de fermer la fenêtre.

Mécanique détaillée de l'ingestion incrémentale (offsets absolus, plafond, drapeau `truncated`, déduplication) : voir `references/incremental-ingestion-offsets.md`.

## Feature Pool : la couverture n'est pas l'inventaire (2026-11-01)

- **`feature_pool` ne voit pas tout le code, et son silence n'est pas une preuve.** `scanner.py::_build_scan_paths` contient une **liste de dossiers codée en dur** (core, experiments, life_mean_studio, captn_runtime, philosophical_council, debate_lab, code_lab, autopilot, hermes-debate, historical, experimental, life_mean_lab, library, compare, analysis) : `pipeline_inspector`, `feature_pool`, `data`, `life_mean_extensions`, `hermes_cronjob_manager` en sont absents. Puis `_classify_feature` ne retient que les classes dont le nom contient un mot-clé (router, provider, safety, sentinel, debate, validator…) ou un suffixe (engine, controller, manager, worker, agent). Mesuré : **187 features pour 1817 classes (10,3 %)** ; 42 classes sécurité/permissions invisibles dont `PolicyGuard`, `ResourceGuard`, `ExperimentExecutionGate`. Conclusion pratique : **ne jamais conclure « cette capacité n'existe pas » depuis 0 hit du pool** — vérifier par `grep`/`ast` dans le code.
- **Élargissement appliqué (procédure et chiffres de contrôle).** `_build_scan_paths` découvre désormais tout paquet de premier niveau sauf denylist ; `_classify_feature` retombe sur un classement par chemin (`PATH_KEYWORDS`), puis `TOOLS`. Résultat mesuré : **989 features** (1280 classes − 70 privées/test − 221 fusions par nom), **0 BROKEN**, `PolicyGuard`/`ResourceGuard`/`ExperimentExecutionGate` présents, Studio construit en 0,13 s avec la table à 989 lignes, `analyze_all` 1,75 s. Recette complète et décomposition : `references/feature-pool-discovery.md`.
- **La denylist doit nommer les workspaces générés, sinon ils se font indexer.** Premier essai sans `code_lab_runs/` : **1943 fichiers scannés** au lieu de 839, 1004 features dont des copies de runs. Toujours compter les fichiers retenus par `_build_scan_paths()` **avant** de valider un changement de découverte ; un dossier de runs peut contenir plus de `.py` que tout le code produit.
- **Ne jamais calibrer un seuil d'acceptation sur un comptage naïf de classes.** Le seuil « 1439 features attendues » (1817 classes − 378 de `tests/`) était faux : `_register_feature` fusionne les homonymes et les classes privées sont ignorées. La métrique qui tient est **100 % des noms de classes non privés indexés** (1055 noms distincts → 1055 indexés, dont 221 multi-emplacements), pas un nombre brut de features.
- **VALIDATED ≠ validé** : la preuve est une recherche de **sous-chaîne** du nom de la feature dans le fichier de test (`analyzer._find_tests`) — un test de `legacy/`, `historical/` ou `hermes-debate/` suffit. Avant élargissement : 138 VALIDATED dont **27** avec pour seule preuve un projet étranger ; après élargissement : **632 VALIDATED dont 129** dans ce cas (20,4 %). L'élargissement n'aggrave pas la proportion mais **multiplie le nombre absolu** : corriger `_find_tests` (exiger un import du module ou une référence `module.Symbol`) avant de présenter ces statuts comme décisionnels, ou laisser les features en `READY` avec `coverage_gaps=["test_evidence_unverified"]`.
- **Les conflits du pool sont un produit cartésien** : 8190 = 70 legacy × 117 modern, 0 high/medium. `orphans: 187` = le graphe de dépendances ne relie rien. Ne pas s'appuyer sur `ready_for_integration` avant d'avoir réparé `dependencies`.

## Le pont Pipeline Inspector ↔ Feature Pool existe déjà

`pipeline_inspector/feature_pool_bridge.py` lit le rapport le plus récent par mtime, normalise les noms (`MathValidationWorker` ≈ `math_validation_worker`) et **sépare usage observé et statut de validation**. Ne pas écrire un nouvel explorateur : corriger la couverture de découverte et ajouter la page Studio (aucune page `pipeline_inspector` dans `life_mean_studio/launcher/app.py`).

## « Erreur de permission » : classer le littéral avant de théoriser

- **Trois familles, jamais interchangeables.** `[Errno 13] Permission denied` / `EACCES` = permission **de système de fichiers** (un chemin en `/app/...` désigne le conteneur) ; `401 Authorization header required` = couche d'authentification Node ; `403 Forbidden: CSRF token missing` = CSRF du dashboard. Quand l'utilisateur dit « j'ai eu une erreur de permission », il parle le plus souvent de la première : **obtenir la capture ou le message exact avant de construire une théorie**, sinon on répare un système que l'erreur n'a jamais touché (une théorie complète du 401 a été bâtie alors que le vrai message était un `Errno 13`).
- **Un choix proposé dans un formulaire n'est pas une preuve** : si l'utilisateur sélectionne une option parmi des messages d'erreur candidats, la relire contre la capture réelle — et signaler l'écart au lieu d'enchaîner sur la mauvaise piste.

## Orchestrateur & permissions : deux systèmes, aucun relié aux clients

- **Deux couches indépendantes.** Python : `core/safety/policy_guard.py` (179 l., testé) n'est appelé que sur **une** opération (`start_debate`, `core/debate/engine.py`), et `core/debate/experiment_gate.py::_check_safety_guards` ne vérifie que des bornes numériques (« In a real system, this would check PolicyGuard, ResourceGuard »). Node : HMAC + Security Gate sur toutes les routes sauf `/health`. Ne jamais décrire « le système de permissions » au singulier.
- **Le 401 est structurel, pas un incident** : aucune route n'émet de jeton et aucun client Life_mean n'en envoie → `Authorization header required` sur tout appel à `:3000`. Matrice des routes, format HMAC (iat/exp en **millisecondes**) et forge de jeton local : `references/orchestrator-permissions.md`.
- **Approuver ≠ exécuter** : une tâche `/codelab` en mode `APPROVAL` est acceptée (202), approuvée (200 `approved:true`) puis bloquée `blocked_isolation_required`. Tant que ce refus existe, ne pas présenter le Code Lab via l'orchestrateur comme fonctionnel, et ne pas proposer de « brancher » le dashboard dessus avant d'avoir traité l'isolation.
- **Le dashboard `:8080` ne parle pas à l'orchestrateur** : zéro appel HTTP sortant dans `experiments/dashboard.py`, pas de route `/api/orchestrator/*`, et `:3000` n'écoute qu'en loopback. Un 401 « vu dans le dashboard » vient donc de `:3000` appelé directement.
- **Un littéral unique dans le dépôt désigne l'émetteur** : avant de chercher la cause d'un message d'erreur, `grep -rln "<message exact>"`. S'il n'existe que dans un composant, les autres sont innocents par construction — cela évite de débugger le mauvais service.

## Registres d'auto-extension (P5) — quatre pièges dans un « total: 0 »

- **Un registre vide peut cacher 60 outils réels.** `library/tools` fournit 60 outils déterministes utilisés à chaque run par `ToolWorker` ; le registre d'extension n'en voyait aucun. Toute réponse de liste doit séparer `catalog` (ce qui existe, `in_registry: false`) de `all`/`stats` (ce qui est approuvé) — découvrir n'est pas activer, et l'écrire dans le payload évite de faire passer une absence d'approbation pour une absence de capacité.
- **Un succès d'API sans stockage est un mensonge à retardement.** Les registres vivaient en mémoire : `POST /api/extensions/tools` renvoyait `proposed` puis tout disparaissait au restart. Persister (`data/extensions/registries.json`, écriture atomique + `.bak`, rechargé à la création de la couche) et répondre `500 persistence_failed` (« applied in memory but NOT persisted ») quand l'écriture échoue.
- **`do_PUT` ne routait que `/api/settings`** et `_ID_RE` (`/(skills|tools)/([^/]+)$`) n'acceptait pas le suffixe d'action : `/approve`, `/activate`, `/disable` renvoyaient **404 sur POST comme sur PUT**. Toute « porte d'approbation humaine » se valide par un vrai `PUT` sur l'URL documentée, pas en relisant le mixin.
- **Un `OSError` qui s'échappe d'un handler ne produit pas un 500 : il coupe la connexion** (`RemoteDisconnected` côté client). Le bac à sable des outils générés vivait dans l'image en lecture seule (`/app/sandbox`) → `EROFS` sur chaque proposition. Le mettre sous `data/sandbox/` (volume) et envelopper la création dans `try/except` → `500 proposal_failed`. Et les propositions sans `need_id` doivent tirer leur id d'un hash de la description, sinon toutes partagent `tool-generated-tool` et s'écrasent en version.
- **Un test qui propose un outil écrit dans le dépôt s'il ne redirige pas son bac à sable.** Le chemin par défaut vit sous `data/` : toute fixture qui appelle `POST /api/extensions/tools` doit poser `LIFE_MEAN_SANDBOX_DIR` (et `LIFE_MEAN_EXTENSIONS_DIR`) vers `tmp_path`, sinon `git status` se salit avec `sandbox/tools/tool-*` et les propositions d'un test polluent les suivants.

## Observabilité persistée : ne pas annoncer une section toujours vide (P6)

- **Une capacité déclarée mais jamais appelée est un mensonge de schéma.** Avant de présenter une section de payload comme une preuve, chercher son émetteur : `grep -rn "record_transition\|record_rule_application\|update_progress" --include=*.py . | grep -v observability`. Sans appelant, deux issues seulement : câbler la source, ou déclarer l'absence dans le payload (`traces_absent_reason`) — jamais un champ toujours vide qui passe pour une mesure. Le câblage se fait par **sink optionnel** (`runner.trace_sink = callable`) qui ne fait qu'émettre, avec un `try/except` côté consommateur : une trace ne doit jamais faire échouer une tâche. Vérifier ensuite sur un run réel (`traces: 6` pour 3 tâches, `tasks_completed: 3`), pas en relisant le schéma.
- **Persister l'observabilité avec ses bornes, dans le même fichier que l'état.** Le summary de run (`data/experiments/runs/<id>.json`) porte `observability: {agents, events, traces, totals, truncated, limits}` ; les plafonds viennent d'env (`LIFE_MEAN_PERSIST_EVENTS`, `LIFE_MEAN_PERSIST_TRACES`) pour être testables. Un snapshot d'observabilité ne doit jamais faire échouer un run terminé : `try/except` + log, comme l'écriture du summary.
- **Un test qui asserait l'ancienne limitation doit être réécrit, pas contourné.** `test_run_durability` vérifiait `events == []` (c'était vrai quand rien n'était persisté). Quand le contrat change, mettre à jour l'assertion **et** écrire dans le docstring du test que c'est l'ancienne limitation qui est remplacée — sinon le prochain lecteur prend l'ancien comportement pour la référence.

## « Bloqué par une dépendance » : vérifier d'abord que le code existe

- **Avant d'accepter un `BLOCKED_EXTERNAL`, faire deux greps** : le nom de la dépendance ET le nom de la fonctionnalité. Ici `psutil`/`win32evtlog` étaient absents **et** aucun collecteur Defender/Event Log n'existait dans le dépôt : le vrai statut était « non écrit », pas « bloqué ». Une dépendance manquante ne bloque que du code qui l'appelle.
- **Windows fournit déjà beaucoup sans pip** : `powershell -NoProfile -Command "Get-MpComputerStatus | ConvertTo-Json -Compress"` donne l'état Defender réel, `wevtutil qe <journal> /c:N /rd:true /f:xml` donne les événements (le format `json` n'existe pas, `text` n'est pas parsable — parser l'XML avec `xml.etree` après avoir enveloppé la sortie dans une racine).
- **Un collecteur doit dire qu'il ne peut pas** : sur un conteneur Linux/WSL2, `platform.system()` vaut `Linux` → renvoyer `ok:false, error:"not a Windows host"` et `degraded: [...]`, jamais un état plausible inventé.
- **Tester contre la machine réelle** pour ces collecteurs (ce sont des faits d'environnement), avec `skipif(not is_windows())`, et tester les cas d'erreur partout (binaire absent, timeout, journal inconnu).

## Outils mathématiques : parser l'expression, ne jamais balayer les chiffres

- **`re.findall(r"\d+", description)` fabrique de fausses réponses.** `sqrt(-1)` renvoyait `1.0` (signe perdu) et un décimal devenait sa troncature. Pour toute expression, analyser une grammaire fermée (`nom(args)`, `a^b` sur littéraux + `pi`/`e`), jamais `eval`, jamais de balayage de chiffres.
- **Un dict d'erreur ne doit pas pouvoir devenir une réponse.** `ln(0)` renvoyait `{'valid': False, 'error': 'value>0'}` comme `answer` parce que l'extraction retombait sur `answer = raw_answer`. Vérifier `valid is False` **avant** l'extraction, pas après.
- **Un refus de l'outil = verdict, pas « absence de réponse ».** Distinguer `UNSUPPORTED_MATH_OPERATION` (on ne sait pas faire) de `MATH_DOMAIN_ERROR` (l'outil refuse l'entrée) ; les deux conservent l'expression et la raison.
- **`tan` d'un angle où cos = 0 : `tan: None` + `tan_undefined`.** Refuser l'appel entier rendait `sin(90°)`, parfaitement calculable, impossible ; renvoyer `"inf"` ou `1.6e16` invente une valeur.
- **Transmettre `tool_name` au worker.** `ToolWorker` re-détecte quand `tool_name` est absent : une expression sans mot-clé (`2^8`) répondait « no tool » et le runner rendait `None` sans erreur.
- **Unités et bases explicites, jamais devinées.** `angle_deg` et `angle_rad` sont deux entrées distinctes ; une base de log est toujours passée (`ln`/`log` = e, `log10` = 10).

## Onglets et télémétrie hôte

- **Une barre d'onglets flex sans `flex-wrap` cache les derniers onglets.** Ils restent dans le DOM (`visible: true`, largeur non nulle) mais sortent de la fenêtre : présents, invisibles, non cliquables. Vérifier `scrollWidth > clientWidth` ou le nombre de lignes (`new Set([...children].map(b => round(top)))`), pas seulement `offsetParent`.
- **Un conteneur Linux ne peut pas lire l'hôte Windows** : pont explicite (agent hôte + client qui ne lève jamais). Le client doit valider la charge (sections attendues) et renvoyer une raison, sinon une réponse partielle passe pour valide. Sans agent, `degraded: [host_agent]` + l'URL tentée + la commande à lancer.
- **Un collecteur jamais exécuté n'est pas un collecteur vérifié.** `os_collectors` se passe de `psutil`/`win32evtlog` (`powershell Get-MpComputerStatus`, `wevtutil`) — la preuve se fait sur l'hôte, pas dans le conteneur Linux où `supported` vaut `false`.

## Brancher un outil n'est pas le supporter

- **Un outil sans générateur est mort.** Vérifier la chaîne complète : le générateur émet la tâche, la vérité terrain vient du même outil, le run la résout, la validation la déclare bonne. Mesurer la couverture par famille (compteur de descriptions) — sinon on croit supporter 9 opérations et 2 sont produites.
- **Vérité terrain = sortie de l'outil.** Recalculer la réponse avec une formule parallèle (même `math.log`, même convention) recrée la divergence qu'on cherche à éliminer : appeler l'outil.
- **`reasoning_type` par défaut ne doit pas être écrasé.** `"calculation"` est la valeur par défaut : la router vers un sous-type (`sin`/`cos`/`tan`) transforme toutes les tâches mathématiques en trigonométrie (mesuré : 300 tâches, 3 familles).
- **Ne générer que des domaines définis :** angles de `tan` hors 90° + k·180°, `log` sur > 1, `sqrt` ≥ 0. Une tâche générée hors domaine garantit un échec déterministe bruité.
- **`/manifest` doit porter le verdict, pas juste le compteur.** `tasks_completed` sans `tasks_valid`/`pass_rate` oblige à croiser trois sources ; et `pass_rate` doit être `None` (pas 0) tant que rien n'est validé.
- **Agréger les erreurs par code machine** (`MATH_DOMAIN_ERROR×3`) plutôt qu'en liste brute : c'est l'information qui dit quoi corriger.

## Journal d'usage runtime : observer l'exécution, pas les logs

- **Un compteur d'usage de logs mesure l'ingestion, pas l'exécution.** Dépendre de fichiers déjà ingérés rend le chiffre dépendant de ce que le pipeline de logs a conservé (et de la politique de rétention). Écrire un journal d'exécution append-only (`data/usage/feature_usage.jsonl`, une ligne par composant réellement exécuté, avec `experiment_id`/`task_id`) rend la preuve indépendante.
- **Émettre là où la décision est prise.** Première version : les cinq outils de la famille du routeur étaient journalisés alors qu'un seul tournait (×5 d'inflation). Le bon point d'émission est la ligne où `detect_tool()` a répondu.
- **Un persona muet ne compte pas.** Dans un débat, la ligne d'usage doit être émise par tour **avec contenu** (le garde de répétition peut produire des tours vides) ; compter les agents inscrits mesure le casting, pas l'exécution.
- **`ok=None` = « exécuté, verdict ailleurs ».** Ne jamais écrire un booléen inventé ; le verdict vient des traces `ValidationRule`.
- **Matcher par sous-chaîne : « unique » plutôt que « long ».** Une règle « ≥ 6 caractères des deux côtés » corrige le faux positif (`math_gcd` → feature « C ») mais bloque un nom court légitime (`Stoic` ne trouvait pas `StoicAgent`). La règle qui tient : candidat ≥ 4 caractères **et un seul candidat possible** (ambiguïté ⇒ aucun match). Vérifier par des cas nommés : `Nihilist→NihilistAgent`, `Stoic→StoicAgent`, `math_gcd→aucun`.
- **Garde de longueur des deux côtés dans un matcher par sous-chaîne.** `candidate_key in key` sans garde sur `candidate_key` fait qu'une feature nommée « C » (ou tout acronyme) absorbe `math_gcd` — mesuré : 14 features observées dont 1 faux positif, 13 après correctif. Un compteur d'usage n'est crédible que si l'appariement des noms est vérifié sur des cas courts.

## Git sur ce dépôt

- **Pas de backtick dans `git commit -m "..."` via bash** : le shell exécute la substitution (`answer: command not found`) et le mot disparaît du message. Écrire le message dans un fichier et utiliser `git commit -F` / `--amend -F`.

## « 2 features observées sur 989 » : la fenêtre récente n'est pas un échantillon

- **Une analyse qui lit « les N derniers événements par type » mesure le dernier producteur, pas le pipeline.** Sur 837 k événements locaux, la fenêtre récente (5 005 lignes) était 100 % `captn_experiences` : les 815 k événements `raw_debates` portant `tool_worker`/`math_validation_worker`/`router` n'étaient jamais lus, d'où « 2 observées » au lieu de 14.
- **Échantillonner par population** : `EventStore.distinct_values(colonne)` (colonne en **liste blanche** — une valeur d'API ne devient jamais un nom de colonne SQL) puis un quota identique par groupe (agent, puis source). Coût mesuré : 4,4 s sur 1,1 M d'événements.
- **Tout compteur d'échantillon doit publier sa couverture** (`coverage: {strategy, groups_sampled, per_group_limit, events_sampled, events_in_sampled_populations, truncated}`) ; sinon « 14 » se lit comme un total.
- **Chiffres local ≠ conteneur, et c'est légitime** : la base du conteneur n'a que 18 k événements (`text_log` + `captn_experiences`) parce que `/app/data` est un volume qui masque `data/raw_debates`. Toujours donner les deux jeux et nommer la cause.
- **Une couverture faible n'est pas toujours un bug** : 987 features non observées sur 989 correspondent à des classes (widgets Qt, stores) que ces pipelines n'instancient jamais. Le dire vaut mieux que forcer un chiffre.

## Un 403 renvoyé avant de lire le corps = connexion avortée sous Windows

- **Symptôme** : un test CSRF échoue ~1 fois sur 12 avec `ConnectionAbortedError: [WinError 10053]`, jamais de façon reproductible à la demande. Le client ne reçoit aucune réponse alors que le serveur a bien envoyé 403.
- **Cause** : `do_POST`/`do_PUT`/`do_DELETE` rejetaient avant `self.rfile.read(Content-Length)`. Windows réinitialise une socket fermée avec des données non lues ; selon le moment où le client finit d'écrire, la réponse est perdue.
- **Correctif** : `_drain_request_body()` (lecture + rejet, plafonné à 1 Mo) avant **chaque** réponse 403/401 des verbes mutants. A/B mesuré sur 60 POST avec 4 Ko : 53/60 réponses avant, 60/60 après.
- **Règle** : toute réponse d'erreur précoce (auth, CSRF, 404, quota) doit vider le corps de la requête, sinon les tests HTTP deviennent « instables » alors que le bug est déterministe côté socket.

## Un test « instable » qui lit du source : `inspect.getsource` ment après réécriture

- **`inspect.getsource` décrit le fichier tel qu'il était à l'import, pas tel qu'il est sur disque.** Réécrire un fichier pendant qu'un process tourne invalide tous les `co_firstlineno` enregistrés ; linecache relit le **nouveau** fichier et le tranche aux **anciennes** lignes → la fonction renvoyée est une autre fonction. Mesuré sur `experiments/dashboard.py` : assertion `True` avant réécriture, `False` pendant (le corps retourné était le chemin d'erreur de `_training_start`), fichier restauré avec sha256 identique.
- **Symptôme typique** : un test qui assert sur du texte source échoue une fois sur 500 exécutions, passe seul et dans tous les sous-ensembles, et la ligne citée dans le rapport ne ressemble pas du tout à la fonction visée. Ce n'est pas un flake de concurrence : c'est le cache de lignes.
- **Correctif** : relire le fichier et retrouver la définition **par nom** avec `ast` (`ast.get_source_segment`) — voir `tests/source_utils.py::current_source()` ; ou asserter le **contrat réel** (`inspect.signature(fn).parameters["host"].default`). Ne jamais « assouplir » l'assertion face à ce faux flake.
- **Corollaire de méthode** : ne jamais éditer un fichier `.py` du dépôt pendant qu'une suite pytest tourne dessus — c'est exactement ce qui a produit le seul échec non reproduit d'un audit complet.

## Porte de vérification avant le patch suivant (exigée par le créateur)

- **Séquence imposée** : `Feature Pool First` (prouver qu'une capacité existe avant d'en créer une) puis `Verify Before Next Patch` (aucun correctif suivant tant que le précédent n'a pas de relevé de vérification).
- **Checkpoint Git = opération contrôlée, jamais `git add .`** : (1) `git status` + résumé des diffs, (2) scan de secrets sur les fichiers candidats (clés `sk-`/`gho_`/`AKIA`, blocs PEM, `password=`), (3) liste de fichiers **explicite** dans `git add -- …`, (4) exclusion des artefacts générés (exports de rapports, `dashboard_debug.html`, `_*.py`, `spec.json` d'état, `*.jsonl` d'exécution), (5) `git diff --cached --numstat` pour vérifier l'absence de binaire, (6) message de commit qui **cite le baseline de tests chiffré**. Les gros artefacts exclus restent sur disque avec leur `sha256` consigné dans un `MANIFEST.txt` versionné.
- **Un critère d'arrêt déclenché arrête le travail même s'il est mal calibré.** Constater le déclenchement, expliquer la décomposition chiffrée, puis rendre la décision au créateur (garder / assouplir / `git checkout --`). Ne jamais réécrire son propre seuil en silence pour pouvoir continuer.
- **Compter les fichiers que le scanner retient avant de conclure sur un changement de découverte**, et vérifier qu'aucune feature ne disparaît sans être nommée (`FakeController` = fixture de test, disparition correcte).
- **« Ça marche » exige de distinguer réel et simulé.** Des tests verts et un HTTP 200 ne prouvent rien si le handler est un stub : chercher les commentaires « In production, this would… », les réponses canoniques (`Response based on <school> perspective:`), et les credentials placeholder (longueur anormale : 15 caractères pour un account Cloudflare). Un audit se termine par une section explicite **« ce qui n'a pas pu être vérifié »** (backend LLM éteint, exécution bloquée) — jamais par une affirmation globale de bon fonctionnement.

## Durabilité, reproductibilité & honnêteté des artefacts

- **Un image Docker qui `COPY` le code n'a aucun bind mount : rebuild obligatoire avant toute vérification.** Sinon le conteneur sert l'ancienne révision et les routes récentes répondent 404. Contrôler `docker images life-mean-dashboard:local --format "created={{.CreatedSince}}"` **et** `docker ps` (`Up … (healthy)`) avant de conclure ; un `docker compose up -d` sans `build` est un test de l'image précédente.
- **La durabilité se prouve par un restart, pas par un test.** Un test sur `tmp_path` valide le code, pas le câblage volume + réhydratation : créer un run via l'API, `docker compose restart dashboard`, puis relire `GET /api/experiments` (run présent, `rehydrated: true`, statut final) et `GET /api/experiments/{id}/manifest` (200).
- **Un manifeste rehydraté porte ce qui a été persisté, et déclare ce qui n'a jamais existé.** Le summary de run contient désormais un bloc `observability` (agents, events ≤ 500, traces ≤ 200) plus `totals`/`truncated`/`limits` ; après restart le manifeste et `/observability` servent la même forme qu'un tracker vivant avec `rehydrated: true` et une note qui chiffre le restauré (« 2 of 2 events, 0 of 0 traces »). Une liste vide sans explication est un défaut : si le build ne produit pas une donnée, le payload porte `traces_absent_reason` — jamais un tableau vide qui laisse croire à une perte de fichier.
- **Un correctif de pipeline se prouve en A/B sur le même seed.** Rejouer exactement le même seed avant/après et comparer les artefacts : `pass_rate` (0.333 → 1.0 ici) puis les lignes du RAW (`answer`, `ground_truth`, `valid`, `error`). Un run différent ne prouve rien.
- **Une tâche non servie doit échouer explicitement, jamais répondre `None`.** `answer=None` confond « aucun outil ne couvre cette tâche » et « mauvaise réponse ». Lever une erreur porteuse d'un code (`UNSUPPORTED_TASK` / `NO_ANSWER`) et la faire atterrir dans le résultat sérialisé, donc dans le RAW.
- **La détection doit couvrir chaque famille que le générateur produit.** Toute famille ajoutée au générateur exige un motif dans `detect_tool` **et** une entrée `DOMAIN_MAP` ; vérifier par `detect_tool("<exemple réel>")` pour chaque famille avant de déclarer la couverture, sinon la tâche part en `None` silencieux.
- **La vérité terrain du générateur prime sur le défaut de l'outil.** Lire comment le générateur calcule `ground_truth` avant de brancher un outil : `log(28)` vaut `math.log` (naturel, 3.332205), un défaut `log10` donnait 1.447 sans erreur visible. Passer la base/les unités explicitement plutôt que s'appuyer sur un défaut.
- **Le README est une surface d'affirmations : chaque compteur et chaque endpoint se vérifie avant publication.** `grep` la route dans le handler, `curl` l'API vivante, compter les objets réels. Un README périmé annonçait 713 tests, un endpoint `/api/experiments/{id}/raw` inexistant et « 22 outils » pour 60.

Recettes complètes (création d'un run via l'API avec CSRF, contrôle après restart, champs du manifeste, A/B même seed, audit des affirmations du README) : `references/durability-reproducibility.md`.

## Packaging : éditer `pyproject.toml` ne suffit pas

- Le finder editable (PEP 660, `__editable__*.pth` + `__editable___*_finder.py`) est **généré à l'installation** : ajouter des motifs à `packages.find.include` ne rend pas les paquets importables. Après édition, rejouer `pip install -e . --no-deps --no-build-isolation`, puis vérifier l'import **depuis un autre cwd** (`cd "$LOCALAPPDATA/Temp" && python -c "import feature_pool, life_mean_studio"`). `--no-deps` évite de faire bouger l'environnement.

## Baseline de tests du dépôt (2026-11-01, à re-vérifier avant de conclure)

`pytest tests -q` → **1797 passed, 13 skipped, 0 failed, ~360 s** (dernier relevé ; `tests/` + `pipeline_inspector/tests` font ~1806. Les blocs ci-dessous décrivent l'état historique pour comprendre les régressions déjà corrigées). Vérifier le compte réel avant de citer un chiffre dans un commit ou un README. Groupes historiques de la baseline : 5 `test_autopilot_llm_adapter` (LM Studio éteint, échouent au lieu de `skip`), 16 `test_workspace_ui` (`experiments/ui/workspace.{html,css,js}` absents), 4 `test_error_memory` (`code_lab/error_memory.py` vide), 1 `test_phase7_weakness` (`KeyError: 'domain'`), 1 `test_qa_fixes` (DELETE 403 vs 200 : CSRF obligatoire), 1 `test_dashboard_ui` (alias `el` disparu du dashboard.html), 1 `test_code_lab_visibility`. Tests par paquet : studio 110, sentinel 31, pipeline_inspector 27, feature_pool 9 (13 depuis l'ajout des 4 tests de découverte). **Trois exécutions indépendantes ont donné les mêmes comptes** (434,17 s / 439,30 s / 437,03 s) : c'est un baseline reproductible, pas une photo. Les 5 échecs `test_autopilot_llm_adapter` sont **environnementaux** (LLM local non joignable depuis le test) et devraient `skip` au lieu d'échouer ; ne pas en conclure « LM Studio éteint » — il peut tourner et exiger un jeton (`An LM Studio API token is required`), ce qui est un 401 et non un serveur arrêté.

## Test commands reference
```bash
cd /c/Users/celes/Documents/Hermes-Workspace/Life_mean
uv run pytest tests/test_sentinel.py -v
uv run pytest tests/test_turn_model_provenance.py -v
uv run pytest -q
```
