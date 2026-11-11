# Headless testing of an interactive terminal game

Terminal games are loop-blocking and full-screen, so tests never type into a
real console. Replace the terminal with a scripted double, and drive the game
object's API for anything that does not need key routing.

## The terminal double

```python
class FakeTerm:
    def __init__(self, keys=()):
        self.keys = list(keys)
        self.frames = []
    def draw(self, lines):      self.frames.append(list(lines))
    def clear(self):            pass
    def hide_cursor(self):      pass
    def show_cursor(self):      pass
    def getkey(self):
        if not self.keys:
            raise RuntimeError("no more scripted keys")
        return self.keys.pop(0)
```

`frames` gives assertions on the last rendered screen (death box, ending box,
inventory). Empty key list must raise loudly — a silently returning `"q"` hides
infinite loops.

## Assertions worth writing (each one caught a real bug)

1. **Frame geometry for every level**: `len(frame) == 28` and
   `visible_len(line) == 79` for all lines; strip ANSI with the same regex the
   renderer uses.
2. **World connectivity across seeds**: for every level and ~30 seeds,
   flood-fill walkable tiles from the spawn; assert the stairs and every
   objective chest are reachable. Catches corridors carved through walls and
   rooms generated in the wrong order.
3. **N simulated turns**: random moves + occasional `interact()`, drawing the
   frame each turn — this is where index errors, `None` panels and ANSI padding
   blow up.
4. **Rules through the API**: put a strong weapon in inventory and step into a
   monster; place the player on the chest and call `open_chest`; set `boss.hp`
   to 1 for the finale; set fragments/insight then call the ending chooser.
5. **Persistence round-trip**: record a death, reload the save module from the
   same path in a fresh instance, compare deaths/endings and that a returning
   monster carries the recorded gear.
6. **Gating**: same finale with and without the required lore resource — assert
   the locked branch is not reachable and the unlocked one is.

## Harness hygiene

- One temp save path per test (`tempfile`, delete the file first) so runs are
  independent and the player's real `save/` is untouched.
- Assert on API state (`player.fragments`, `game.ending`, `mem.deaths`) rather
  than screen text; screen assertions belong to the geometry test.
- Keep a `preview.py` that writes plain-text dumps of title, play frame,
  inventory, death and ending screens (`re.sub` the ANSI out). Reading actual
  output is the only way to catch misaligned panels and truncated footers.
- Budget scripted keys generously: any prompt inside combat (mercy, merchant,
  shrine) consumes one, and the failure looks like a crash.
