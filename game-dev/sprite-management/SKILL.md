---
name: sprite-management
category: game-dev
description: Load and render sprite sheets for PyBR0S characters
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pygame, sprites, rendering, pybr0s]
    related_skills: [pybr0s, pygame-asset-generation, pygame-debugging]
---

# Sprite Management for PyBR0S

## Overview
Handles loading and rendering of sprite sheets for player and enemy characters.

## Key Files
- `core/sprite_manager.py` - Main sprite loader and renderer
- `assets/sprites/pipoya/` - Sprite sheet images (96x128)

## Sprite Sheet Structure
All sprites are 96x128 PNG files containing 3x4 frames of 32x32 pixels each.

### Player Sprites
- `player_knight.png` - Knight class
- `player_rogue.png` - Rogue class
- `player_mage.png` - Mage class
- `player_heavy.png` - Heavy class

### Enemy Sprites
- `enemy_regular.png` - Regular enemies
- `enemy_elite.png` - Elite enemies
- `enemy_boss.png` - Boss enemies (288x384, 9x12 frames)

## Loading Process
1. Detect sprite sheet size (>=64x64 pixels)
2. Extract first frame using PIL crop: `(0, 0, 32, 32)`
3. Convert to pygame surface with alpha channel
4. Scale for rendering while maintaining aspect ratio

## Rendering Rules
- Target size: `max(60, rect.width * 1.5) x max(80, rect.height * 1.5)`
- Center sprite on entity rect
- Flip horizontally based on facing direction
- Hitbox remains at original entity size (40x60)

## Common Issues
- **Artifacts showing multiple sprites**: Sprite sheet not being cropped properly
- **Sprites too small**: Scaling factor needs adjustment
- **Sprites misaligned**: Center calculation may be off