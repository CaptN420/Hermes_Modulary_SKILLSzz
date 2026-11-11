---
name: pybr0s
category: game-dev
description: Use when working on PyBR0S (Python/Pygame 2D fighting/RPG).
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pygame, rpg, combat, sprite, game-dev, tests]
    related_skills: [pygame-debugging, sprite-management, pygame-asset-generation]
---

# PyBR0S (Python/Pygame 2D Fighting/RPG)

Project: `C:\Users\celes\Documents\Hermes-Workspace\PyBR0SVARCHITECTURE-master` (v1.3). French-speaking user; concise French replies. Values verified working code over explanations.

## Architecture Notes (Audit 2026-09-29)

**CRITICAL - Address in priority order:**

1. **God class anti-pattern** - `GameBaseMixin` is 864 lines with 12+ managers. Extract responsibilities into focused classes before adding new features.
2. **Entity duplication** - Player/Enemy share ~70% identical code. Look for base Entity extraction (combat logic, state machines).
3. **Config balancing spread** - Balance values scattered across `config.py`, `settings.py`, `combat_balance.py`. Centralize in dedicated `balance.py`.
4. **Test coverage gaps** - Combat/core tested; roguelite/perks/equipment untested. Add tests for subsystems before changes.

**Good patterns to preserve:**
- Manager registry pattern (`ManagerRegistry`) for dependency injection
- Event-driven architecture (`EventSystem`) for decoupling
- Data-driven design (config dicts, not hardcoded values)

## Hard-won facts (do not regress)

- **Assets now shipped (2026-10)**: `assets/` populated — Kenney Pixel Platformer + Industrial expansion + UI Pack + Impact Sounds, Brackeys' bundle, LuizMelo Martial Hero 1&2, Samurai, Ice Golem, Ardentryst magic effects, battle/factory/lava music. All licenses + attributions recorded in `assets/CREDITS.txt` (CC-BY packs must keep the author name: Redshrike for Ice Golem, Elle Trudgett for Ardentryst).
- **Sprite system (per-class skins)**: `core/sprite_animator.py` maps class → skin via `get_player_animator(class_name)` (lazy, cached per class, `.upper()`-normalized). Knight→SamuraiAnimator (samurai pack), Rogue→Martial Hero 2 (default/fallback), Mage→Martial Hero, Heavy→StaticAnimator on one extracted knight-grid frame; unknown class → Rogue, never None. Animations: idle/run/attack1/attack2/hurt/jump/fall/death; state missing → idle fallback. Enemies render the Ice Golem via `StaticAnimator`. All drawn over the unchanged 40x60 rect, anchored bottom-center, flipped by `facing`, fallback to the old rectangle when the asset is missing. Remaining roadmap per user: VFX → Kenney UI → audio → per-map music.
- **Runtime combat probes**: before asserting HP dropped, know the pipeline — `DamageSystem.apply_damage(target, dmg, direction)` takes a SCALAR direction (a Vector2 raises in `apply_knockback`), and armor absorbs damage BEFORE HP (a hit under the enemy's ~30 armor leaves HP unchanged and looks like a false failure; use damage > armor). `ComboSystem.on_hit(attacker, defender)` requires both args. Verify these signatures in the source before writing a regression script.
- **Standing rule for ALL asset integration (rendering/audio only)**: modify ONLY the requested render/audio code; NEVER touch gameplay mechanics, hitboxes, damage, save, or balance. Visual sprite ~40x60, physical rect 40x60 stays identical. The 367-test suite must stay green — run it BEFORE and AFTER via the loader script (the `pygame.event.wait` monkeypatch loader in scratch; direct `unittest discover` freezes in dummy driver).
- **Level layout**: Unified platform layout in `world/level.py` - big ground (y=520), 2 lower platforms (y=420), middle elevated (y=320), 3 in line (y=250), upper platforms (y=150). All one-way.
- **Spawn points**: At (328,400) and (1272,400).
- **CLASS_SKINS keys capitalized but .lower() lookup** - causes FIGHTER fallback. Keys are uppercase in dict but looked up with `.lower()`.

## Running tests
- B1 deprecated (fixed): reload_game no longer crashes. The UnboundLocalError bug came from a conditional LOCAL import `from x import Y` in a method where the name is also used outside the if: Python treats Y as local for the whole function -> UnboundLocalError when the if is skipped. Fix: use the import already present at module level, do not re-import locally inside the method.
- B2 is major: save_game writes the `coins` key, load_game/reload_game read `gold` -> gold always reset to 0 on load. Do not confuse them. P2 fix: save also writes kills/combats_won/level/xp/points ; load reads `coins` (gold fallback); reload_game restores level/xp/points. Verified: full roundtrip preserves gold/kills/combats/level.
- B4: ARMOR_REGEN_RATE was 4.0 -> enemy armor (30) regenerated faster than player DPS (~53/s on contact) => total softlock, no HP lost. Fix: changed to 1.0, armor now breaks. Does not work if tests expect 5.0 (already red beforehand).
- B5: DamageSystem.apply_phase_2_damage(entity, damage, ko_threshold=250) created - accumulates damage_percent, KO at >= threshold (is_dead=True, hp=0). Reuses KOSystem.trigger_ko (the KO system existed but was never called). The 6 test_phase_2 ERRORs resolved.
- B6: on_enemy_defeated awards the gold (50 NORMAL/500 BOSS) via player.currency_manager.add_gold if present, otherwise player.gold directly. test_on_enemy_defeated/test_on_boss_defeated pass. test_start_run still fails (damage_percent not reset to 0 by start_run, pre-existing outside B6).
- B7: EquipmentManager.SLOT_TO_CATEGORIES (centralized slot->categories map) + validation in equip() rejects an inconsistent category-slot. load_game() calls equip() so the validation also protects loading (a corrupted save no longer reintroduces invalid gear). ring->ring1/ring2, amulet->amulet1/amulet2 covered. test_equip_with_invalid_category (5 subcases) passes. test_save_persists_equipment still fails (equipment vs equipped_gear key, B8 outside B7).
- B10: combo was capped at 1.1. Cause: on_hit() reset combo_count if current_attacker != attacker, but the tests pass a NEW object on every hit => permanent reset. The reset was dead code (in game on_hit is always called with self.p, the same object). Fix: remove the current_attacker guard, combo accumulates over the chrono window, reset by timer/parry. ALSO: DamageSystem.calculate_damage capped combo_mult at 2.5 while ComboSystem promises 3.0 -> aligned to 3.0. TTK drops ~1.9x, B4 intact.
- B9: balance tests hardcoded old values (HP 100, armor 50, regen 5.0, etc). The current constants in combat_balance.py carry comments explicitly documenting the design (Increased/Reduced/Same delay). Verdict: constants = intentional design, tests stale -> tests updated to the constants (not the reverse). 9 tests repaired (player_hp 500, armor 250, regen 1.0, delay 2.5, enemy ranges 250-400/500-800/1200, dmg ranges, boss_mult 1.3). B4/B10 intact at runtime.
The full PyBR0S suite (367 tests) must be run with the monkeypatch `pygame.event.wait = lambda t=0: pygame.event.poll()` BEFORE importing pygame, otherwise Game.__init__ (game_base.py:221 event.wait(0)) freezes in dummy driver (Run ~0.6s, otherwise blocks indefinitely). Use a loader script rather than `python -m unittest discover` (which does not monkeypatch). B9 done: 9 constant tests updated to the combat_balance design. Suite = 7 FAIL (B11 x5 + B8 x1 + test_start_run x1) + 0 ERROR.
- B8: save_game read self.equipment_manager (game attribute) instead of p.equipment_manager (source mutated by gameplay). Fix: helper _equipped_to_dict() reads p.equipment_manager (game fallback). ALSO dual-write: data["equipment"] (top-level) = player["equipped_gear"], and load_game falls back to top-level "equipment" if equipped_gear is absent (old save compatibility). test_save_persists_equipment reparses. test_start_run: start_run omitted the damage_percent reset -> added.
- B11: rage was DEAD CODE: add_meter() incremented current but never set rage_mode=True -> decay/display never active. Fix: activation when current>=rage_threshold(80). Knockback: the implementation formulas deviated from the contract documented in the test docstrings (P1 8.0+0.35d+0.25d vs contract 3.5+0.065d+0.16d ; P2 12+0.3d ignored damage_percent vs contract 5.0+dmg%*0.15+d*0.1). Fix toward the contract, knockback P1 ~2.6x weaker => the enemy stays in range, combat is more coherent. All combat tests pass.

## Running tests
```bash
cd C:/Users/celes/Documents/Hermes-Workspace/PyBR0SVARCHITECTURE-master
venv/Scripts/python.exe -m unittest discover -s tests
# Or for a single test file:
/c/Users/celes/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m unittest tests.test_state_machine -v
```

**Pitfall**: System python 3.14 has no pygame — `import pygame` fails with ModuleNotFoundError. Always use the hermes-agent venv python.

## Verifying sprite/VFX rendering headless (dummy driver)
When you change rendering but cannot see a window, verify the sprite actually drew by probing the game's own screen surface:
1. Build a `Game`, `set_state(PLAYING)`, `ensure_player()`, `reset_game()`, call `g.draw()` a few times.
2. Locate the player with `g.cam.apply(p.rect)` — the camera is NOT updated until the loop runs, so in a bare probe `offset=(0,0) zoom=1` and the rect sits at its world coords. Probe the pixel region around that rect and count colors that are NOT the background `(20,20,20)` or platform green `(100,200,100)`; a rendered sprite shows its palette colors there (e.g. Martial Hero outfit ~`(51,56,146)`).
3. To eyeball it, `pygame.image.save(g.screen, path)` then upscale the region around `cam.apply(p.rect)` with `pygame.transform.scale(x4)` — clamp the subsurface to screen bounds or you get `ValueError: subsurface rectangle outside surface area`.
4. Test the asset-missing fallback by renaming the sprite folder, calling `draw()`, and asserting the fallback (white rect) draws without crash — restore the folder after.
5. Confirm the hitbox is untouched: assert `p.rect` stays `Rect(620, 212, 40, 60)`-shaped (40x60) across states.

## File structure
- `core/` - Game loop, base classes, config
- `entities/` - Player, Enemy classes
- `combat/` - Damage, combo, elemental, knockback, parry systems
- `systems/` - Managers (save, inventory, equipment, currency, skill)
- `world/` - Level layout, world prototype (map, player, camera, portal, manager)
- `roguelite/` - Roguelite mechanics
- `perks/` - Perk system
- `advanced_ai/` - AI brain
- `tests/` - Test suites

## Pitfalls

- **Don't add features to GameBaseMixin** - It's already a maintenance hazard. Add managers via registry or composition.
- **Entity refactoring first** - Before adding new combat features, extract base Entity class to reduce duplication.
- **Balance values centralized** - Any new balance parameter goes in `combat_balance.py`, not scattered across files.
- **Test before touching untested subsystems** - Roguelite/perks/equipment have no tests. Add them first.

## World Prototype Integration Pattern

When integrating the world prototype (world/manager.py) into the main game loop:

1. **Add GameState.WORLD** to `core/game_states.py` for the new state.
2. **Add `self.world_manager = None`** in `GameBaseMixin.__init__` (core/game_base.py).
3. **Implement `_enter_world()` and `_update_world(dt)`** methods in `GameBaseMixin`.
4. **Handle WORLD state in event loop** (game_loop.py) - typically ESC to exit, another key to enter.
5. **Add `draw_world_screen()`** to `GameRenderMixin` (core/game_render.py).
6. **Call `_update_world(dt)`** in the update loop when `self.state == GameState.WORLD`.

**Lesson:** The world prototype is intentionally isolated - it doesn't modify existing combat systems. Integration should be minimal: state flag + delegate calls, no coupling to game internals.

**Debug tip:** Use a debug key (e.g., 'W' from title screen) to enter the world for testing. ESC returns to TITLE state.

## Autonomous Mode (Auto-Play for Testing)

For headless testing or demo purposes, implement autonomous mode:

1. Add flag `self.autonomous = False` in `GameBaseMixin.__init__`
2. Implement `_autonomous_input()` returning dict with movement keys based on enemy positions
3. Implement `_autonomous_advance()` to auto-transition through menu states (TITLE→MAIN_MENU→CLASS_SELECT→MAP_SELECT→PLAYING)
4. In `game_loop.py`, replace `self.ctrl.get()` with `self._autonomous_input() if self.autonomous else self.ctrl.get()`
5. Add CLI arg `--autonomous` in `main.py`

**Pitfall**: Pygame requires a display window - there is no true headless mode without SDL dummy driver. For CI/testing, consider `pygame.display.set_mode()` with offscreen rendering or use the dummy driver: `os.environ['SDL_VIDEODRIVER'] = 'dummy'` before `pygame.init()`.

**Pitfall**: Menu classes expect pygame events - either pass `None` and handle it, or bypass menus entirely by calling state transitions directly.

## Related Skills
- `sprite-management` - Sprite loading and rendering
- `software-development:codebase-inspection` - LOC analysis
- `software-development:requesting-code-review` - Pre-commit review
