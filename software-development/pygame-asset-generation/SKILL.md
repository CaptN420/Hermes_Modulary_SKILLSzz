---
name: pygame-asset-generation
category: software-development
description: Generate pixel art sprites for Pygame games; source free/CC0 external assets.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pygame, assets, pil, pixel-art, cc0, sprites]
    related_skills: [sprite-management, pybr0s, mountain-roy]
---

# Pygame Asset Generation

Use when creating or managing sprite assets for Pygame-based games, OR when sourcing free (CC0 / commercial-use) external art & sound for a game. Covers sprite generation, loading, rendering, fallback strategies, and license-verified asset sourcing.

## Procedure

### 1. Create Sprite Directory Structure
```
mkdir -p assets/sprites
```

### 2. Generate Sprites with PIL/Pillow
```python
from PIL import Image, ImageDraw
import os

OUTPUT_DIR = 'assets/sprites'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_sprite(width=40, height=60):
    return Image.new('RGBA', (width, height), (0, 0, 0, 0))

def draw_knight():
    img = create_sprite()
    d = ImageDraw.Draw(img)
    d.rectangle([8, 5, 32, 18], fill=(100, 170, 255))
    d.rectangle([10, 18, 30, 42], fill=(85, 153, 255))
    return img
```

### 3. Load Sprites in Pygame
```python
import pygame

class SpriteManager:
    def __init__(self):
        self.player_sprites = {}
        self._load_sprites()
    
    def _load_sprites(self):
        sprite_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sprites')
        for class_name in ['knight', 'rogue', 'mage', 'heavy']:
            path = os.path.join(sprite_dir, f'player_{class_name}.png')
            if os.path.exists(path):
                self.player_sprites[class_name] = pygame.image.load(path).convert_alpha()
    
    def draw_player(self, screen, rect, class_name='knight'):
        sprite = self.player_sprites.get(class_name)
        if sprite:
            sprite_rect = sprite.get_rect().center = rect.center
            screen.blit(sprite, sprite_rect)
        else:
            pygame.draw.rect(screen, (255, 255, 255), rect)
```

### 4. Create/Activate Virtual Environment on Windows
```bash
# Clean up any old venv first
rm -rf .venv venv

# Create venv using the hermes-runtime python (Windows-compatible)
/c/Users/celes/AppData/Local/hermes/hermes-agent/.hermes-runtime/python/cpython-3.11.16-windows-x86_64-none/python.exe -m venv .venv

# Install dependencies
cd C:/Users/celes/Documents/Hermes-Workspace/PyBR0S
.venv/Scripts/pip.exe install pygame>=2.5.0,<3.0.0

# Run the game
.venv/Scripts/python.exe main.py
```

**Critical**: Do NOT use `source .venv/bin/activate` on Windows - it will fail. Use `.venv/Scripts/python.exe` directly.

### 5. Integrate with Renderer
Replace `pygame.draw.rect()` calls in renderer with sprite manager calls.

## Pitfalls

- **Windows venv creation**: The hermes-runtime python creates a proper Windows venv; the default python may create a Linux-format venv that won't work on Windows.
- **Path handling**: Use `C:/Users/...` format for native tools in MSYS bash. `/c/Users/...` gets mangled by path translation.
- **PIL vs Pillow**: Import is `from PIL import Image`, not `import Image`.
- **Fallback required**: Always provide rectangle fallback when sprites are missing - don't crash the game.
- **Sprite sizing**: Match sprite dimensions to expected rect sizes (40x60 for players, 40x50 for enemies).
- **State preservation bug**: When `reset_game()` is called with a new class, preserve the NEW class selection instead of restoring from old saved data. Check: `self.p.rpg.class_name = player_class` not `prev_data.get("rpg_class", player_class)`.
- **CLASS_SKINS key mismatch**: `CLASS_SKINS` dict keys are capitalized ("Knight", "Rogue") but RPG stores lowercase ("knight"). Always capitalize before lookup: `class_name.capitalize()` when retrieving from CLASS_SKINS, or store consistently lowercase everywhere.

## Mountain_Roy RTS Specifics

### Known Issues Fixed
- **ResourceNode lambda bug**: Dynamic types with lambdas referencing `self` fail. Use proper classes from modules instead of `type('Name', (), {...})()` with lambda methods.
- **AudioEvents method mismatch**: `on_build()` doesn't exist; use `on_building_built()` from `systems/audio.py`. Also `on_collect()` → `on_resource_collected()`.
- **Game loop missing flip()**: Always call `pygame.display.flip()` after `self.draw()` in the game loop.
- **Camera float crash**: Camera position passed as float to `range()` causes TypeError. Convert to int: `camera_x = int(camera_x)` at start of `GameMap.draw()`.
- **Window DPI scaling**: Windows DPI scaling can cut off window corners. Set before pygame init:
  ```python
  os.environ['SDL_VIDEO_HIGHDPI_DISABLED'] = '1'
  try:
      import ctypes
      ctypes.windll.shcore.SetProcessDpiAwareness(1)
  except Exception: pass
  ```
- **Window sizing**: 800x600 works reliably on all displays. 1024x768 may be cut off on high-DPI screens.
- **Display surface reuse**: Use `pygame.display.get_surface() or pygame.display.set_mode()` to avoid creating duplicate screens when display already exists.

## PyBR0S Game Flow

### Menu Navigation Sequence
1. **Start Game** → Class Select → Map Select → Play
2. **Load Game** (Continue) → Map Select → Play (preserves class from save)
3. **Select Class** menu item → Direct to class selection

### State Transitions
- `GameState.CLASS_SELECT` stores `_selected_class` for use in map selection
- `GameState.MAP_SELECT` passes `player_class` to `reset_game()`
- Load game restores class via `self._selected_class = self.p.rpg.class_name`

### Pitfall: Missing Class Selection
If "Start Game" skips to map select without class selection, player skin won't load. Always ensure:
1. Start → Class Select → Map Select → Play
2. Load → Map Select → Play (class already loaded from save)

## References

- `references/sprite-palette.md` - Color palettes for different character types
- `references/free-asset-sourcing.md` - Workflow for finding CC0/commercial-use external assets with license verification (characters, tiles, UI, effects, sounds, music)
- `references/pygame-sprite-animation.md` - Slicing spritesheets into per-state animations (incl. heterogeneous/composite grid layout detection via mask bbox + region-alpha diff), READ-only attack timing driven by the gameplay timer (fixes out-of-sync sword swing & mid-swing state flip), bottom-center drawing over an unchanged hitbox, dummy-driver pitfalls, and persisting the class skin across save/load via `rpg.class_name`
- `scripts/itch_download.py` - End-to-end itch.io free-asset downloader (POST /file/{upload_id} flow, shared cookie jar)
- `templates/sprite_generator.py` - Boilerplate sprite generation script