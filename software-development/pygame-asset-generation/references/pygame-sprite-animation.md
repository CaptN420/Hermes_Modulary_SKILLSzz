# Slicing & Animating Pygame Spritesheets (project style)

Recipe for turning raw spritesheets into per-state animations drawn over an unchanged physics rect — the PyBR0S player pipeline (Martial Hero 2 via `core/sprite_animator.py`).

## Slicing
- Sheets are single-row bands of square frames `frame_h` px tall (Martial Hero): `nframes = width // frame_h`. BUT the Samurai pack (and many others) is NOT a single band — see "Layout detection" below.
- Per frame: `sheet.subsurface((i*frame_h, 0, frame_h, height))` → crop to the NON-TRANSPARENT bbox (measure with `pygame.mask.from_surface(...).get_bounding_rects()`) → `pygame.transform.smoothscale` so final height == target (~60) with ratio kept. Result ~35-56px wide x 60 tall for a 40x60 rect.
- Cropping to the content bbox matters: e.g. Martial Hero frames are 200x200 but the character occupies ~33x56, so full-frame scaling wastes resolution.
- Precompute all scaled frames once in `__init__`; `get_image(state, frame, facing)` only indexes and flips.

### Layout detection — NEVER guess (fw, fh) on a pack you didn't author
Free packs are packed irregularly, and guessing the frame size produces two silent visual bugs that pass tests:
- **Stacked-sprite collapse** (character shrinks to a sliver in one state): slicing a 2-row grid at the FULL height packs two stacked sprites into one cell (e.g. run sheet 3x2 of 16x16 read as 3 frames of 16x32). The crop becomes one narrow deformed figure — idle 54px, run 22px. Symptom: the state's rendered width collapses ~half.
- **Composite blink** (sprite flickers during an animation): reading all N non-empty cells row-major from a sheet that contains several sub-animations jumps between unrelated poses.
Measurement procedure before writing any (fw,fh):
1. For each candidate cell, union `pygame.mask.from_surface(cell).get_bounding_rects()` and print `x,y,w,h`. True frames are roughly `height*0.6+` tall; tiny/partial bboxes are fragments or a different pose set — they tell you the real grid.
2. To find the ONE coherent sub-animation inside a composite, build a 3x3 per-region alpha count signature per cell (`pygame.mask.from_surface(surf.subsurface(rect)).count()`) and diff consecutive window members. A real stroke has diffs <~15; a sub-animation boundary shows a jump >~100. Pick the lowest-diff contiguous window as the swing.
3. Support exposing a coherent window: give the state's grid config an optional subset of flat row-major cell indices (e.g. `attack1: ("Attack_1.png", 48, 48, (13,14,15,16,17))`) and have the loader select `[cells[i] for i in subset]` after building the full grid. Verify the animation feels complete by checking frame widths stay near idle's.
4. Some packs ship separate files per state (`Samurai_Bundle`: Idle/Idle_1.png + Idle_2.png, Run/, Hit/, Jump/, Death/, Attack/Attack_1, Attack/Attack_2) — list the directory before assuming one sheet holds everything. Know these measured layouts: Samurai idle=two 32x32; jump/fall=one 48x48; death=3 columns of 32x48 (NOT 2x48); run=3x2 grid of 16x16; attack1=5x4 grid of 48x48 (use a coherent subset); attack2=4x2 of 48x48 (top row).

## Animation-state mapping (READ-ONLY)
Map existing entity flags to an animation name by priority: `is_dead` > `hitstun`/`stun_timer` > `attack`/`attack_timer` (>18 → heavy else light) > not `is_grounded` (vel.y<0 jump else fall) > `|vel.x|>0.5` run > idle. Read flags only; never change gameplay to drive the animator.

## Frame timing — drive ATTACK frames from the gameplay timer, others from wall-clock
- Idle/run/fall/hurt/jump/death: drive from `pygame.time.get_ticks()` in the renderer — on state change reset frame to 0; else `frame += dt_s * rate`; loop (modulo) for idle/run/fall, clamp to last frame (non-looping) for hurt/jump/death. Store `{state, frame, last_tick}` on the renderer.
- Attack frames: a fixed `FRAME_RATES[attack]` (e.g. 16fps) makes the sword swing play at its own speed, out of sync with the real ~0.25s attack, and `player_animation` flips `attack2`->`attack1` mid-swing because the heavy/light threshold (attack_timer > 18) sits INSIDE a timer that starts at 25. Instead:
  - Capture `attack_max = p.attack_timer` when the attack state first enters; each frame map `prog = 1 - attack_timer/attack_max` onto the frame index. The swing then always completes exactly when the gameplay attack ends, for every class — no tuning per frame count.
  - Lock the attack sub-state once the swing starts: if the previously drawn state already began with "attack", keep it and ignore the flip returned by `player_animation`.
  - This is read-only over gameplay state — no damage/hitbox/knockback touched (the project's standing rule).

## Drawing
- `img = anim.get_image(state, int(frame), facing)`; flip on `facing < 0`.
- Position bottom-center of image on bottom-center of `cam.apply(rect)`: `blit_pos = (screen_rect.centerx - w//2, screen_rect.bottom - h)`. Decouples visual size from hitbox.
- Blink on `flash_timer`/`invincibility_timer`: skip a draw every ~100ms tick.
- Return a sentinel so the caller falls back to the old rectangle draw when the animator/sprite is unavailable — never crash.

## Static single-image sprites (no spritesheet) — StaticAnimator
When the asset is ONE static image (e.g. Ice Golem, 64x67 PNG) with no animation frames, do NOT invent gameplay states: use the same image for idle/move/attack/hurt/death as a clean fallback. `StaticAnimator` in `core/sprite_animator.py` implements this with an interface compatible with `SpriteAnimator` (`get_image(state, frame, facing)`, `num_frames`→1, `.loaded`, `.load_error`).

### Remove the background by FLOOD-FILL from the borders, not by keying the color
Many free static sprites ship on a solid background (e.g. white) with NO alpha channel. Naively making every pixel of that color transparent punches holes through interior pixels of the same color (an ice golem has white highlights INSIDE its body). Instead:
- Flood-fill from all four border edges, marking only pixels connected to the border that are within `tolerance` of the corner color → those become transparent. Interior same-color pixels (not connected to the border) survive.
- **The source surface may be 24-bit (no alpha)** — `set_at((x,y),(0,0,0,0))` on it silently does nothing. Build the output as `pygame.Surface((w,h), pygame.SRCALPHA)` and copy every pixel into it (transparent or original).
- Then crop to the content bbox (via `pygame.mask.from_surface`), scale to target height keeping ratio, and cache the scaled surface.
- Same fallback contract: any exception during load → `.loaded=False`, renderer falls back to the old rectangle.

## Enemy sprite integration (multi-enemy)
The enemy renderer mirrors the player: one generic `_draw_enemy_sprite(e)` called per enemy inside the `for e in self.enemies` loop, returning a sentinel so the loop falls back to the old red rectangle when the sprite is unavailable. Pass the entity so each enemy reads its own `facing` and `flash_timer` (blink per-enemy). The Ice Golem static image scales to ~57x60 over the 40x60 rect — fine, the hitbox is untouched. Enemies default `facing=-1`; read it, don't assume a player-style +1.

## Persisting the class skin across save/load (PyBR0S)
The render reads `p.rpg.class_name`, but the save layer historically wrote/read the bare `p.class_name` attribute and `reload_game` calls `reset_game(map_name)` which re-defaults `rpg.class_name` to FIGHTER — so after loading a save you get the wrong skin (or the default) even though the save file is fine.
- Save: serialize `getattr(getattr(p,'rpg',None),'class_name', p.class_name)`, not just `p.class_name`.
- Load: after `reset_game`, restore BOTH `p.class_name = saved` AND `p.rpg.class_name = saved`.
- Use the real public pathway (`save_game()` builds the `player` dict then calls `save_manager.save(data)`). Calling `save_manager.save(g)` directly or `update_player_data(...)` piecemeal bypasses the dict builder and silently drops fields like class — verify a real save->fresh-Game->load round-trip, asserting `rpg.class_name` afterwards.

## Pitfalls
- `pygame.image.load(path).convert_alpha()` raises `cannot convert without pygame.display initialized` under the SDL dummy driver (headless tests/QA). Wrap convert in try/except; use the raw surface on failure.
- Cache the animator globally and load lazily; the loader must never raise — return None so the renderer falls back.
- Heavy-attack frames can be much wider than the rect (extended arm, up to ~94px) — fine visually; the hitbox stays 40x60.
- Non-looping clamp uses `min(frame, nframes-1)` — do not modulo those states or death/hurt/attack never settle on their last pose.
