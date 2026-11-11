---
name: pygame-debugging
category: root
description: 'Debug Pygame apps: fog of war, state flow, DPI issues.'
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [pygame, debugging, windows, rendering, fog-of-war]
---

# Pygame Debugging Guide

## When to Use

- Game or application won't start or shows black screen
- Units/buildings not visible at startup
- Input events not responding
- Display issues on Windows

## Critical: Pygame Version Requirement

**This system requires pygame 2.2.0, NOT 2.6.1.**

```bash
# Check current version:
.venv/Scripts/python.exe -c "import pygame; print(pygame.ver)"

# Downgrade if needed:
.venv/Scripts/pip.exe install pygame==2.2.0 --only-binary=:all:
```

**Symptom of wrong version:** `SystemError: <built-in function get> returned a result with an exception set` when calling `pygame.event.get()`.

**Lesson:** Always verify pygame version after creating or updating venv. The Hermes agent venv has 2.6.1 which is incompatible.

## Common Pitfalls

### 1. Coordinate Conversion (Map vs Screen)

**Symptom:** Units/buildings not visible or drawn off-screen.

**Root cause:** Drawing entities using map coordinates instead of screen coordinates.

**Fix:** Convert map coords to screen coords before drawing:
```python
screen_x = int(self.x - camera_x)
screen_y = int(self.y - camera_y)
pygame.draw.circle(screen, color, (screen_x, screen_y), radius)
```

### 2. Mouse Input Not Matching Entity Positions

**Symptom:** Clicking on units doesn't select them, right-click movement goes to wrong location.

**Root cause:** Mouse coordinates are in screen space, but entity positions are in map space.

**Fix:** Always convert mouse position to map coordinates:
```python
# In event handlers for MOUSEBUTTONDOWN/MOUSEMOTION/MOUSEBUTTONUP:
map_x = event.pos[0] + camera.x
map_y = event.pos[1] + camera.y
```

**Lesson:** Camera offset must be applied to ALL mouse input, not just drawing. This includes selection boxes, movement targets, and resource clicks.

### 3. Fog of War Hiding Starting Area

**Symptom:** Game starts but player units and buildings are invisible.

**Root cause:** `fog_of_war.update()` called before player entities exist or camera positioned.

**Fix:**
```python
# After creating entities and positioning camera:
self.fog_of_war.update(self.units, self.buildings)
```

### 4. Game State Flow Requirements

Pygame games often require specific input sequences to progress:

```
menu → click button → mission_screen → press SPACE → playing
```

**Debug tip:** If game appears stuck, check current state and whether required input was processed.

### 5. DPI Scaling Issues on Windows

**Symptom:** Window appears off-screen or black.

**Fix:** Set environment variables BEFORE `pygame.init()`:
```python
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
os.environ['SDL_VIDEO_CENTERED'] = '1'
os.environ['SDL_VIDEO_HIGHDPI_DISABLED'] = '1'
```

### 6. Display Surface Reuse

**Symptom:** Second window created or silent failure.

**Fix:**
```python
self.screen = pygame.display.get_surface() or pygame.display.set_mode((WIDTH, HEIGHT))
```

### 7. Missing display.flip()

**Symptom:** Black screen despite rendering.

**Fix:** Ensure game loop calls `pygame.display.flip()` after drawing.

## Debugging Workflow

1. **Check state:** Print current game state and entity positions
2. **Verify visibility:** Check if fog_of_war shows entities as visible
3. **Confirm screen coords:** Calculate map-to-screen conversion
4. **Test input flow:** Verify event handling for state transitions
5. **Isolate rendering:** Draw simple shapes to verify display works

## Règles actionnables (extraites du détail, vérifiées en jeu)

- **Un seul chemin de mouvement par unité.** Deux blocs qui pilotent `move_target` se neutralisent ;
  un `return` placé avant le dépôt fait porter les ressources à vie.
- **Mêlée : `range` doit dépasser la séparation de collision** (25 + 2×12 ≈ 49 px → range 64).
  Sinon `distance <= range` est inatteignable et aucun coup ne part, alors que les tests unitaires
  isolés passent (le harnais n'applique pas la collision).
- **Récolte temporisée** : `harvest_progress >= 1.0`. Un `update(0.016)` unique ne produit rien ;
  les tests doivent boucler les frames jusqu'à la transition et asserter l'état final.
- **`hasattr(target, 'hp')` avant tout accès** : les cibles peuvent être `BuildingProgress` ou
  `ResourceNode`, pas seulement des unités.
- **XP seulement si `killed_by` est propagé** dans `take_damage(damage, attacker=...)` ; un
  level-up qui ne restate pas (damage/max_hp/armor) est cosmétique.
- **Surcharge polymorphe** : `draw()`/`update()` d'une sous-classe doivent garder la signature du
  parent, sinon `TypeError` au dispatch de la boucle de jeu.
- **Refactor partiel** : `git diff --stat` + suite complète AVANT de toucher ; `create_unit` affecte
  `.game` après construction ; restaurer une méthode de base supprimée plutôt que l'inliner.

## Quick Reference

| Issue | Check |
|-------|-------|
| Black screen | State, fog_of_war visibility, display.flip() |
| Invisible units | Camera position, entity coords, fog update |
| Input not working | Event handling, state checks, key constants |
| Off-screen window | SDL env vars, DPI settings |
| Resources not depleting | Check amount/max_amount tracking |
| Resources not regenerating | Verify resource_type and is_depleted() check |
| Workers not gathering | Check unit_type == "worker" (not "scout") |
| Erratic worker movement | Check for duplicate movement control |


## Related References

- `references/mountain-roy-workflow.md` — cycle de vie des systèmes RTS (workers, bâtiments, boucle).
- `references/mountain-roy-pitfalls.md` — oracle de bugs : symptôme → cause → correctif → leçon
  (récolte, mouvement, mêlée, XP, HUD, signatures, refactor partiel).
Le détail DPI/fenêtre reste volontairement inline ci-dessus (moins de 30 lignes) ; si un futur
besoin le fait grossir, l'extraire dans un fichier de référence plutôt que gonfler ce SKILL.md.
