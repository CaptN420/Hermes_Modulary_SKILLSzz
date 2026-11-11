# Mountain_Roy / Pygame — bug oracle (symptom → cause → fix → lesson)

Extracted from the former SKILL.md (799 lines) during the split. Every entry is a real pitfall.

## Resource Systems

### Resource Node Pattern

**Symptom:** Resources not depleting or regenerating.

**Root cause:** Missing `max_amount` attribute for regeneration tracking.

**Fix:** Always initialize both `amount` and `max_amount`:
```python
class ResourceNode:
    def __init__(self, x: int, y: int, resource_type: str, amount: int):
        self.x = x
        self.y = y
        self.resource_type = resource_type
        self.amount = amount
        self.max_amount = amount  # Required for regeneration
```

### Resource Regeneration

**Pattern:** Only regenerate renewable resources (wood), not depletable ones (gold).

```python
def _regenerate_resources(self, dt: float):
    """Regenerate wood forests over time."""
    for node in self.resource_nodes:
        if node.resource_type == "wood" and not node.is_depleted():
            regen_amount = int(node.max_amount * 0.01 * dt)  # 1% per second
            if regen_amount > 0:
                node.amount = min(node.max_amount, node.amount + regen_amount)
```

**Lesson:** Gold mines are "abandoned" - they deplete and don't regenerate. Wood forests regenerate slowly.

### Random Resource Generation

**Pattern:** Use time-based seed for varied map layouts across playthroughs.

```python
def _generate_resource_nodes(self):
    import random
    random.seed(int(time.time()) % 10000)  # Varied but reproducible
    
    min_x, max_x = 50 * TILE_SIZE, (MAP_WIDTH - 10) * TILE_SIZE
    min_y, max_y = 50 * TILE_SIZE, (MAP_HEIGHT - 10) * TILE_SIZE
    
    # Mines (buildings) - squares, max 3 workers each
    for _ in range(20):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        gold_node = ResourceNode(x, y, 'gold', 800)
        self.resource_nodes.append(gold_node)
    
    # Forests (obstacles) - trees block movement
    for _ in range(60):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        wood_node = ResourceNode(x, y, 'wood', 150)
        self.resource_nodes.append(wood_node)
```

**Lesson:** Mines render as squares (48x48) like buildings. Forests render as trees and block unit movement.

### Map Bounds Verification for Resources

**Symptom:** Resources not visible or unreachable.

**Root cause:** Resource generation bounds exceed actual map dimensions. Common when MAP_WIDTH/MAP_HEIGHT are changed but resource bounds use hardcoded values.

**Fix:** Always derive bounds from actual map constants:
```python
# CORRECT - derived from map constants:
min_x, max_x = 50 * TILE_SIZE, (MAP_WIDTH - 10) * TILE_SIZE
min_y, max_y = 50 * TILE_SIZE, (MAP_HEIGHT - 10) * TILE_SIZE

# WRONG - hardcoded bounds may exceed map:
min_x, max_x = 50 * TILE_SIZE, 350 * TILE_SIZE  # 350 may exceed MAP_WIDTH!
```

**Debug tip:** Verify generation bounds match map dimensions:
```python
print(f"Map size: {MAP_WIDTH}x{MAP_HEIGHT} tiles = {MAP_WIDTH*TILE_SIZE}x{MAP_HEIGHT*TILE_SIZE} pixels")
print(f"Resource bounds: {min_x}-{max_x}, {min_y}-{max_y}")
assert max_x <= MAP_WIDTH * TILE_SIZE, "Resources generated outside map!"
```

**Lesson:** Always check that resource generation bounds are within actual map dimensions. Hardcoded values like `350 * TILE_SIZE` will fail if MAP_WIDTH is smaller.

### Mine Worker Assignment

**Pattern:** Gold mines accept max 3 workers for efficient harvesting.

```python
class ResourceNode:
    def assign_worker(self, worker) -> bool:
        """Assign worker to mine (max 3)."""
        if not self.is_mine:
            return False
        if len(self.assigned_workers) >= 3:
            return False
        if worker not in self.assigned_workers:
            self.assigned_workers.append(worker)
            return True
        return False
```

**Lesson:** Check `can_assign_worker()` before assigning to avoid overloading mines.

### Forest Collision & Cutter Mode

**Pattern:** Trees block units unless unit has `can_cut_trees` flag enabled.

```python
class Worker(Unit):
    def __init__(self, ...):
        self.can_cut_trees = False  # Toggle with right-click on forest

class CollisionSystem:
    def _check_forest_collision(self, unit):
        """Check collision with forests."""
        for node in self.resource_nodes:
            if node.resource_type != "wood" or node.is_depleted():
                continue
            # Allow passage if cutter mode enabled
            if getattr(unit, 'can_cut_trees', False):
                continue
            # Push unit away from tree
            dx = node.x - unit.x
            dy = node.y - unit.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance < node.radius + unit.radius:
                push_x = (dx / distance) * (node.radius + unit.radius - distance)
                push_y = (dy / distance) * (node.radius + unit.radius - distance)
                unit.x += push_x
                unit.y += push_y
```

**Lesson:** Toggle cutter mode with right-click on forest node.

### ResourceNode Class Import Pitfall

**Symptom:** `AttributeError: 'ResourceNode' object has no attribute 'radius'`

**Root cause:** Multiple versions of `ResourceNode` exist in the codebase:
- `systems/economy.py` - Old version (no `radius`, simple circles)
- `entities/resource_node.py` - New version (has `radius`, supports worker assignment, forest collision)

**Fix:** Always import from `entities.resource_node`:
```python
# CORRECT:
from entities.resource_node import ResourceNode

# WRONG (old version without radius):
from systems.economy import ResourceNode
```

**Lesson:** Check for multiple ResourceNode implementations before using. The `entities/` version is the current working version with all features.

### Resource Node Rendering by Type

**Pattern:** Different visual representation for mines vs forests.

```python
def draw(self, screen, camera_x, camera_y):
    screen_x = int(self.x - camera_x)
    screen_y = int(self.y - camera_y)
    
    if self.resource_type == "gold":
        # Mine: square like building (48x48)
        pygame.draw.rect(screen, (255, 215, 0), 
                       (screen_x - 24, screen_y - 24, 48, 48))
        # Show worker count
        if self.assigned_workers:
            text = f"{len(self.assigned_workers)}/3"
            screen.blit(font.render(text, True, (255, 255, 255)), 
                       (screen_x - 8, screen_y + 24))
    
    elif self.resource_type == "wood":
        # Forest: tree with trunk and foliage
        pygame.draw.rect(screen, (101, 67, 33), (screen_x - 4, screen_y, 8, 15))
        pygame.draw.circle(screen, (34, 139, 34), (screen_x, screen_y - 10), 12)
```

**Lesson:** Mines are square (building-like), forests are circular/tree-shaped (obstacle).

### Worker Auto-Gathering System

**Symptom:** Workers not moving to resources or dropping off at Town Hall.

**Root cause:** Type mismatch in auto-gather check - code checks for `"scout"` but workers have `unit_type == "worker"`.

**Fix:** Ensure type checks match actual unit types:
```python
def _auto_gather_resources(self):
    for unit in self.units[:]:
        # CORRECT: Check for "worker" type
        if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
            if not hasattr(unit, 'target_resource') or unit.target_resource is None:
                # Find nearest resource
                ...
```

**Lesson:** Always verify unit types match between definition and checks. Common mistake: checking `"scout"` when worker units are actually typed as `"worker"`.

### Auto-Gather Method Simplification

**Pattern:** Don't duplicate logic - use existing methods instead of reimplementing.

```python
# WRONG: Complex inline logic duplicating worker's resource finding
def _auto_gather_resources(self):
    for unit in self.units[:]:
        if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
            if not hasattr(unit, 'target_resource') or unit.target_resource is None:
                closest_node = None
                min_distance = 300
                # ... 40 lines of duplicate logic ...

# CORRECT: Delegate to worker's existing method
def _auto_gather_resources(self):
    for unit in self.units[:]:
        if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
            if not hasattr(unit, 'target_resource') or unit.target_resource is None:
                unit._find_and_assign_to_resource()
```

**Lesson:** When a method already exists to do what you need, call it instead of reimplementing. Reduces bugs, simplifies maintenance, and ensures consistent behavior.

### Auto-Gather Method Simplification

**Pattern:** Don't duplicate logic - use existing methods instead of reimplementing.

```python
# WRONG: Complex inline logic duplicating worker's resource finding
def _auto_gather_resources(self):
    for unit in self.units[:]:
        if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
            if not hasattr(unit, 'target_resource') or unit.target_resource is None:
                closest_node = None
                min_distance = 300
                # ... 40 lines of duplicate logic ...

# CORRECT: Delegate to worker's existing method
def _auto_gather_resources(self):
    for unit in self.units[:]:
        if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
            if not hasattr(unit, 'target_resource') or unit.target_resource is None:
                unit._find_and_assign_to_resource()
```

**Lesson:** When a method already exists to do what you need, call it instead of reimplementing. Reduces bugs, simplifies maintenance, and ensures consistent behavior.

### Worker Movement Logic Conflict

**Symptom:** Workers move erratically or stop at wrong positions.

**Root cause:** Two separate systems trying to control worker movement:
1. `_auto_gather_resources()` calls `movement_system.move_to()`
2. Game loop has inline harvest logic that also moves units

**Fix:** Consolidate worker update into single location - either in worker.py's `update()` or game loop, not both.

```python
# CORRECT: Single update path for workers
for unit in self.units[:]:
    if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
        unit.update(dt)  # Worker handles its own movement
    else:
        self.movement_system.update(unit, dt)
```

**Lesson:** Never duplicate movement control. Pick one system (worker's own update or movement system) and stick with it.

### Worker Resource Priority Logic

**Pattern:** Workers should prefer wood/food over gold mines.

```python
def _find_and_assign_to_resource(self):
    # First: find nearest wood/food within 300px
    closest_node = None
    min_distance = 300

    for node in self.game.resource_nodes:
        if node.is_depleted():
            continue
        distance = math.sqrt((node.x - self.x)**2 + (node.y - self.y)**2)
        if distance < min_distance and node.resource_type in ['wood', 'food']:
            min_distance = distance
            closest_node = node

    # Fallback: gold mine with available slots
    if not closest_node:
        for node in self.game.resource_nodes:
            if (node.resource_type == 'gold' and
                not node.is_depleted() and
                node.can_assign_worker()):
                # ... assign worker
```

**Lesson:** Workers should prioritize accessible resources (wood/food) over specialized ones (gold mines with capacity limits).

### Worker Resource Diversification by Faction

**Symptom:** All workers converge on gold mines, ignoring wood/food even when available.

**Root cause:** `_find_and_assign_to_resource()` only finds the nearest resource without considering what types the worker is already carrying. Workers repeatedly harvest the same type, starving other resource lines.

**Fix:** Phase the search — first look for a resource of a type NOT yet carried (within 1.5× distance), then fall back to nearest:

```python
def _find_and_assign_to_resource(self):
    if getattr(self, 'selected', False):
        return
    if not hasattr(self, 'game') or not self.game:
        return
    if self.carrying:  # Must deposit first
        return

    carried_types = set(self.carrying_types) if self.carrying_types else set()

    # Phase 1: prefer a type we don't have yet (diversification)
    preferred = None
    preferred_dist = float('inf')
    for node in self.game.resource_nodes:
        if node.is_depleted():
            continue
        if carried_types and node.resource_type not in carried_types:
            dist = ((node.x - self.x)**2 + (node.y - self.y)**2) ** 0.5
            if dist < preferred_dist:
                preferred_dist = dist
                preferred = node

    # Phase 2: nearest resource (fallback)
    closest = None
    closest_dist = 600
    for node in self.game.resource_nodes:
        if node.is_depleted():
            continue
        dist = ((node.x - self.x)**2 + (node.y - self.y)**2) ** 0.5
        if dist < closest_dist:
            closest_dist = dist
            closest = node

    # Choose diversified resource if within 1.5× fallback distance
    chosen = preferred if preferred and preferred_dist <= closest_dist * 1.5 else closest
    if chosen:
        self.target_resource = chosen
```

**Lesson:** Diversification logic lives in the worker's auto-assignment, not in game-level loops. The `carrying_types` list tracks what was last harvested; reset it on deposit so the next cycle picks up a different type.

### Faction-Specific Worker Bonus (max_carry_types)

**Pattern:** Some factions get workers that carry more resource types (e.g., dwarves).

```python
# In systems/factions.py, Faction.apply_worker_bonus():
def apply_worker_bonus(self, worker):
    for attr, value in self.worker_bonus.items():
        if hasattr(worker, attr):
            current = getattr(worker, attr)
            if isinstance(current, (int, float)) and isinstance(value, (int, float)):
                setattr(worker, attr, current + value)
            elif attr == "max_carry_types":
                worker.max_carry_types = getattr(worker, 'max_carry_types', 2) + value
```

**Lesson:** `max_carry_types` is a per-faction bonus. Base workers carry 2 types; dwarves get +1 → 3 types (gold, wood, food). The diversification logic in `_find_and_assign_to_resource()` uses this attribute to decide when to reset `carrying_types` after deposit.

### Worker Drop-off Point Assignment

**Pattern:** Workers need a drop-off point to deposit resources.

**Fix:** Find the nearest building of the same faction (any type), not just Town Halls:

```python
def _find_drop_off_point(self):
    """Find closest building of same faction."""
    if not hasattr(self, 'game') or not self.game:
        return

    closest_building = None
    closest_distance = 500  # Search radius

    for building in self.game.buildings:
        if building.faction != self.faction:
            continue

        dx = building.x - self.x
        dy = building.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < closest_distance:
            closest_distance = distance
            closest_building = building

    # Use nearest building as drop-off point
    if closest_building:
        self.drop_off_point = closest_building
```

**Lesson:** Workers should deposit at the nearest building of their faction, regardless of building type. Don't hardcode specific building types like "town_hall".

### Selected Worker Must Finish Its Full Cycle

**Symptom:** Player selects a worker and right-clicks a resource, but the worker never deposits — it carries the load to the drop-off and then goes inert, so resources never accumulate. The auto-gather loop "works" while unselected but collapses once selected.

**Root cause:** An early `return` at the top of `Worker.update()` gated on `self.selected`. That early return sits BEFORE the deposit logic, so a selected worker that reaches the drop-off never runs `_deposit_resources()`. The carry/deposit/return loop dies as soon as the player touches the worker.

**Fix:** Pilot the worker by an explicit resource target, but do NOT early-return the whole update. Let the selected worker run the SAME complete cycle (move → harvest → move to drop-off → deposit → return) as an unselected one. Gate ONLY the resource *searching* (`_find_and_assign_to_resource`) on `selected` — not the whole update:

```python
def update(self, dt):
    # ... timers, mood ...
    # NO early `if selected: return` here — deposit must always run.

    if self.carrying and not self.drop_off_point:
        self._find_drop_off_point()          # any same-faction building
    if self.is_moving and self.move_target:  # single movement block
        ...move toward target...
    # harvest / deposit / combat logic, unchanged for selected workers

def _find_and_assign_to_resource(self):
    if getattr(self, 'selected', False):
        return  # only stops NEW auto-assignment; manual target stays
```

**Lesson:** A `return` before the deposit logic is the classic worker-loop bug — it makes workers carry forever without accumulating. Gate *discovery* on `selected`, never the *lifecycle* (which owns deposit + return-to-resource). A selected worker must still finish gather → carry → deposit → go back. Also ensure there is exactly ONE movement block in `update()`; a second redundant block that clears `move_target` on arrival will also abort the return leg.

### Resource Accumulation Pattern

**Pattern:** Workers deposit resources by calling economy.add_resources().

```python
def _deposit_resources(self):
    if self.carry_amount > 0:
        if self.target_resource and hasattr(self.target_resource, 'resource_type'):
            resource_type = self.target_resource.resource_type
            if resource_type == "gold":
                if hasattr(self, 'game') and self.game and hasattr(self.game, 'economy'):
                    self.game.economy.add_resources(gold=self.carry_amount)
            elif resource_type == "wood":
                if hasattr(self, 'game') and self.game and hasattr(self.game, 'economy'):
                    self.game.economy.add_resources(wood=self.carry_amount)
            elif resource_type == "food":
                if hasattr(self, 'game') and self.game and hasattr(self.game, 'economy'):
                    self.game.economy.add_resources(food=self.carry_amount)

        # Reset carrying state
        self.carrying = False
        self.carry_amount = 0
```

**Lesson:** Always check `hasattr(self, 'game')` before accessing economy. Don't require drop_off_point to exist - deposit resources directly when carry_amount > 0.

### Building Name Display

**Pattern:** Show building type name centered on the building for identification.

```python
def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
    # ... existing drawing code ...

    # Display building name in center
    try:
        import pygame as pg
        font = pg.font.Font(None, 16)
        type_name = self.building_type.replace("_", " ").title()
        text_surface = font.render(type_name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_x, screen_y))
        screen.blit(text_surface, text_rect)
    except Exception:
        pass
```

**Lesson:** Add building type labels for player identification. Convert snake_case to Title Case and replace underscores with spaces.

### Movement System AttributeError Fix

**Symptom:** `AttributeError: 'BuildingProgress' object has no attribute 'hp'`

**Root cause:** Movement system tries to access `.hp` on any target without checking if it exists.

**Fix:** Always check hasattr before accessing target attributes:
```python
# In systems/movement.py
def update(self, unit: Unit, dt: float):
    # Check whether the unit can attack
    if unit.target and hasattr(unit.target, 'hp') and unit.target.hp > 0:
        # ... attack logic
```

**Lesson:** Movement system targets can be non-unit objects (BuildingProgress, ResourceNode). Always use `hasattr()` checks before accessing target attributes.

### Melee Units Never Land a Hit

**Symptom:** Melee units (warrior/knight/scout) chase enemies but never deal damage — combat never resolves, kills never happen despite a correct combat loop.

**Root cause:** The collision-separation force is LARGER than the melee attack range. Units are pushed apart faster than they can close, so `distance <= range` is never true.

**Fix:** Make melee `range` comfortably exceed the collision separation (`separation_distance + attacker.radius + target.radius`). For the default separation of 25px and radii of 12: separation ≈ 49px, so set melee range to 64, not 32. Also let ranged/melee attacks use `range + target.radius` when checking reach so building targets (larger radius) are hittable:
```python
if distance <= unit.range + getattr(unit.target, 'radius', 0):
```

**Diagnosis tip:** When "units never kill anything," compute `separation_distance + radius_a + radius_b` and compare it to the unit's `range`. If separation > range, the swing is physically impossible. This is why isolated combat tests pass but full-game combat fails — the loop calls collision resolution that the unit-test harness omits. Reproduce with full `game.update()` (collision active), not a hand-rolled movement-only harness.

### XP/Level Attribution via killed_by

**Pattern:** To award XP to the unit that lands the killing blow, thread the attacker through damage:

```python
# Unit/Building
def take_damage(self, damage, attacker=None):
    self.hp -= damage
    if attacker is not None:
        self.killed_by = attacker

# Movement system passes attacker on every hit:
unit.target.take_damage(unit.damage, attacker=unit)

# In game.update() when a unit/building dies:
if unit.killed_by is not None and unit.killed_by in self.units:
    xp = unit.killed_by.xp_on_kill(unit)
    unit.killed_by.gain_xp(xp)
    unit.killed_by.kills += 1
```

**Lesson:** XP is only attributable if the attacker propagates through `take_damage`. Level-up (`gain_xp`/`level_up`) must also restat the unit (damage, max_hp, armor) or higher levels are cosmetic. Include enemy buildings in the destroy path — right-click must set `target` on enemy buildings and the game loop must remove/buildings handle dead buildings, or the player "cannot destroy buildings."

### Population Display Fix

**Symptom:** Population shows 0/0 or incorrect values

**Root cause:** `get_max_population()` called with empty list instead of actual buildings

**Fix:** Pass buildings to HUD when drawing:
```python
# In game.py draw()
self.hud.draw_resources(self.economy, self.units, self.buildings)

# In hud.py
def draw_resources(self, economy, units=None, buildings=None):
    max_pop = economy.get_max_population(buildings or [])
```

**Lesson:** HUD methods need game state passed explicitly. Don't assume access to game attributes.

### Production System Key Bindings

| Key | Action |
|-----|--------|
| W | Produce worker (30 gold, 15 wood, 5 food) |
| J | Produce builder (40 gold, 20 wood, 5 food) |
| B | Open/close build menu (select a building by category, then click to place) |
| 1-6 | Produce the SELECTED building's unit at that index (skips prereq-locked units) |
| T | Research (requires a research building selected: academy/temple/workshop) |
| Click | Select/place building; click empty ground or ESC deselects building |

**Lesson:** Production is building-centered — 1-6 produce from `_selected_building`, not a global roster. B is a menu, not a cycle-through switch. T does nothing useful without a research building selected (see the workflow reference for messages/UX).

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

## Related References

- [Mountain_Roy RTS Workflow](references/mountain-roy-workflow.md) - Project structure, worker auto-gathering system, building selection/interaction, and common pitfalls

### Method Signature Compatibility in Pygame Inheritance

**Symptom:** `TypeError: Hero.draw() takes 2 positional arguments but 4 were given` when calling a subclass method that was overridden with a different signature than the parent.

**Root cause:** Child classes override parent methods but change the parameter list. The game loop calls all entities through the parent interface (`unit.draw(screen, camera_x, camera_y)`), so any subclass must match the signature.

**Fix:** Always match the parent class method signature when overriding:
```python
# Parent class (Unit)
def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
    """Draw unit on screen."""
    ...

# Child class (Hero) - MUST match signature
def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
    """Draw hero on screen."""
    # Now safe to call via parent interface
```

**Lesson:** In Pygame entity hierarchies, drawing methods are polymorphic — the game loop calls `entity.draw(screen, cx, cy)` on all entities. If a subclass changes the signature, it breaks at runtime even though the code compiles. Always match parent signatures when overriding, or use `*args, **kwargs` to accept any call pattern.

**Diagnosis tip:** When you see "takes N positional arguments but M were given" for a draw/update method, check if a subclass recently changed its signature. The fix is almost always adding the missing parameters with default values.

### Partial Refactor Leaves the Suite Red: factory kwargs, removed base methods, changed timing

**Symptom:** after an uncommitted refactor, many test modules at once fail with `X.__init__() got an unexpected keyword argument 'param'` and/or `'super' object has no attribute 'method'`. These are the two signature of an in-progress inheritance/architecture change, not N unrelated bugs.

**Before touching any code on a repo with uncommitted work, map the actual state first:** `git diff --stat` + run the FULL suite. Notes from earlier sessions are stale the moment a tree is mid-refactor; the diff shows the real breakage pattern.

**Root cause A — a factory threads a new kwarg into subclass constructors that don't accept it** (`create_unit(..., game=game)` while every subclass is `def __init__(self, x, y, faction=`). Fix by assigning the attribute AFTER construction (`unit = unit_class(x, y, faction); unit.game = game`) instead of editing every subclass signature — one-line, minimal blast radius, and the base class tolerates the attribute.

**Root cause B — the refactor deleted/renamed a base method that subclasses still call via `super()`** (`Worker.to_dict()` calls `super().to_dict()` but `Unit.to_dict` was removed). Fix by RESTORING the base method to its prior shape, not by inlining it into each subclass — every `super()` site resolves at once.

**Root cause C — an intentional behavior change invalidates old single-frame unit tests.** A timed gate (e.g. harvest requires `harvest_progress >= 1.0`) makes a one-frame `obj.update(0.016)` assert nothing happened. Update the TESTS to drive frame loops until the transition completes and assert the END state (`loop update until obj.carrying`, compare post-completion `carry_amount`), preserving the assertion's intent. Do not revert the design to satisfy an outdated test — the test is what encodes the old contract.
