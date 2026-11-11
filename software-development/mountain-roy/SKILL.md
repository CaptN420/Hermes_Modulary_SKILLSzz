---
name: mountain-roy
category: software-development
description: Use when working on Mountain_Roy (Python/Pygame RTS).
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pygame, rts, game-dev, units, missions]
    related_skills: [pygame-debugging, pygame-asset-generation, python-venv-setup]
---

# Mountain_Roy (Python/Pygame RTS)

Project: `C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy`. French-speaking user; concise French replies. Values verified working code over explanations.

## Running tests (critical)
System `python` has NO pytest. Always use the venv:
```bash
./.venv/Scripts/python.exe -m pytest tests/ -q
```
Add `tests/<file>` to target one file. Never pipe pytest output through `tail` if you need the real exit code.

## Test conventions
- Every test module must `pygame.init()` + `pygame.display.set_mode((100,100))` BEFORE importing `core.game` / entity modules (else font/surface errors).
- Mirror the existing pattern: `from core.game import Game; g = Game(); g._apply_faction("human"); g.state="playing"`.
- Avoid calling `g.update(dt)` in tests (touches too many systems). Call the specific method under test (e.g. `_can_produce_unit`, `_check_victory_defeat`).
- For AI tests, feed `SimpleNamespace` ghost games (units/buildings/enemy_economy/resource_nodes/movement_system recorder) instead of full Game.

## Hard-won facts (do not regress)
- **Harvest is TIMED**: worker only harvests when `harvest_progress >= 1.0` (accumulates `dt*speed`; ~1s). A single `update(0.016)` yields nothing. Tests must loop frames until the worker carries/deposits. Mining research doubles `max_carry` (15→30), i.e. more gold per completed cycle, not faster frame.
- **`create_unit` assigns `.game` AFTER construction** (subclass `__init__` signatures are `(x,y,faction)` and reject `game=`; `Unit.__init__` accepts `game=None`). Pass `game=self.game` to give new units the reference for synergies/harvest.
- **`Unit.to_dict()` must stay on the base**: `Worker.to_dict` (and buildings) call `super().to_dict()`. Removing it breaks ALL save/load + integration tests at once.
- **AI filters**: `_enemy_workers()` (unit_type worker/builder) gathers; `_enemy_combat()` fights. Combat units have `target=None` by default, so `u.target is None` is NOT a valid worker filter. Workers must never be ordered to attack.
- **Victory/defeat** lives in `Game._check_victory_defeat()`. Defeat = 0 player buildings. **Victory = the enemy's TOWN HALL (main base) is destroyed** — NOT a total wipe. The AI re-produces/re-builds permanently, so '0 enemy units AND 0 buildings' was unwinnable. The AI never rebuilds a town_hall, so destroying the base is the achievable win; on mission advance, surviving enemies are purged before `initialize_enemy_base()` spawns the next base.
- **`survive` objective**: assign `objective.current = int(mission_timer)` directly. NEVER `objective.update(...)` — that ADDS the amount each frame and completes a 120s survive in seconds.
- **`get_max_population`** = `10 + 5*farm_count`. AI production capped the same way.
- **Faction prereq order**: `_can_produce_unit` checks `faction.can_produce` (building/tech prereq) BEFORE the population check — add a Barracks in tests that must reach the population gate.
- **Per-mission enemy setup**: `EnemyAI.initialize_enemy_base(config=None)` reads `current_mission.enemy_config` (else `DEFAULT_ENEMY_CONFIG`): town_hall/barracks/farms/collection/towers/workers/warriors + starting gold/wood/food. `Mission.enemy_config` is serialized in to_dict/from_dict. `create_default_campaign()` scales difficulty (warriors 3→5→7→9).
- **Mission time limit**: `Mission.time_limit` (seconds, 0 = unlimited, serialized). `Game._check_victory_defeat()` checks it FIRST (before building loss): `mission_timer >= limit` → defeat + `mission.fail()`. Opt-in; default campaign missions have no limit.
- **Time acceleration**: press [G] in playing state to cycle `Game.time_scale` through `TIME_SCALES=(1,2,4,8,16)`. `run()` calls `update(dt * effective_dt)` — everything (gathering, production, mission clock) speeds up. Guarded methods: `_cycle_time_scale`, `set_time_scale` (rejects invalid), `effective_dt`.
- **NEVER rebind `self.units`/`self.buildings` with `=`** — `ConstructionSystem(units, buildings)` (and movement/collision/production) hold the ORIGINAL list references from `__init__`. `produce_worker` appends to construction_system.units; if it points at a stale list the worker never shows up in game.units (resources debited, nothing spawned). Filter/reset with SLICE ASSIGNMENT `self.units[:] = [...]` instead of reassignment. Guard: `assert g.construction_system.units is g.units`.
- **`Hero` MUST set `unit_type`** (now `'hero'`). `Hero` subclasses `Unit` and vious code accessed `unit.unit_type` unguarded (right-click mine, `get_synergy_bonus`, construction filters) → `AttributeError` crash. Rule: never add a new Unit subclass without setting `unit_type`; and any new code reading `u.unit_type` on arbitrary units should use `getattr(u, 'unit_type', '')`.
- **Hero is NOT free anymore** — no Hero spawned at game start (`self.hero = None`). Each faction builds a `hero_hall` (registered: BASE_BUILDING_COSTS, footprint, factory, BUILDING_INFO, every faction's building roster), selects it, presses [H] → `Game._recruit_hero()` spawns/revives the hero for `HERO_RECRUIT_COST` (250g/100w), or later resurrects a dead hero keeping level/XP. Hero skills/keys are guarded by `and self.hero`.
- **`Unit.take_damage()` applies armor ONCE itself** — callers must pass RAW damage and must NOT pre-subtract armor (`damage - target.armor` then pass it = DOUBLE armor). Fixed in `Unit.update` (synergy), `Worker.update`, `CombatSystem.attack`. Also: dead units are purged from BOTH `self.units` AND `self.selected_units` in the death loop — a dead selected hero must not linger (HUD drew its skills).
- **3 heroes/faction coexist** (warrior/mage/archer, data-driven in `entities/hero_types.py`): summon from a selected hero_hall with keys 1-3 (or H = first), each costs + no duplicate of a living hero. Skills (Space/Q/E) act on the SELECTED hero; victory XP goes to all living player heroes. Enemy AI builds a hero_hall and summons its 3 (side=enemy). HUD shows the summon panel (names/costs/keys/status) when a hero_hall is selected.

## Synergy system (recent refactor)
`Unit.get_synergy_bonus(game)`: archer `range_mult 1.2` when a friendly wall/tower is <128px; knight `damage_mult 1.15` with 2+ friendly knights <64px. Applied in `Unit.update` using `self.game`.

## Balance (audit 2026-09-21)
- **Ranged units were 3x underpowered vs melee per cost** (eff DPS*EHP/cost ~10 vs warrior ~33). Fixed: Archer dmg 12->16 + atkspd 1.2->1.0 (DPS 16), Mage dmg 30->40 + atkspd 2.0->1.6 (DPS 25). Ranged now out-DPSes warrior — that's their identity (glass cannon + range), DON'T nerf back to parity on the crude eff metric (it ignores kiting/range value).
- **Orc 'all' modifier was +25% dmg/+15% hp on every unit** (strongest faction, ~27% over human). Now dmg 1.15/hp 1.10, warrior-specific 1.2. Orc identity = cheap aggressive melee + slow harvest (max_carry -5), not raw stat inflation.
- Eff metric overvalues armor/EHP (dwarf warrior reads 48 = tanky but slow, that's intended). Use it for relative comparison, not absolute targets.

## Améliorations (2026-09-22)
- **Animations de sprites** : unités dessinées en sprites animés (pas des cercles). `systems/sprite_anim.py` = `SpriteAnimator` singleton (`get_animator()`) + états `ANIM_IDLE/WALK/ATTACK/DEATH` + `FRAME_COUNTS/FRAME_FPS`. `Unit` a `anim_state/anim_frame/anim_timer/facing`, mis à jour dans `_update_animation(dt)` (appelé depuis `update`). `Unit.draw` utilise l'animator (fallback `_draw_circle`). Nécessite `unit_type` — jamais ajouter de sprite sans type. Worker/hero : générateurs `generate_worker`/`generate_hero` dans sprite_generator (le générateur scout a été restauré ; attention aux delete de blocs).
- **Audio** : `systems/audio.py` (actif, `sounds.py` = code mort). `AudioManager` + `AudioEvents` + `SoundGenerator` (procédural). Ajout : `generate_music_loop()` (arpège mineur), `start_music/stop_music` (Channel 0, ne coupe pas les SFX). Game attache `audio_events` : `on_unit_hit` appelé dans `Unit.take_damage`, `on_victory/on_defeat` dans `_check_victory_defeat`, musique synchronisée dans `_sync_music()` (appelé en tête d'`update`, pas seulement si `playing`).
- **Difficulté** : `Game.difficulty` = easy/normal/hard. `DifficultyMenu` (ui/menus.py) entre faction et campagne (état `difficulty_select`). `_apply_difficulty()` scale `current_mission.enemy_config` (warriors/workers/farms/towers/gold/wood) + boost ressources joueur en easy ; appelé dans `_start_campaign` ET après `start_next_mission` (sinon les missions suivantes perdent le scaling).

## IA ennemie : développement continu (2026-09-22)
L'IA est maintenant PROACTIVE et se développe, au lieu de rester figée. Changements clés dans `systems/ai.py` :
- `_set_development_targets()` : cibles par difficulté (`self.dev` = workers/army/barracks/towers, `dev_interval` plus rapide en hard).
- `update()` : boucle d'appel `_develop()` en continu (cadence `dev_interval`), indépendante de l'état tactique. `_choose_state()` a maintenant un état `develop` et attaque dès que `enemy_combat >= dev["army"]` (plus besoin de dominer 1.5x).
- `_produce_workers()` : produit plus de workers depuis le town_hall (économie qui grossit). PAC : il faut `worker.game = self.game` pour la récolte, réserve d'or ≥120, et ne pas dépasser le cap de pop.
- `_try_place(btype, cls)` : placement de bâtiment près du town_hall avec `validate_build_position` + débit du coût. Helpers : `_build_farms_as_needed` (cap pop ≥80%), `_build_extra_barracks` (jusqu'à dev[barracks]), `_build_towers` (si ≥2 unités de combat).
- `building_costs` inclut désormais `farm`. Les tests ghost du dev AI fournissent `construction_system.validate_build_position=lambda: (True,"")` + `economy.get_max_population`.

## IA ennemie : agressive + tactique (2026-09-22)
Rafraîchit l'IA pour qu'elle soit plus agressive et fasse vraiment la guerre :
- `self.dev` a maintenant une clé `garrison` (unités gardées en défense pendant l'attaque) : easy 2 / normal 2 / hard 3.
- `_choose_state` attaque dès `enemy_combat >= aggr_threshold`, seuil = ~2/3 de `army` en normal/hard (`max(3, int(army*0.66))`), cible pleine en easy. `self.state != "defend"` est conservé pour ne pas abandonner la défense sous siège.
- `_attack_player` est TACTIQUE : `_strategic_player_target()` choisit UNE cible commune — priorité bâtiment de production joueur (barracks/workshop/*_barracks/academy/dock), sinon hôtel de ville, sinon bâtiment, sinon unité joueur, le tout via `_dist_to_army` (ancré sur la 1re unité de combat ennemie). Toute l'armée est ordonnée sur cette cible (concentration, plus d'éparpillement). Garnison gardée via `_enemy_base_pos()` (position du town_hall).
- Tests ghost : `_game()` accepte `units=` et `buildings=` (pas `workers/combat_units` si fournis), et fournit `movement_system` (RecordingMovement) — nécessaire car `_attack_player` passe par `_order_attack`, qui vérifie `hasattr(game, 'movement_system')`.

## IA ennemie : escalade + défense des ressources (2026-09-22)
2 problèmes réglés : (1) l'IA plafonnait (~18 unités) et ne pouvait rivaliser avec un joueur qui amasse des workers/armée ; (2) elle ignorait les raiders de workers qui drainaient les mines/forêts. Choses à retenir :
- **Cibles SCALING** : `_army_target()` / `_worker_target()` = base (`self.dev`) + croissance au fil du temps (`mission_timer`) : armée +1 par 30s (plafond easy 20 / normal 34 / hard 50), workers +1 par 45s (plafond 24). `getattr(self.game, "mission_timer", 0)` retourne 0 hors jeu. `self.dev` reste la BASE (workers 7/10/14, army 6/8/12, garrison 2/3/4, barracks 2/3/4, towers 3/4/6).
- **`_develop()`** : sous la moitié des workers → worker ; sinon `_produce_units()` (qui retourne maintenant **bool** : True si produit) jusqu'à `_army_target()` ; si rien produit (cap de pop) → `_build_farms_as_needed()` pour lever le cap ; complète les workers ; puis fermes/casernes/tours ; excédent → armée au-delà de la cible.
- **`_build_farms_as_needed()` construit PROACTIVEMENT** (avant d'atteindre le cap) : construit une ferme tant que `max_pop < workers_target + army_target + 6` (capé à 70). C'est ce qui permet à l'armée de grossir avec l'escalade. AVANT elle attendait pop >= 80% du cap = deadlock (armée bloquée).
- **`_player_raiding_resources()`** : détecte un worker/builder joueur dont `target_resource` est un node NON épuisé à <600px de la base ennemie. `_choose_state` passe en `defend` si des raiders drainent les ressources locales (sinon le joueur épuise toutes les mines). Utilise `_enemy_base_pos()`.

## Mode Sandbox (mode libre) (2026-09-22)
- Bouton **"Mode Libre"** dans le menu principal → `main_menu.handle_event` retourne `"sandbox"`. Flow : `Game._sandbox_pending=True` → `faction_select` → `_start_sandbox()` direct (pas de difficulté).
- **`_start_sandbox()`** : `self.sandbox=True`, `current_mission=None`, `_apply_faction`, ressources généreuses (800 or / 600 bois / 300 nourriture), purge TOUTE entité ennemie par **slice assignment** (`units[:]`/`buildings[:]`/`construction_sites[:]`), `ai.state="idle"`, `state="playing"`.
- Neutralisations dans `Game.update` : `if not self.sandbox: self.ai.update(dt)` → l'IA ne joue pas. `_check_victory_defeat` retourne tôt si `sandbox` → aucune victoire/défaite même si tu détruis toute la base.
- Pas de crash : `_update_mission_progress`, `_check_mission_objectives`, `_draw_mission_hud` sont toutes gardées par `if not self.current_mission` (None en sandbox). `_draw_mission_hud` est du code mort (jamais appelé).

## Profondeur + minimap/groupe (2026-09-22)
- **Techs toutes fonctionnelles** : `game._RESEARCH_EFFECTS` couvre maintenant TOUTES les techs de `TechTree._TECH_DEFS` (avant `gunpowder`, `orc_warpath`, `woodland_craft`, `master_armor`, `hero_training`, `siege_weapons`, etc. n'avaient AUCUN effet). Nouveaux types d'effets dans `_apply_one_research_effect` : `attack_speed_percent` (**<1 = plus rapide**), `speed_percent`, `max_hp_percent`, `worker_speed`. Techs de déblocage pur (`siege_weapons`, `ultimate_skill`, `hero_training`) = effet `{}`.
- Nouvelles techs : `rapid_weapons` (pre-req iron_working, atk_speed -12%), `mounted_speed` (heavy_armor, +20% speed), `veteran_bulk` (iron_working, +12% PV), `scout_sight` (archery, +20% portée), `rapid_workers` (libre, workers 25% plus vite via `worker_speed` qui booste `base_harvest_speeds`/`harvest_speeds`), `siege_power` (siege_weapons, +20% dégâts).
- **`_apply_research_effects_to_unit(unit)`** : applique les bonus de recherche à une unité PRODUITE APRÈS la recherche (les unités existantes les reçoivent au moment où la recherche se termine). Appelé dans `update` après `production_system.update` spawn (à côté de `apply_unit_modifiers`). Sans ça, une unité produite après la soulée n'avait pas les bonus de dégâts/armure/etc déjà recherchés.
- **Minimap cliquable** : `HUD.minimap_rect()` expose le rectangle ; `Game._handle_minimap_click()` recentre la caméra (clic gauche prioritaire avant sélection). `Camera.move_to(x,y)` existe.
- **Groupes de contrôle** : `Game.control_groups` (dict int -> [units]). `Ctrl+1..9` = assigner la sélection (`_assign_group`), `1..9` seul = rappeler (`_select_group`, filtre les morts, recentre caméra). `_handle_group_keys(event)` gère le clavier ; touche simple ne capte que si AUCUN bâtiment sélectionné (sinon 1-6 = production). Mapping via `_group_key_for`. Ne PAS rebind les unités dans control_groups (références) — on re-filtre `is_alive()` au rappel vs la liste.

## Système de défense corrigé (2026-09-22)
GROS bug corrigé : les tours (`tower`) avaient `damage`/`range` mais AUCUN système ne les faisait tirer, et les murs (`wall`) ne bloquaient pas le pathfinding. Maintenant :
- **Tours qui tirent** : `Game._update_defenses(dt)` appelé en fin d'`update`, boucle sur les bâtiments `tower` vivants et appelle `_tower_fire(tower, dt)`. `_tower_fire` cible l'ADVERSAIRE du `tower.faction` le plus proche à portée (`tower.range`=128, dmg=20), cooldown 1s via `tower.attack_timer` (initialisé dans `Tower.__init__`). Applique `take_damage` + particule. Les tours ennemis tirent donc aussi sur le joueur.
- **Murs qui bloquent** : `Pathfinder` a maintenant `blocked_cells` (set de tuiles (x,y)) + `set_blocked/add_blocked/remove_blocked`. `_is_valid_tile` refoule les cellules bloquées. `_update_defenses` recalcule le set à chaque frame à partir des murs vivants (`b.hp>0`) → un mur construit bloque, un mur détruit libère. ATTENTION : murs bloquent TOUS les camps (défense des deux côtés).
- Construction défense : `tower`/`wall` sont déjà dans les rosters de toutes les factions + `BASE_BUILDING_COSTS` (pas besoin de les ajouter).

## Layout
`core/game.py` (Game), `entities/` (Unit, Worker, Hero, unit_types w/ `create_unit`, building, resource_node), `systems/` (ai, construction, economy, faction data in factions.py, campaign, fog_of_war, combat), `ui/` (hud, menus), `map/`, `tests/` (pytest). Design history in `TAPE_*.md` and `*.md` audit notes at repo root.
