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
- B1 deprecated (fixé) : reload_game ne crashe plus. Le bug UnboundLocalError venait d'un import LOCAL conditionnel `from x import Y` dans une méthode où le nom est aussi utilisé hors du if : Python traite Y comme local sur toute la fonction -> UnboundLocalError quand le if est sauté. Fix : utiliser l'import deja present au niveau module, ne pas re-importer localement dans la methode.
- B2 est majeur : save_game écrit la clé `coins`, load_game/reload_game lisent `gold` -> or toujours remis à 0 au chargement. Ne pas confondre. Fix P2 : save écrit aussi kills/combats_won/level/xp/points ; load lit `coins` (fallback gold) ; reload_game restaura level/xp/points. Verifié : roundtrip complet preserve or/kills/combats/level.
- B4 : ARMOR_REGEN_RATE était 4.0 -> armure ennemie (30) régénérait plus vite que le DPS joueur (~53/s au contact) => softlock total, aucun HP perdu. Fix : passé a 1.0, l'armure se brise maintenant. Ne marche pas si tests attendent 5.0 (deja rouges avant).
- B5 : DamageSystem.apply_phase_2_damage(entity, damage, ko_threshold=250) créée - accumule damage_percent, KO a >= threshold (is_dead=True, hp=0). Réutilise KOSystem.trigger_ko (le système KO existait mais n'était jamais appelé). Les 6 ERROR test_phase_2 résolus.
- B6 : on_enemy_defeated attribue l'or (50 NORMAL/500 BOSS) via player.currency_manager.add_gold si present, sinon player.gold direct. test_on_enemy_defeated/test_on_boss_defeated passent. test_start_run echoue encore (damage_percent non remis a 0 par start_run, pre-existant hors B6).
- B7 : EquipmentManager.SLOT_TO_CATEGORIES (carte centralisee slot->categories) + validation dans equip() rejecte category-slot incoherent. load_game() appelle equip() donc la validation protege aussi le chargement (save corrompue ne reintroduit plus de gear invalide). ring->ring1/ring2, amulet->amulet1/amulet2 couverts. test_equip_with_invalid_category (5 subcases) passe. test_save_persists_equipment echoue encore (cle equipment vs equipped_gear, B8 hors B7).
- B10 : combo plafonnait a 1.1. Cause: on_hit() resetait combo_count si current_attacker != attacker, or les tests passent un NOUVEL objet a chaque hit => reset permanent. Reset etait du code mort (en jeu on_hit toujours appele avec self.p, meme objet). Fix: supprimer la garde current_attacker, combo s'accumule sur la fenetre chrono, reset par timer/parry. AUSSI: DamageSystem.calculate_damage plafonnait combo_mult a 2.5 alors que ComboSystem promet 3.0 -> aligne a 3.0. TTK baisse ~1.9x, B4 intact.
- B9 : tests balance codaient d'anciennes valeurs (HP 100, armor 50, regen 5.0, etc). Les constantes actuelles de combat_balance.py portent des commentaires documentant explicitement le design (Increased/Reduced/Same delay). Verdict: constantes = design volontaire, tests obsoletes -> tests mis a jour vers les constantes (pas l'inverse). 9 tests reparés (player_hp 500, armor 250, regen 1.0, delay 2.5, enemy ranges 250-400/500-800/1200, dmg ranges, boss_mult 1.3). B4/B10 intacts en runtime.
PyBR0S suite complete (367 tests) doit etre lancee avec monkeypatch `pygame.event.wait = lambda t=0: pygame.event.poll()` AVANT import pygame, sinon Game.__init__ (game_base.py:221 event.wait(0)) se fige en dummy driver (Run ~0.6s, sinon bloque indefiniment). Utiliser un script loader rather than `python -m unittest discover` (qui ne monkeypatche pas). B9 done: 9 tests constantes mis a jour vers le design combat_balance. Suite = 7 FAIL (B11 x5 + B8 x1 + test_start_run x1) + 0 ERROR.
- B8 : save_game lisait self.equipment_manager (attribut game) au lieu de p.equipment_manager (source mutee par gameplay). Fix: helper _equipped_to_dict() lit p.equipment_manager (fallback game). AUSSI dual-write: data["equipment"] (top-level) = player["equipped_gear"], et load_game fallback sur top "equipment" si equipped_gear absent (compat anciennes saves). test_save_persists_equipment reparse. test_start_run: start_run omettait damage_percent reset -> ajoute.
- B11 : rage etait CODE MORT: add_meter() incrementait current mais ne mettait jamais rage_mode=True -> decay/display jamais actifs. Fix: activation si current>=rage_threshold(80). Knockback: formules de l'implémentation deviaient du contrat documente dans les docstrings des tests (P1 8.0+0.35d+0.25d vs contrat 3.5+0.065d+0.16d ; P2 12+0.3d ignorait damage_percent vs contrat 5.0+dmg%*0.15+d*0.1). Fix vers contrat, knockback P1 ~2.6x plus faible => ennemi reste en portee, combat plus coherent. Tous les tests combat passent.

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
