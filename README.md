# Hermes Skills — profil `def`

17 skills maison pour Game On Terminal, PyGame, modulary architecture, Multi AI Framework, experimental et outillage QA/dev.

                          ## Installation ##


# PROMPT — Recréer le bundle complet des 17 skills maison (profil Hermes `def`)

Copier-coller ce prompt tel quel dans une session Hermes fraîche (même machine, même utilisateur)
pour régénérer le bundle de skills développé sur les projets PyBR0S, Mountain_Roy, Life_mean,
CaptN-BRAIN et l'outillage QA/dev.

---

## RÔLE

Tu es un agent Hermes qui doit reconstruire un bundle de skills procéduraux à partir de la
spécification ci-dessous. Tu écris des skills, pas de la documentation décorative : chaque skill
encode des faits durement gagnés (chemins exacts, commandes exactes, pièges reproductibles) pour
qu'une session future ne réapprenne pas les mêmes bugs.

## CIBLE ET CONVENTIONS

- Racine des skills : `C:\Users\celes\AppData\Local\hermes\profiles\def\skills\`
- Un skill = un dossier + `SKILL.md` (+ `references/`, `scripts/`, `templates/` si listés).
- Frontmatter YAML obligatoire :
  ```yaml
  ---
  name: <slug-kebab-case>
  description: <≤120 caractères, format "Use when ... . <comportement>.">
  category: <software-development|game-dev|autonomous-ai-agents>
  version: 1.0.0
  author: Hermes Agent
  license: MIT
  metadata:
    hermes:
      tags: [ ... ]
      related_skills: [ ... ]
  ---
  ```
- Ne PAS recréer les ~60 skills bundled (hermes-agent, github, systematic-debugging, dogfood,
  p5js, microsoft-office, etc.) : ils reviennent avec l'installation Hermes et sont listés dans
  `.bundled_manifest`. Seuls les 17 skills ci-dessous sont maison.
- Langue : français pour les skills de projet (utilisateur francophone), anglais acceptable pour
  l'outillage générique. Ton concis, impératif, une règle par leçon.
- Chaque skill projet commence par : chemin du projet + « utilisateur francophone ; réponses
  concises ; valeur = code vérifié qui fonctionne ».

- La `description` sert au **routing** : elle doit contenir la techno, le symptôme et le nom du
  projet (« Debug Pygame apps: fog of war, state flow, DPI issues »). 120 caractères est un
  plafond, pas un objectif : ne jamais la mutiler pour tenir 60.

## MODE D'EXÉCUTION

Exécute sans demander de confirmation : écris les fichiers, ne rapporte qu'à la fin.
Procède en 5 passes, avec un `skills_list()` de contrôle après chacune (ne charge pas les 17
d'un coup dans un seul raisonnement) :

- **Passe 1 — jeu PyBR0S** : skills 1 → 4
- **Passe 2 — RTS + environnements** : skills 5 → 6
- **Passe 3a — Life_mean (la plus lourde)** : skills 7 → 9 — `life-mean` (+6 references),
  `life-mean-recent-lessons` (+6 references, 1 script), `life-mean-dashboard-qa`.
  Un skill à la fois : `SKILL.md` d'abord, puis ses references ; ne pas garder les 17 specs en tête.
- **Passe 3b — CaptN / Mia_Brain** : skills 10 → 13
- **Passe 4 — outillage transverse** : skills 14 → 17

Si le contexte sature en cours de passe : termine le skill en cours, puis reprends à la frontière
suivante. Ne laisse jamais un skill à moitié écrit — un skill partiel est pire qu'un skill absent,
il sera chargé et trompera la session suivante.

Si un fait d'une spec paraît faux ou incohérent avec le disque, ne bloque pas et ne demande rien :
écris-le tel quel et liste l'écart dans le rapport final. Un skill écrit avec un écart signalé
vaut mieux qu'un bundle à moitié créé.

## RÈGLES D'ÉCRITURE (non négociables)

1. Pas de narration de session, pas de date de réunion : seulement la règle + le POURQUOI.
   Exception unique : un skill « lessons log » (dont la description l'annonce comme journal daté)
   est daté par section — c'est sa valeur, et il est destiné à être archivé, pas à durer.
2. Tout fait doit être vérifiable : chemin, commande, valeur numérique, nom de fonction.
3. Signaler explicitement les pièges « ça a l'air cassé mais c'est un test obsolète » et
   « ça passe en test unitaire mais échoue en jeu » (les deux classes de faux diagnostics).
4. Séparer : faits projet (chemins/constantes) → skill projet ; oracle technique réutilisable
   (pygame, FastAPI, venv) → skill outillage ; leçons datées d'une campagne → skill « lessons ».
5. Un skill ne dépasse pas ~320 lignes ; au-delà, découper en `references/<sujet>.md`.

## ORDRE DE CRÉATION (dépendances d'abord)

1. `pybr0s` → 2. `sprite-management` → 3. `pygame-asset-generation` → 4. `pygame-debugging`
→ 5. `mountain-roy` → 6. `python-venv-setup` → 7. `life-mean`
→ 8. `life-mean-recent-lessons` → 9. `life-mean-dashboard-qa`
→ 10. `snapshot-logic-architecture` → 11. `captn-brain` → 12. `team-coding-workflow`
→ 13. `autonomous-decision-engine` → 14. `dogfood-python` → 15. `python-fastapi-apps`
→ 16. `python-terminal-games` → 17. `hermes-cron-jobs`

---

## SPÉCIFICATIONS

### 1. `pybr0s` (catégorie game-dev)
Description : `Use when working on PyBR0S (Python/Pygame 2D fighting/RPG).`
Projet : `C:\Users\celes\Documents\Hermes-Workspace\PyBR0SVARCHITECTURE-master` (v1.3).
Sections obligatoires : Architecture Notes (audit), Hard-won facts, Running tests,
Verifying sprite/VFX rendering headless, File structure, Pitfalls, World Prototype Integration,
Autonomous Mode, Related Skills.
Faits durs à conserver :
- Dette : `GameBaseMixin` = 864 lignes / 12+ managers (god class) ; Player/Enemy ~70 % dupliqués ;
  valeurs d'équilibrage éparpillées (`config.py`, `settings.py`, `combat_balance.py`) ;
  roguelite/perks/equipment non testés. Bons patterns à préserver : `ManagerRegistry`,
  `EventSystem`, design data-driven.
- Skins par classe : `core/sprite_animator.py`, `get_player_animator(class_name)` lazy + cache,
  `.upper()` normalisé ; Knight→Samurai, Rogue→Martial Hero 2 (fallback), Mage→Martial Hero,
  Heavy→StaticAnimator, inconnu→Rogue (jamais None). États idle/run/attack1/attack2/hurt/jump/
  fall/death, fallback idle. Ennemis = Ice Golem via `StaticAnimator`. Rect 40x60 inchangé,
  ancrage bottom-center, flip par `facing`, fallback rectangle.
- Règle asset : ne modifier QUE le rendu/audio ; jamais hitbox, dégâts, save, balance.
  Suite 367 tests verte AVANT et APRÈS.
- Combat : `DamageSystem.apply_damage(target, dmg, direction)` attend une direction SCALAIRE
  (un Vector2 casse `apply_knockback`) ; l'armure absorbe AVANT les HP → un coup < ~30 armure
  laisse les HP intacts (faux négatif ; tester avec damage > armor) ;
  `ComboSystem.on_hit(attacker, defender)` exige les deux arguments.
- Journal de bugs B1–B11 à résumer en règles : import local conditionnel → UnboundLocalError ;
  save `coins` vs lecture `gold` (or perdu au load) ; `ARMOR_REGEN_RATE` 4.0 → softlock, fix 1.0 ;
  `apply_phase_2_damage(entity, damage, ko_threshold=250)` ; `SLOT_TO_CATEGORIES` centralisé
  (ring→ring1/ring2, amulet→amulet1/amulet2) ; garde `current_attacker` dans `on_hit` = code mort
  qui plafonnait le combo à 1.1, plafond aligné 2.5→3.0 ; tests de balance obsolètes → mettre à
  jour les tests, pas le design (HP 500, armor 250, regen 1.0, delay 2.5) ; save lit
  `p.equipment_manager` + dual-write `equipment`/`equipped_gear` ; rage jamais activée
  (`rage_threshold` 80) et knockback hors contrat documenté.
- Tests : monkeypatch `pygame.event.wait = lambda t=0: pygame.event.poll()` AVANT `import pygame`,
  sinon `Game.__init__` (game_base.py:221) se fige en driver dummy. Utiliser un script loader,
  pas `python -m unittest discover`. Python système 3.14 sans pygame → venv Hermes.
- Vérif headless : `Game` → `set_state(PLAYING)` → `ensure_player()` → `draw()` ; position via
  `g.cam.apply(p.rect)` (caméra non mise à jour hors boucle → offset 0, zoom 1) ; compter les
  pixels ≠ fond `(20,20,20)` / plateforme `(100,200,100)` ; sauver et agrandir x4 avec clamp du
  subsurface ; tester le fallback en renommant le dossier ; vérifier `p.rect` toujours 40x60.
- Intégration world prototype : `GameState.WORLD`, `self.world_manager=None`, `_enter_world()`,
  `_update_world(dt)`, `draw_world_screen()`, touche debug, ESC → TITLE. Mode autonome :
  flag `self.autonomous`, `_autonomous_input()`, `_autonomous_advance()`,
  remplacement de `self.ctrl.get()` dans game_loop, arg CLI `--autonomous`,
  `SDL_VIDEODRIVER=dummy` pour le headless.

### 2. `sprite-management` (game-dev)
Description : `Load and render sprite sheets for PyBR0S characters`
Contenu : `core/sprite_manager.py` ; feuilles 96x128 = 3x4 frames de 32x32 ; boss 288x384 = 9x12 ;
crop premier frame `(0,0,32,32)` via PIL → surface alpha ; taille cible
`max(60, w*1.5) x max(80, h*1.5)` ; centrage, flip par facing, hitbox 40x60 inchangée ;
issues : artefacts multi-sprites (crop raté), sprites trop petits (facteur d'échelle),
mauvais alignement (calcul de centre).

### 3. `pygame-asset-generation` (software-development)
Description : `Generate pixel art sprites for Pygame games; source free/CC0 external assets.`
Sections : Procedure (structure `assets/sprites`, génération PIL, SpriteManager, venv Windows,
intégration renderer), Pitfalls, Mountain_Roy RTS Specifics, PyBR0S Game Flow, References.
Faits durs : venv Windows via python du hermes-runtime (`cpython-3.11.16`) car le python par
défaut crée un venv Linux ; `from PIL import Image` ; fallback rectangle obligatoire ;
`CLASS_SKINS` capitalisé vs `rpg.class_name` minuscule → `.capitalize()` ; `reset_game()` doit
préserver la NOUVELLE classe ; pièges Mountain_Roy (lambda dynamique avec self, `on_building_built()`
et non `on_build()`, `display.flip()` manquant, caméra float → `int()`, DPI, réutilisation de
`display.get_surface()`) ; flux de menus Start→Class→Map→Play / Load→Map→Play.
Fichiers liés : `references/sprite-palette.md`, `references/free-asset-sourcing.md`,
`references/pygame-sprite-animation.md`, `scripts/itch_download.py`,
`templates/sprite_generator.py`.

### 4. `pygame-debugging` (racine)
Description : `Debug Pygame apps: fog of war, state flow, DPI issues.`
**Budget : `SKILL.md` ≤ 320 lignes** (état de référence après découpage : 162). Répartition :
- `SKILL.md` : Quick Reference (symptôme → cause probable) + 7 règles actionnables
  (une règle = une cause + un correctif) + 5 pièges génériques Pygame. Pas de récit.
- `references/mountain-roy-pitfalls.md` : l'oracle de bugs extrait de l'ancien SKILL.md
  (symptôme → cause → correctif → leçon : récolte, mouvement, mêlée, XP, HUD, signatures).
- `references/mountain-roy-workflow.md` : le cycle de vie des systèmes RTS.
- `references/pygame-dpi-and-window.md` : **optionnel** — seulement si le détail DPI/fenêtre
  dépasse les 5 puces du SKILL.md (sinon il reste inline, pas de fichier pour 20 lignes).
Rôle : oracle transverse Pygame + atelier Mountain_Roy. Quick Reference (écran noir, unités
invisibles, input, fenêtre hors écran, ressources, workers, mouvement erratique, melee qui ne
touche jamais), plus :
- Un seul chemin de mouvement par unité ; un `return` avant le dépôt = worker qui porte à vie.
- `_find_and_assign_to_resource()` : diversifier par type non porté (rayon 1.5x), sinon le plus
  proche ; `max_carry_types` par faction ; dépôt au bâtiment allié le plus proche.
- Séparation de collision (25 + rayons 12 = ~49 px) > range mêlée 32 → coup impossible :
  range 64, test `distance <= unit.range + target.radius`. Diagnostiquer avec `game.update()`
  complet, pas un harnais mouvement seul.
- XP via `killed_by` propagé dans `take_damage(damage, attacker=None)` ; level-up doit restater.
- `hasattr(target,'hp')` avant accès (cibles `BuildingProgress`/`ResourceNode`).
- Surcharge de `draw()` : signature identique au parent, sinon TypeError au dispatch polymorphe.
- Refactor partiel : `git diff --stat` + suite complète AVANT de toucher ; `create_unit` affecte
  `.game` après construction ; restaurer `Unit.to_dict` plutôt qu'inliner ; tests mono-frame
  invalides par une nouvelle temporisation → boucler les frames, ne pas revenir au design.
Fichier lié : `references/mountain-roy-workflow.md`.

### 5. `mountain-roy` (software-development)
Description : `Use when working on Mountain_Roy (Python/Pygame RTS).`
Projet : `C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy`, tests
`./.venv/Scripts/python.exe -m pytest tests/ -q`.
Faits durs (tous à conserver) : `pygame.init()` + `set_mode((100,100))` avant imports ; ne pas
appeler `g.update(dt)` dans les tests ; récolte temporisée (`harvest_progress >= 1.0`, ~1 s) ;
`create_unit` affecte `.game` après construction ; `Unit.to_dict()` doit rester sur la base ;
`_enemy_workers()` vs `_enemy_combat()` ; victoire = town hall ennemi détruit (pas wipe total) ;
objectif survive = `objective.current = int(mission_timer)` en direct ; population
`10 + 5*farm_count` ; `_can_produce_unit` vérifie `faction.can_produce` avant la population ;
`Mission.enemy_config` + `time_limit` sérialisés ; `[G]` cycle `TIME_SCALES=(1,2,4,8,16)` ;
JAMAIS réaffecter `self.units`/`self.buildings` (`[...]` slice assign, sinon systèmes désynchronisés) ;
`Hero.unit_type='hero'` ; héros non gratuit (hero_hall, 250g/100w, résurrection) ;
`take_damage()` applique l'armure UNE fois (passer les dégâts bruts) ; purge des morts dans
`units` ET `selected_units` ; 3 héros/faction (`entities/hero_types.py`) ; synergie
(`Unit.get_synergy_bonus`) ; équilibrage ranged (archer 16 dmg/1.0, mage 40/1.6) déjà corrigé ;
modificateur orc 1.15 dmg/1.10 hp.
Ajouter un tableau des touches (W worker, J builder, B build, 1-6 unités, T recherche, H héros).

### 6. `python-venv-setup` (racine)
Description : `Create and manage Python virtual environments on Windows.`
Procédure venv, activation PowerShell vs bash, pip, vérification, désactivation ; pièges :
terminal = bash (pas PowerShell), `.bat` avec `cd /d` + `-m package.main`, venv Windows vs Linux,
pygame impossible à compiler → wheel précompilée / `pygame-ce` pour Python 3.14,
`SDL_VIDEO_WINDOW_POS/CENTERED/HIGHDPI_DISABLED`, `display.get_surface() or set_mode()`,
`display.flip()` obligatoire, lambda `type()` avec self cassé, `mixer.init()` en try/except.

### 7. `life-mean` (software-development, ~314 lignes + 6 references)
Description : `Use when working on the Life_mean synthetic data lab.`
Projet : `C:/Users/celes/Documents/Hermes-Workspace/Life_mean_realm` (ADSG P0–P12, 501 tests).
Sections : When to Use, Verification rules (always on), Architecture truth, Subject tree
(`compare/subjects.py`), Dashboard Docker data sync (host `data/` → volume nommé), Compare UI
click-flow, Compare V1 (`compare/`), Life_mean Studio PySide6, Life_mean Lab Phase D, Test suite,
Zero-secrets/packaging, Wheel integrity, fichiers vidés, réparations P0/P1 (2026-10-09),
audit terminologique « protocol », provenance RAW du Code Lab, preuves RAW (pass-rates),
timeline lab-wide, cycle de vie AutoPilot/DebateEngine (8d2392a), Debate Lab, Code Lab,
méthodologie d'audit Context-State (lecture seule), cartographie état canonique vs compresseur
(deux mécanismes parallèles NON câblés), pitfall GCM push headless Windows (bypass wincred),
pitfall defaultdict qui mute l'état (verdict dépendant de l'ordre), E2E code-lab doit forcer
`multi_agent=False`, Cluster Graph CG1 (`compare/graph.py`), revue sécurité hermes-orchestrator,
pitfalls, credentials/providers/onglets, process, `experimental/`.
References : `dashboard-api-extension.md`, `docker-and-provider-verification.md`,
`experiment-resume-and-checkpoints.md`, `history-rewrite-secret-purge.md`,
`recovering-emptied-source.md`, `verification-and-audit-discipline.md`.

### 8. `life-mean-recent-lessons` (software-development, ~244 lignes + 6 references + 1 script)
Description : `Journal daté Oct 2026 des leçons Life_mean — temporaire, archivable.`
Nature : **lessons log**, seule exception assumée à la règle « pas de date ». Le frontmatter doit
l'annoncer (« journal daté … temporaire, archivable ») pour qu'un agent sache que le contenu est
périssable : quand une leçon devient une règle durable, la promouvoir dans `life-mean` et la
retirer d'ici.
Leçons une par section, datées, sans narration : Agent Builder (2026-10-31), Historical Thinkers
& Patterns, config du modèle Sentinel, correctif de provenance provider, accès GitHub (Tailscale
bloque le privé), CaptN Runtime v1, Pipeline Inspector & Feature Pool, permissions Docker
(Errno 13), Studio qui « ne fait rien » au lancement, couverture ≠ inventaire, pont déjà existant,
« erreur de permission » = classer le littéral d'abord, orchestrateur vs permissions (deux systèmes
non reliés aux clients), registres d'auto-extension P5 (« total: 0 »), observabilité persistée P6,
« bloqué par une dépendance » (vérifier que le code existe), outils maths (parser, ne pas balayer
les chiffres), onglets/télémétrie hôte, brancher ≠ supporter, journal d'usage runtime, git sur ce
dépôt, « 2 features sur 989 » (fenêtre récente ≠ échantillon), 403 avant lecture du corps =
connexion avortée sous Windows, `inspect.getsource` ment après réécriture, porte de vérification
avant le patch suivant, durabilité/reproductibilité/honnêteté des artefacts, `pyproject.toml`
insuffisant, baseline de tests + commandes.
References : `dashboard-tabs.md`, `docker-run-volumes.md`, `durability-reproducibility.md`,
`feature-pool-discovery.md`, `incremental-ingestion-offsets.md`, `orchestrator-permissions.md` ;
script `scripts/audit-js-blocks.py`.

### 9. `life-mean-dashboard-qa` (racine)
Description : `Use when QA-testing the Life_mean dashboard.`
Cible `http://127.0.0.1:8080/dashboard` ; lanceur canonique `run_server.bat` (tue les listeners
zombies, forward `--host/--port`, `run_server.bat 9099`) ; équivalent
`python -m experiments.dashboard --port 8080` ; durcissement SQL (requêtes paramétrées,
validation des entrées) ; évolution MIA v0 → Life_mean ; gotcha métriques ; procédure QA ;
fichiers.

### 10. `snapshot-logic-architecture` (software-development)
Description : `Use for LearningBus, Snapshot, and Security Gate logic.`
Trois états indépendants (Security Gate = RBAC statique, LearningBus = preuve brute,
Snapshot = pont) ; `BatchProcessor` = compilateur (analyse acquis → diff → Version_Manager
v1.1.a→v1.1.b → `active_snap.json` → rollback vers `snapshots/`) ; schéma unifié
(version, timestamp, context.identity/competencies/constraints, active_roadmap_step,
build_notes) ; autorisation = `Role_Has_Right AND Has_Validated_Competency` ; reconstruction
d'un état passé en réappliquant Gate + Bus.

### 11. `captn-brain` (software-development)
Description : `CaptN-BRAIN CLI, optimisation tokens/contexte temps réel.`
Projet `C:\Users\celes\Documents\Hermes-Workspace\Mia_Brain\CaptN-BRAIN-main`.
Sections : CLI Protocol (la CLI est LA seule source de vérité), principe central
(déterministe d'abord, LLM si nécessaire), wrapper + venv unique point d'entrée, flags globaux
d'optimisation du contexte À METTRE AVANT la commande, commandes temps réel sous `devtools`,
économiseurs de tokens, fichiers clés, pitfalls.

### 12. `team-coding-workflow` (software-development)
Description : `Use when building a multi-role AI coding team pipeline.`
Sections : Architecture (rôles junior/mid/senior/validator), Role Philosophies, Intelligent Turn
Reprise, Validator Gates, Usage, Integration with Code Lab Engine, Pitfalls, Files.

### 13. `autonomous-decision-engine` (software-development)
Description : `Build telemetry-driven decision systems with pattern analysis.`
Sections : Overview, Architecture, Procedure en 6 étapes (decision space, collecte télémétrie,
analyse de patterns, règles de décision, garde-fous de sécurité, journalisation), Decision Rules
Reference, CLI Integration (`captn/cli/_devtools.py`), Verification, Pitfalls, Files Structure.
Principe : les modèles proposent, le système de permissions autorise.

### 14. `dogfood-python` (software-development)
Description : `QA exploratory d'applications Python par exécution réelle.`
Workflow discover entrypoints → scénarios réalistes → varier entrées/config → observer →
inspecter l'état persisté → reproduire → minimiser → rapporter la preuve. Pour chaque issue :
scénario, attendu, réel, commande exacte, traceback, reproductibilité, sévérité, composant
suspect. Règles : exécution réelle > lecture de code ; aucune affirmation sans reproduction ;
ne pas corriger pendant la découverte ; distinguer FAIL/ERROR/INCONCLUSIVE/PASS.

### 15. `python-fastapi-apps` (software-development)
Description : `Use when building or extending a Python FastAPI web app.`
Procédure en 7 points : baseline (suite existante verte + compte), ne pas réécrire le cœur,
SPA servie par la même app (`Mount("/assets")`, `html[data-theme]`), `python-multipart` pour
`UploadFile`, jobs longs en threads daemon avec work-file disque + réindexation paresseuse
(survit au restart), tests à 3 niveaux (unit / `httpx.AsyncClient(ASGITransport)` / E2E uvicorn+browser),
vérifier chaque critère par exécution réelle y compris les chemins d'échec.
Pitfalls : `JSONResponse` écrase `status_code` du décorateur ; `__init__.py` qui shadow un
sous-module (`from . import export as export_mod`) ; `Lock` non réentrant → `RLock` ;
mutateur « no-op silencieux » ; encodage (utf-8 → cp1252 → latin-1 avant détection) ;
TestClient multiples deadlock Windows ; singletons qui fuient entre fichiers de test ;
`write_file` refusé après lecture partielle → `.new` + `mv -f` ; upload CDP
`DOM.setFileInputFiles` + event `change`, polling jamais sleep fixe ; `pip-audit` sort 3
QUAND il trouve des vulnérabilités ; normaliser le vocabulaire de sévérité ; `Mount` sans
`.endpoint` ni `.methods`.
References : `test-harness.md`, `audit-and-validation.md`.

### 16. `python-terminal-games` (software-development)
Description : `Use when building ASCII/terminal games in Python.`
Sections : When to Use, Procedure, Windows console specifics, Pitfalls, Conventions for this user.
References : `headless-testing.md`, `windows-console.md` ; template `launcher.bat`.

### 17. `hermes-cron-jobs` (autonomous-ai-agents)
Description : `Schedule/edit Hermes cron jobs with Discord delivery.`
Commandes de création/édition de cron jobs Hermes, livraison Discord, pièges de planification ;
template `templates/ai-morning-briefing-prompt.md` (briefing matinal autonome).

---

## VÉRIFICATION FINALE

Exécuter et corriger jusqu'au vert :

```bash
cd C:/Users/celes/AppData/Local/hermes/profiles/def/skills
# 1) les 17 dossiers existent
for s in pybr0s mountain-roy sprite-management pygame-asset-generation pygame-debugging \
  python-venv-setup snapshot-logic-architecture life-mean-dashboard-qa; do test -f "$s/SKILL.md" || echo "MISSING $s"; done
# 2) frontmatter valide + description présente
for f in */SKILL.md software-development/*/SKILL.md autonomous-ai-agents/hermes-cron-jobs/SKILL.md; do
  head -1 "$f" | grep -q '^---$' || echo "BAD FRONTMATTER $f"
  grep -q '^description:' "$f" || echo "NO DESCRIPTION $f"
done
# 3) aucun skill vide ou stub
find . -name SKILL.md -not -path './.archive/*' -size -1k
```

Puis `skills_list()` doit montrer **les 17 noms attendus** — verdict par nom, jamais par total
(le nombre de skills bundled varie avec la version d'Hermes installée), chacun avec description et
catégorie. Contrôle de substance : ouvrir
`pybr0s`, `mountain-roy`, `life-mean`, `pygame-debugging` et vérifier qu'on y trouve bien les
faits numériques (864 lignes, 367 tests, 10+5*farms, harvest 1.0, armor 4.0→1.0, 40x60).

## SORTIE ATTENDUE

Un court rapport : skills créés (nom, catégorie, nombre de lignes), fichiers de support
recréés, résultat des 3 vérifications, et tout écart assumé par rapport à cette spécification.
