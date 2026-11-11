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

## Improvements (2026-09-22)
- **Sprite animations**: units drawn as animated sprites (not circles). `systems/sprite_anim.py` = `SpriteAnimator` singleton (`get_animator()`) + `ANIM_IDLE/WALK/ATTACK/DEATH` states + `FRAME_COUNTS/FRAME_FPS`. `Unit` has `anim_state/anim_frame/anim_timer/facing`, updated in `_update_animation(dt)` (called from `update`). `Unit.draw` uses the animator (fallback `_draw_circle`). Requires `unit_type` — never add a sprite without a type. Worker/hero: `generate_worker`/`generate_hero` generators in sprite_generator (the scout generator was restored; watch out for block deletions).
- **Audio**: `systems/audio.py` (active, `sounds.py` = dead code). `AudioManager` + `AudioEvents` + `SoundGenerator` (procedural). Added: `generate_music_loop()` (minor arpeggio), `start_music/stop_music` (Channel 0, does not cut the SFX). Game attaches `audio_events`: `on_unit_hit` called in `Unit.take_damage`, `on_victory/on_defeat` in `_check_victory_defeat`, music synced in `_sync_music()` (called at the top of `update`, not only when `playing`).
- **Difficulty**: `Game.difficulty` = easy/normal/hard. `DifficultyMenu` (ui/menus.py) between faction and campaign (`difficulty_select` state). `_apply_difficulty()` scales `current_mission.enemy_config` (warriors/workers/farms/towers/gold/wood) + boosts player resources on easy; called in `_start_campaign` AND after `start_next_mission` (otherwise the following missions lose the scaling).

## Enemy AI: continuous development (2026-09-22)
The AI is now PROACTIVE and develops itself, instead of staying frozen. Key changes in `systems/ai.py`:
- `_set_development_targets()`: per-difficulty targets (`self.dev` = workers/army/barracks/towers, `dev_interval` faster on hard).
- `update()`: calls `_develop()` in a continuous loop (cadence `dev_interval`), independent of the tactical state. `_choose_state()` now has a `develop` state and attacks as soon as `enemy_combat >= dev["army"]` (no more need to dominate 1.5x).
- `_produce_workers()`: produces more workers from the town_hall (growing economy). GOTCHA: needs `worker.game = self.game` for harvesting, a gold reserve ≥120, and must not exceed the pop cap.
- `_try_place(btype, cls)`: building placement near the town_hall with `validate_build_position` + cost debit. Helpers: `_build_farms_as_needed` (pop cap ≥80%), `_build_extra_barracks` (up to dev[barracks]), `_build_towers` (if ≥2 combat units).
- `building_costs` now includes `farm`. The dev AI ghost tests provide `construction_system.validate_build_position=lambda: (True,"")` + `economy.get_max_population`.

## Enemy AI: aggressive + tactical (2026-09-22)
Refreshes the AI so that it is more aggressive and actually wages war:
- `self.dev` now has a `garrison` key (units kept on defence during the attack): easy 2 / normal 2 / hard 3.
- `_choose_state` attacks as soon as `enemy_combat >= aggr_threshold`, threshold = ~2/3 of `army` on normal/hard (`max(3, int(army*0.66))`), full target on easy. `self.state != "defend"` is kept so that defence is not abandoned under siege.
- `_attack_player` is TACTICAL: `_strategic_player_target()` picks ONE shared target — priority player production building (barracks/workshop/*_barracks/academy/dock), else town hall, else building, else player unit, all via `_dist_to_army` (anchored on the 1st enemy combat unit). The whole army is ordered onto that target (concentration, no more scattering). Garrison kept via `_enemy_base_pos()` (town_hall position).
- Ghost tests: `_game()` accepts `units=` and `buildings=` (not `workers/combat_units` when provided), and provides `movement_system` (RecordingMovement) — required because `_attack_player` goes through `_order_attack`, which checks `hasattr(game, 'movement_system')`.

## Enemy AI: escalation + resource defence (2026-09-22)
2 problems fixed: (1) the AI plateaued (~18 units) and could not rival a player who stacks workers/army; (2) it ignored worker raiders draining the mines/forests. Things to remember:
- **SCALING targets**: `_army_target()` / `_worker_target()` = base (`self.dev`) + growth over time (`mission_timer`): army +1 per 30s (cap easy 20 / normal 34 / hard 50), workers +1 per 45s (cap 24). `getattr(self.game, "mission_timer", 0)` returns 0 outside a game. `self.dev` remains the BASE (workers 7/10/14, army 6/8/12, garrison 2/3/4, barracks 2/3/4, towers 3/4/6).
- **`_develop()`**: below half the workers → worker; otherwise `_produce_units()` (which now returns **bool**: True if produced) up to `_army_target()`; if nothing was produced (pop cap) → `_build_farms_as_needed()` to raise the cap; completes the workers; then farms/barracks/towers; surplus → army beyond the target.
- **`_build_farms_as_needed()` builds PROACTIVELY** (before reaching the cap): builds a farm as long as `max_pop < workers_target + army_target + 6` (capped at 70). That is what lets the army grow with the escalation. BEFORE, it waited for pop >= 80% of the cap = deadlock (army stuck).
- **`_player_raiding_resources()`**: detects a player worker/builder whose `target_resource` is a NON-depleted node within <600px of the enemy base. `_choose_state` switches to `defend` if raiders drain the local resources (otherwise the player exhausts every mine). Uses `_enemy_base_pos()`.

## Sandbox mode (free mode) (2026-09-22)
- **"Mode Libre"** button in the main menu → `main_menu.handle_event` returns `"sandbox"`. Flow: `Game._sandbox_pending=True` → `faction_select` → `_start_sandbox()` directly (no difficulty).
- **`_start_sandbox()`**: `self.sandbox=True`, `current_mission=None`, `_apply_faction`, generous resources (800 gold / 600 wood / 300 food), purges EVERY enemy entity via **slice assignment** (`units[:]`/`buildings[:]`/`construction_sites[:]`), `ai.state="idle"`, `state="playing"`.
- Neutralisations in `Game.update`: `if not self.sandbox: self.ai.update(dt)` → the AI does not play. `_check_victory_defeat` returns early if `sandbox` → no victory/defeat even if you destroy the whole base.
- No crash: `_update_mission_progress`, `_check_mission_objectives`, `_draw_mission_hud` are all guarded by `if not self.current_mission` (None in sandbox). `_draw_mission_hud` is dead code (never called).

## Depth + minimap/groups (2026-09-22)
- **All techs functional**: `game._RESEARCH_EFFECTS` now covers ALL the techs of `TechTree._TECH_DEFS` (before, `gunpowder`, `orc_warpath`, `woodland_craft`, `master_armor`, `hero_training`, `siege_weapons`, etc. had NO effect). New effect types in `_apply_one_research_effect`: `attack_speed_percent` (**<1 = faster**), `speed_percent`, `max_hp_percent`, `worker_speed`. Pure unlock techs (`siege_weapons`, `ultimate_skill`, `hero_training`) = `{}` effect.
- New techs: `rapid_weapons` (pre-req iron_working, atk_speed -12%), `mounted_speed` (heavy_armor, +20% speed), `veteran_bulk` (iron_working, +12% HP), `scout_sight` (archery, +20% range), `rapid_workers` (free, workers 25% faster via `worker_speed` which boosts `base_harvest_speeds`/`harvest_speeds`), `siege_power` (siege_weapons, +20% damage).
- **`_apply_research_effects_to_unit(unit)`**: applies the research bonuses to a unit PRODUCED AFTER the research (existing units receive them at the moment the research completes). Called in `update` after the `production_system.update` spawn (next to `apply_unit_modifiers`). Without it, a unit produced after the research did not carry the damage/armor/etc. bonuses already researched.
- **Clickable minimap**: `HUD.minimap_rect()` exposes the rectangle; `Game._handle_minimap_click()` re-centres the camera (left click takes priority over selection). `Camera.move_to(x,y)` exists.
- **Control groups**: `Game.control_groups` (dict int -> [units]). `Ctrl+1..9` = assign the selection (`_assign_group`), `1..9` alone = recall (`_select_group`, filters out the dead, re-centres camera). `_handle_group_keys(event)` handles the keyboard; a bare key is only captured when NO building is selected (otherwise 1-6 = production). Mapping via `_group_key_for`. Do NOT rebind the units in control_groups (references) — `is_alive()` is re-filtered on recall against the list.

## Fixed defence system (2026-09-22)
BIG bug fixed: the towers (`tower`) had `damage`/`range` but NO system made them fire, and the walls (`wall`) did not block pathfinding. Now:
- **Towers that fire**: `Game._update_defenses(dt)` called at the end of `update`, loops over the living `tower` buildings and calls `_tower_fire(tower, dt)`. `_tower_fire` targets the OPPONENT of the `tower.faction` nearest in range (`tower.range`=128, dmg=20), 1s cooldown via `tower.attack_timer` (initialised in `Tower.__init__`). Applies `take_damage` + particle. Enemy towers therefore also fire at the player.
- **Walls that block**: `Pathfinder` now has `blocked_cells` (set of (x,y) tiles) + `set_blocked/add_blocked/remove_blocked`. `_is_valid_tile` rejects the blocked cells. `_update_defenses` recomputes the set every frame from the living walls (`b.hp>0`) → a built wall blocks, a destroyed wall frees. WARNING: walls block ALL camps (defence for both sides).
- Defence construction: `tower`/`wall` are already in every faction's rosters + `BASE_BUILDING_COSTS` (no need to add them).

## Layout
`core/game.py` (Game), `entities/` (Unit, Worker, Hero, unit_types w/ `create_unit`, building, resource_node), `systems/` (ai, construction, economy, faction data in factions.py, campaign, fog_of_war, combat), `ui/` (hud, menus), `map/`, `tests/` (pytest). Design history in `TAPE_*.md` and `*.md` audit notes at repo root.
