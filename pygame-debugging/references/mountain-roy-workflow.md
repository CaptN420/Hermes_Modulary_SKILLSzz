# Mountain_Roy RTS Game - Development Workflow

## Project Overview
Python/Pygame 2D Real-Time Strategy game at `C:/Users/celes/Documents/Hermes-Workspace/Mountain_Roy`

## Core Systems Architecture

### Entity Hierarchy
```
entities/
  unit.py          # Base Unit class
  worker.py        # Worker with auto-gathering
  hero.py          # Hero unit
  building.py      # Buildings (TownHall, Barracks, Farm, CollectionBuilding)
  resource_node.py # Resource nodes (gold mines, wood forests, food farms)
  unit_types.py    # Factory for creating units (includes Builder)
```

### Systems Hierarchy
```
systems/
  construction.py  # Building construction & production
  movement.py      # Movement system
  combat.py        # Combat system
  economy.py       # Resource economy
  ai.py            # Enemy AI
  effects.py       # Visual/audio effects
```

### Core Game Loop
```python
class Game:
    def update(self, dt):
        # Handle input
        self.handle_events()
        
        # Update systems
        self._auto_gather_resources()  # Worker auto-gathering
        
        # Update entities
        for unit in self.units[:]:
            if unit.unit_type == "worker":
                unit.update(dt)  # Worker handles own movement
            else:
                self.movement_system.update(unit, dt)
            
            # Collision resolution
            self.collision_system.resolve_collision(unit, ...)
        
        # Render
        self.draw()
        pygame.display.flip()
```

## Worker Auto-Gathering Workflow

### Complete Lifecycle
1. **Spawn**: Workers created near base (4 workers + 1 builder for player)
2. **Assignment**: `_auto_gather_resources()` finds nearest resource
3. **Movement**: Worker moves toward target (wood/food first, then gold)
4. **Harvest**: At <30px, collect 10 units per harvest
5. **Deposit**: Return to closest same-faction building (Town Hall or Collection Building)
6. **Repeat**: Cycle continues until resource depleted

### Resource Priority
```
Priority 1: Wood forests (within 300px)
Priority 2: Food farms (within 300px)  
Priority 3: Gold mines (with available slots, max 3 workers)
```

## New Building Types (2026-09-16)

### Collection Building (harvest hut)
Constructible building near village for workers to deposit resources.

**Cost:** 100 gold, 80 wood, 6 seconds construction time
**Spawn:** One per faction at game start (near base)
**Usage:** Workers automatically find closest same-faction building for drop-off

```python
# In entities/building.py
class CollectionBuilding(Building):
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "collection")
        self.max_hp = 300
        self.hp = self.max_hp
        self.width = 48
        self.height = 48
```

**Lesson:** Collection buildings are the preferred drop-off point over Town Hall when closer.

### Builder Unit
Special worker that can construct buildings. Inherits from Worker.

```python
# In entities/unit_types.py
class Builder(Worker):
    def __init__(self, x: int, y: int, faction: str = "player"):
        Worker.__init__(self, x, y, faction)
        self.unit_type = "builder"
        self.can_build = True
```

**Spawn:** 1 builder per faction at game start (near workers)
**Usage:** Select builder → press `B` to enter build mode → click to place building

**Lesson:** Builder must inherit from Worker (not Unit) to get auto-gathering functionality.

### Worker Drop-off Point Logic
Workers now find closest same-faction building automatically:

```python
def _find_drop_off_point(self):
    closest_building = None
    closest_distance = float('inf')  # No search radius limit

    for building in self.game.buildings:
        if building.faction != self.faction:
            continue
        dx = building.x - self.x
        dy = building.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < closest_distance:
            closest_distance = distance
            closest_building = building

    if closest_building:
        self.drop_off_point = closest_building
```

**Lesson:** Use `float('inf')` for search radius, not a hardcoded value like 500.

### Building Selection and Interaction

**Pattern:** Left- or right-click a player building to select it; selection opens a production/research panel. **Re-clicking the already-selected building DOES NOT deselect it** — a selection toggle there feels like "it won't stay selected" to the player. Deselect ONLY via clicking empty ground (or a unit) or the **ESC** key, which must both route through `_deselect_building()`.

```python
# In game.py
def _find_building_at(self, map_x, map_y, radius=48):
    # nearest player building within radius, else None
    ...

def _select_building(self, building):
    for unit in self.units: unit.selected = False
    self.selected_units = []
    building.selected = True          # NO toggle: re-click keeps it selected
    self._selected_building = building

def _deselect_building(self):
    if self._selected_building:
        self._selected_building.selected = False
        self._selected_building = None
```

**Production is building-centered, not global.** Selecting a building and pressing keys 1-6 produces the units THAT building can make (per faction `unit_building` map), not a fixed global roster. Production buildings are: `barracks`, `workshop`, and the faction-unique `human_barracks`/`orc_war_hut`/`elf_ranger_lodge`/`dwarf_forge`. A unit appears only if its building exists AND its `unit_prereq` tech is researched (faction data).

```python
# In game.py
def _produce_selected_index(self, index):
    if not self._selected_building: return
    units = self._get_building_units(self._selected_building)
    combat = [u for u in units if u not in ("worker", "builder")]
    producible = [u for u in combat if self._is_unlocked(u)[0]]   # skip prereq-locked
    if 0 <= index < len(producible):
        self._spawn_unit(producible[index])

def _is_unlocked(self, unit_type):
    if self.faction is not None:
        return self.faction.can_produce(unit_type, self.buildings, self.tech_tree.unlocked_techs)
    return True, ""

# W/J always produce worker/builder directly (town hall), independent of selection
def _produce_worker(self, worker_type): ...  # unchanged
```

**HUD Integration:** Pass game + faction to the production HUD so it lists the selected building's units and marks locked ones:
```python
self.hud.draw_production_buttons(self.economy, self.selected_units, self._selected_building,
                                 self.production_system, self.faction, self)
```

**ESC must exit build mode BEFORE anything else.** When the player is in build mode (menu open via B, or `selected_building_type` armed for placement), a single ESC press should close the mode — NOT go to pause and NOT just deselect a building. Priority order in the `K_ESCAPE` handler: `build_menu_open` → close menu + clear `selected_building_type` + clear preview; elif `selected_building_type` → cancel placement; elif `_selected_building` → deselect; else → pause. If ESC only handles `_selected_building`/pause, the player is stuck in build mode and reports "ESC doesn't exit construction."

**Lesson:** Building selection uses `_selected_building`; deselect via empty-ground click or ESC, never a re-click toggle — a re-click toggle reads as "won't stay selected" and glues the panel shut. Units are gateable per-building (dock→naval) and per-tech (berserker→orc_warpath), and the touch keys MUST skip locked units. Also ensure each faction's primary war building produces at least one UNLOCKED basic unit at game start, or the player can never field troops until a tech/other building exists. Sort the production HUD's listed units so unlocked come first (numbered 1..N) to stay in sync with the touch keys.

### Worker Harvest Amount (timed gate + max_carry)

**Pattern:** Harvest is delay-gated and yields what the worker carries — the auto-loop is closed: harvest → carry → drop-off → deposit → return to the same resource.

```python
# In worker.py - update() method, at <30px from the node:
speed = self.harvest_speeds.get(rtype, 1.0)   # research bonuses multiply speed
self.harvest_progress += dt * speed            # ~1.0 second to fill
if self.harvest_progress >= 1.0:
    amount = node.harvest(self.max_carry)      # yield = min(max_carry, node.amount)
    if amount > 0:
        self.carrying = True
        self.carry_amount = amount
    self.harvest_progress = 0.0
```

**Lesson:** Harvest no longer happens in one frame — `harvest_progress` accumulates `dt * speed` and only fires when it crosses 1.0. Yield is `node.harvest(self.max_carry)`, so a research bonus must MULTIPLY `max_carry` (e.g. `u.max_carry = int(u.max_carry * factor)`) to affect real yield. Tests that assert harvesting must drive frame loops (`while not w.carrying: w.update(0.016)`) to complete the gate, then read the post-completion `carry_amount` — a single-frame `update` asserts nothing.

### Worker Fatigue and Multi-Resource System

**Pattern:** Workers can carry multiple resource types but need rest between deposits.

```python
class Worker(Unit):
    # Capacity
    self.max_carry = 15  # Increased from 10
    
    # Fatigue system
    self.fatigue_timer = 0.0
    self.fatigue_duration = 3.0  # Seconds of fatigue after deposit
    self.carrying_types = []  # Types being carried
    self.max_carry_types = 2  # Max 2 types before fatigue
    
    # Hyper mode (rare) - carry all 3 types for 10s
    self.hyper_mode = False
    self.hyper_timer = 0.0
    self.hyper_duration = 10.0
```

**Behavior:**
- After depositing, worker enters fatigue for 3 seconds - only gathers same resource type
- If carrying 2 types and deposits, 10% chance to activate hyper mode (carry all 3 types for 10s)
- During fatigue, `_find_and_assign_to_resource()` filters out different resource types

**Resource Finding Logic:**
```python
def _find_and_assign_to_resource(self):
    is_fatigued = self.fatigue_timer < self.fatigue_duration
    
    # If fatigued, only search for resources of carried types
    if is_fatigued and self.carrying_types:
        for node in self.game.resource_nodes:
            if node.resource_type not in self.carrying_types:
                continue  # Skip different types while fatigued
            # ... find closest matching resource
    
    # Normal search - prioritize uncollected types
    for node in self.game.resource_nodes:
        if is_fatigued and node.resource_type not in self.carrying_types:
            continue
        # ... normal distance check
```

**Lesson:** Fatigue prevents workers from constantly switching resources, creating more efficient collection patterns. Hyper mode is a rare bonus for balanced resource gathering.

### Worker Production System

**Pattern:** Workers can be produced via construction system.

```python
# In systems/construction.py
WORKER_COSTS = {
    "worker": {"gold": 30, "wood": 15, "food": 5, "time": 2.0},
    "builder": {"gold": 40, "wood": 20, "food": 5, "time": 2.5},
}

def produce_worker(self, worker_type: str, x: int, y: int) -> bool:
    """Produce a worker unit."""
    cost = self.WORKER_COSTS.get(worker_type)
    if not cost or not self.economy.can_afford(cost):
        return False
    
    self.economy.pay_cost(cost)
    
    from entities.worker import Worker
    from entities.unit_types import Builder
    
    if worker_type == "worker":
        unit = Worker(x, y, "player")
    else:
        unit = Builder(x, y, "player")
    
    unit.game = self.economy  # Assign game reference
    self.units.append(unit)
    return True
```

**Controls:**
- `W` key - Produce worker
- `J` key - Produce builder

**Lesson:** Workers and builders are produced through the construction system, not the production system. Use separate keys to distinguish from military units (1-6).

### Construction System Must Be Wired Into the Game Loop

**Symptom:** "Construction started: farm" prints, but the building is never completed — workers/builder are assigned to the site but nothing progresses.

**Root cause:** `ConstructionSystem.start_construction()` creates the `BuildingProgress` site and assigns a builder, but `ConstructionSystem.update(dt)` was **never called** from `game.update()`. No update → `site.progress` never advances → the building is never created. This is the same class of bug as a movement/render system you forget to tick.

**Fix:** Call it every frame in `game.update()` (alongside the other systems):
```python
# in game.update()
self.visual_effects.update(dt)
self.construction_system.update(dt)   # <-- was missing
self.tech_tree.update(dt)
```

**Also required:** builders must physically move to the site. In `Worker.update()`, after the movement block, if the worker has a `construction_target`, steer toward its (x, y):
```python
construction = getattr(self, 'construction_target', None)
if construction is not None:
    cdx, cdy = construction.x - self.x, construction.y - self.y
    d = (cdx*cdx + cdy*cdy) ** 0.5
    if d > 25:
        self.x += (cdx/d) * self.speed * dt
        self.y += (cdy/d) * self.speed * dt
    return  # building progress is driven by BuildingProgress.update once assigned
```

And `_assign_worker_to_construction` must pick builders/workers that are NOT already on a site, neutralize their resource target so they stop gathering:
```python
def _assign_worker_to_construction(self, progress):
    candidates = [u for u in self.units
                  if getattr(u, 'unit_type', None) in ('builder','worker')
                  and getattr(u, 'construction_target', None) is None]
    for unit in candidates:      # builders first, then workers
        unit.construction_target = progress
        unit.target_resource = None   # stop gathering while building
        unit.carrying = False
        unit.carry_amount = 0
        progress.assigned_workers.append(unit)
        return True
    return False
```

**When the site completes**, free the workers by deleting `construction_target` and let the existing remove-site logic run — don't also mutate `self.construction_sites` inside the worker loop (that corrupts the iteration and removed the wrong site before).

**Lesson:** A system that owns a time progression (`ConstructionSystem.update`) does NOT run unless the game loop ticks it. When a building "never completes," first check the `update()` call exists. Construction is a three-part contract: game loop ticks the system, the site has an assigned worker, and that worker moves to the site. Missing any one part looks identical: "started but never built."

## Common Pitfalls

### Shared Economy Pool Between Factions (Critical)

**Symptom:** Player's gold/wood/food inexplicably decrease or "reset" over time when units are being produced, even though nothing was built/spent.

**Root cause:** Both player and enemy share the SAME `EconomySystem` instance (`self.game.economy`). The enemy AI (`ai.py` `_produce_units`/`_build_structures`) and enemy workers both debit/credit the player's single pool — so enemy production drains the player's visible resources.

**Fix:** Give each faction its own economy and route resource access by faction:
```python
# In Game.__init__:
self.economy = EconomySystem()          # player
self.enemy_economy = EconomySystem()    # enemy

# In ai.py — always reference the enemy's pool:
ec = self.game.enemy_economy
if ec.gold >= cost["gold"]: ...

# In worker.py _deposit_resources — pick pool by faction:
ec = self.game.enemy_economy if getattr(self, 'faction', 'player') == 'enemy' else self.game.economy
ec.add_resources(wood=self.carry_amount)
```

**Lesson:** In an RTS, never give two factions the same economy handle. Search EVERY site that mutates resources (`ai.py`, worker deposit, production) and split by `faction`. A shared pool is the classic "resources drain for no reason" bug — audit where resource deltas originate before touching harvest/balance values.

### Type Mismatch in Auto-Gather
```python
# WRONG - checks for "scout" but workers are "worker"
if unit.unit_type == "scout":
    ...

# CORRECT
if unit.unit_type == "worker":
    ...
```

### Duplicate Movement Control
- Worker's `update()` handles movement OR game loop does, not both
- Mixing causes erratic behavior

### Resource Node Import Path
```python
# CORRECT - use entities version (has radius, worker assignment)
from entities.resource_node import ResourceNode

# WRONG - old economy version (no radius)
from systems.economy import ResourceNode
```

### Worker Collision: Carrying Workers Should Not Push Each Other

**Symptom:** Workers carrying resources stop moving or get stuck in clusters when heading to drop-off points. They \"pass through\" but then suddenly bounce off each other.

**Root cause:** The collision system pushes ALL units apart with a 25px separation distance. Two workers both carrying resources will repel each other even though they need to pass freely to reach their destinations.

**Fix:** Skip collision resolution between two workers that are BOTH carrying resources:
```python
# In systems/collision.py resolve_collision():
is_worker_carrying = (getattr(unit, 'unit_type', None) == 'worker' and getattr(unit, 'carrying', False))
for other in all_units:
    if other == unit:
        continue
    other_carrying = (getattr(other, 'unit_type', None) == 'worker' and getattr(other, 'carrying', False))
    if is_worker_carrying and other_carrying:
        continue  # Workers carrying resources pass through each other
```

**Lesson:** When workers carry resources, they need free passage to complete their cycle. The collision system should not block two carrying workers from passing each other — only push them apart when at least one is NOT carrying (e.g., a combat unit vs. a worker). Use `getattr()` with defaults to avoid AttributeError on plain Unit objects in tests.

### Worker Tree Traversal

**Symptom:** Workers get stuck moving through forest areas, bouncing off trees endlessly.

**Root cause:** `Worker.can_cut_trees` is set to `False` by default, causing forest collision to block all workers.

**Fix:** Set `can_cut_trees = True` in Worker.__init__ so workers can traverse forests:
```python
# In entities/worker.py __init__()
self.can_cut_trees = True  # Workers can pass through forests
```

**Lesson:** Workers are designed to gather resources from forests, so they should be able to move through them. The `can_cut_trees` flag controls forest collision in `_check_forest_collision()`.

### Worker Personality and Mood System

**Pattern:** Workers have individual personalities that affect their behavior and dialogue.

```python
class Worker(Unit):
    # Personality traits (randomized at spawn)
    self.personality = {
        "traits": {
            "work_ethic": random.uniform(0.5, 1.5),
            "social": random.uniform(0.3, 1.2),
            "optimism": random.uniform(0.4, 1.0),
            "resilience": random.uniform(0.5, 1.0),
        },
        "primary": "hardworking",  # lazy, optimist, pessimist, social, loner
        "phrase": "Je peux travailler toute la journée!",
    }

    # Mood system
    self.mood = "neutral"  # neutral, happy, tired, motivated, demotivated
    self.motivation_level = 1.0  # 0.0 to 1.0
    self.chat_bubble = None  # Dialogue bubble
```

**Mood Determination:**
- `happy`: Carrying resources and not fatigued
- `tired`: Fatigue timer > 2x fatigue_duration
- `motivated`: Motivation > 0.8 AND hyper_mode active
- `demotivated`: Motivation < 0.3
- `neutral`: Default state

**Motivation Factors:**
- Morning (6-12h): +0.2 motivation boost
- Afternoon (12-18h): +0.1 motivation boost
- Evening/Night: -0.1 motivation boost

**Group Motivation:**
```python
def try_motivate_nearby(self, nearby_workers):
    """Motivated workers boost nearby workers' motivation."""
    if self.mood not in ["motivated", "happy"]:
        return False

    for other in nearby_workers:
        dx = other.x - self.x
        dy = other.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < 100:  # Motivation radius
            other.motivation_level = min(1.0, other.motivation_level + 0.2)
            other.mood = "motivated"
```

**Dialogue System:**
```python
def _generate_chat(self):
    """Generate context-appropriate dialogue."""
    chats = {
        "happy": ["Ça va bien!", "J'adore travailler!"],
        "tired": ["J'en peux plus...", "Zzz..."],
        "motivated": ["On va gagner!", "En avant!"],
        "demotivated": ["Pourquoi je fais ça?"],
    }

    # Social workers add greeting phrases
    if random.random() < self.personality["traits"]["social"]:
        chats["neutral"].append("Salut les gars!")
```

**Lesson:** Workers with personalities create more immersive gameplay. The motivation system creates emergent group dynamics where positive workers influence others.

### Worker Update Pattern (Critical)

**Pattern:** Worker update must be consolidated - never duplicate movement control between game loop and worker's own update().

```python
# CORRECT: Single update path
for unit in self.units[:]:
    if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
        unit.update(dt)  # Worker handles its own movement
    else:
        self.movement_system.update(unit, dt)
```

**Common Error:** Adding inline worker movement logic in game.py alongside worker.update() causes erratic behavior.

**Lesson:** Pick one system (worker's own update or movement system) and stick with it. Never mix both.

### Random Import Pattern

**Pattern:** Import `random` at module level, not inside methods.

```python
# CORRECT:
import pygame
import random
from entities.unit import Unit

class Worker(Unit):
    def _update_mood(self, dt: float):
        # Use random directly
        if random.random() < 0.001 * dt:
            self._generate_chat()
```

**Common Error:** Forgetting to import `random` at module level causes `NameError: name 'random' is not defined`.

**Lesson:** Always import standard library modules at the top of the file, not inside methods. This is a common Python anti-pattern that breaks code.

## Automated Test Suite (pytest, headless)

**Pytest lives in the venv:** `.venv/Scripts/python.exe -m pytest tests/ -q`. Install once with `.venv/Scripts/pip.exe install pytest`. Run the WHOLE `tests/` dir before and after any change; the suite is fast and catches regressions the isolated unit harness misses.

**Every test module must `pygame.init()` + `pygame.display.set_mode((100,100))` at import** or SDL init fails. Never `pytest.ini` `SDL_VIDEODRIVER=dummy` in a way that skips this — the real Game() constructor calls `pygame.display.set_mode` itself, so give it a surface.

**Seasoned test fixtures for Game-facade tests:**
```python
def fresh_game(save_dir):
    from core.game import Game
    g = Game()
    g._apply_faction("elf")          # MUST call _apply_faction to init faction/rosters
    g.state = "playing"
    g.economy.gold = 1000; g.economy.wood = 1000; g.economy.food = 1000
    g.enemy_economy.gold = 123       # seed the SEPARATE enemy pool too
    if save_dir: g.save_system.save_dir = save_dir
    return g
```

**Force the whole map to GRASS in any test that PLACES A BUILDING or runs save/load of construction sites.** The real `game_map` is randomly generated with WATER/MOUNTAIN/FOREST tiles, and once build-position validation is real, `start_construction` at a fixed coordinate silently refuses on a random water tile — the test becomes flaky, passing or failing on the map seed of the moment. Synthetic maps are the cure:
```python
from map.tile import Tile, TileType
for yy in range(g.game_map.height):
    g.game_map.tiles[yy] = [Tile(xx, yy, TileType.GRASS) for xx in range(g.game_map.width)]
g.construction_system._game_map = g.game_map
g.construction_system._all_nodes = []
```

**Inspect the API before writing the test.** This session's first QA harness crashed wholesale with `missing 1 required positional argument: 'fid'` because the runner called `fn()` while each scenario declared `fn(fid)`. Add a tiny argument-dispatch (inspect signature, pass the loop var only if the callable declares it) so the harness doesn't mask the real results.

**After a parallel-subagent merge, verify the combined state, not just your slice.** When two agents edit the same `core/game.py` concurrently (one adding pathfinding in the movement section, another adding objectives/UI in the mission section), each agent's own tests pass in isolation but the merged file can collide. After the last agent reports: run the FULL `tests/` dir, then a real `game.update()+game.draw()` loop across every faction past some frames. A green full suite PLUS a live smoke loop is the only reliable signal that the concurrent edits merged cleanly. Do not declare victory on a subagent's self-reported test count.

## Audit Priority Order (user-specified)

When fixing a batch of verified bugs, the user wants this exact order (do not reorganize):
1. **Technology research** (tech tree)
2. **Workers & economy**
3. **Save / load**
4. **Construction & placement**
5. **Movement, pathfinding & combat**
6. **Campaign & UX**

Each fix must be done TDD (test first, watch it fail, implement, watch it pass) and must NOT break the earlier tests. At the end give a summary: files modified, bugs fixed, tests run, remaining limits.

## Tech-Tree State Bugs (class-level state is shared)

**Symptom:** researching in one game affects another; a finished tech is re-added to `unlocked_techs` every frame; cost is never deducted; `start_research()` with no resources silently grants 9999.

**Root causes and fixes:**
- `all_technologies = []` as a CLASS attribute in `TechTree` → every instance mutates the same list/objects. Declare a module-level immutable `_TECH_DEFS` and build per-instance `self.technologies` dict in `__init__`.
- `start_research` validated affordance but never debited → call `resources.pay_cost(cost)` exactly once at launch.
- Finished tech stays in `current_research` and is appended each frame → on completion, append once (guard `if tech_id not in unlocked_techs`) and set `current_research = None`.
- `start_research(tech_id)` with `resources=None` defaulted to 9999 → **refuse** when resources is None; the caller must pass a real economy.
- `resources` param can be a dict OR an object. The refactored `TechTree` calls `resources.pay_cost(cost)`/`resources.can_afford(cost)`, so the CALLER (game.py `_research_next_tech`) must pass the `EconomySystem` object, not a `{gold:,wood:,food:}` dict.
- Make `Technology.update` activate when `progress >= time` even if a test sets progress exactly to the limit — gate on `if not self.researched`, not `if progress < time`.

**save/load of the tree:** `to_dict`/`from_dict` must round-trip `current_research`, `unlocked_techs`, and per-tech `researched` + `research_progress`. Restore by tech_id into the already-built instance, don't reconstruct from scratch.

## Save/Load v2 (persistence completeness)

**Symptom:** after loading, all buildings are TownHalls, enemy resources reset, campaign/tech/stats lost, workers can't gather.

**Root causes and fixes:**
- `save_game` previously wrote only `resources`, `units`, `buildings`, `hero` → add **`version: "2.0"`** plus faction_id, enemy_resources, tech_tree, resource_nodes, construction_sites, stats, campaign, mission.
- Buildings restored via `TownHall(...)` for every type → restore the REAL type through the construction factory `self.construction_system._create_building(type, x, y, faction)`, falling back to TownHall on unknown.
- Workers loaded with `game=None` (or economy) → reattach every worker/builder to the Game object and reset its gather state (target_resource/carrying).
- Version check: reject unknown versions with a clear message; migrate or refuse.
- Always add a save→load idempotence test (faction, resources, building types, workers attached, campaign, tech tree, in-progress sites all preserved).

## produce_worker Must Receive the Game Object

**Symptom:** a worker produced via `ConstructionSystem.produce_worker` crashes or never gathers — `AttributeError` on `game.resource_nodes`, or it silently does nothing.

**Root cause:** `produce_worker` assigned `unit.game = self.economy` — a worker expects a `Game` (needs `resource_nodes`, `buildings`, `economy`, `enemy_economy`), not an economy.

**Fix:** add a `game=None` parameter and store a fallback: `self.set_game(game)` from `Game.__init__`, pass `game=self` at the one production call site. Never let a worker end up with `.game` pointing at an `EconomySystem`.

## Harvest Amount MUST Be Driven by max_carry

**Symptom:** researching `mining`/`logging`/`agriculture` claims "2x more" but nothing changes — the research bonus mutates `max_carry` yet the harvest line is `node.harvest(50)` (a hard constant).

**Fix:** harvest what the worker can actually carry so the research multiplier has a real effect:
```python
amount = node.harvest(self.max_carry)
```
And make the research bonus a MULTIPLIER, not a +constant: `u.max_carry = int(u.max_carry * factor)` with `factor = max(boosts.values())`.

**Lesson:** a bonus whose effect is stored in a variable that nothing reads is fake. Trace the actual harvest call when "the bonus does nothing" — the constant-swallow is the bug.

## Construction Validation (can_build was a stub)

**Symptom:** `ConstructionSystem.can_build` returned `True` unconditionally (a TODO stub), so buildings could be placed on water/mountains/on top of other things, and resources were debited for invalid placements.

**Fix:** make placement a real predicate `validate_build_position(type, x, y) -> (ok, reason)` that refuses: out of map, non-buildable terrain (Water/Mountain/Forest/etc.), overlapping building, overlapping construction site, overlapping resource node, overlapping unit. Use a per-building `_BUILDING_FOOTPRINT` (px) for overlap distance. Keep the LIVE lists (`self.buildings`, `self.construction_sites`, `self.units`) — do NOT snapshot them into copies at `set_game`, or buildings added later never get detected. `can_build` = validate + afford. `start_construction` must call the validation BEFORE `pay_cost`, and NOT debit when the position is invalid.

**Building center vs. footprint:** buildings draw centered on (x,y) with a width/height, and collision uses `distance < footprint`. Use `footprint` for overlap so two buildings never co-locate; use `footprint // 2` for units so a unit lets a building spawn next to it.

## Quick Test
```bash
cd C:/Users/celes/Documents/Hermes-Workspace/Mountain_Roy
.venv/Scripts/python.exe -u main.py
```

### Unit Test Worker
```python
from entities.worker import Worker
from entities.unit_types import create_unit

worker = Worker(100, 100, 'player')
print(f'Worker type: {worker.unit_type}')
print(f'Can gather: {worker.can_gather}')
```

## Controls Reference
| Key | Action |
|-----|--------|
| `1-6` | Produce the selected building's units (faction roster) |
| `W` | Produce worker (gatherer) |
| `J` | Produce builder (construction unit) |
| `T` | Research (requires a research building selected) |
| `B` | Toggle build mode |
| Click | Select buildings/units / place buildings |
| Click empty ground / ESC | Deselect the selected building |
| Right-click | Order to resource/enemy / select building |
| WASD/Arrows | Camera movement |
| Scroll wheel | Zoom in/out |

## File Structure Quick Reference
```
Mountain_Roy/
  core/
    game.py          # Main Game class
  entities/
    unit.py          # Base Unit
    worker.py        # Worker with auto-gathering
    building.py      # Buildings
    resource_node.py # Resource nodes
  systems/
    construction.py  # Building/production systems
    movement.py      # Movement logic
  ui/
    hud.py           # Heads-up display
  settings.py        # Constants (SCREEN_SIZE, COLORS, etc.)
```