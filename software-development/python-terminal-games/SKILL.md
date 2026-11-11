---
name: python-terminal-games
description: Use when building ASCII/terminal games in Python.
category: software-development
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [roguelike, ascii, terminal, windows, ansi, game-dev, testing]
---

# Python terminal / ASCII games

## When to Use

- Building a roguelike, dungeon crawler, text adventure or any full-screen
  ASCII game in Python (new project or extending one).
- Adding a double-click `.bat` launcher for a console Python app on Windows.
- The console frame flickers, wraps, or shows raw escape codes / mojibake.
- Needing to test a key-driven game loop without a human at the keyboard.

Build turn-based, full-screen ASCII games (roguelikes, dungeon crawlers,
text adventures) that run in a real console on Windows and stay testable
headlessly. Optimise for: it launches by double-click, the frame never jitters
or wraps, and a headless harness can exercise the whole ruleset.

## Procedure

1. **Split by responsibility, not by screen.** One package: `ui` (ANSI, frame,
   keyboard), `content` (names, texts, tables), `items`, `entities` (player +
   monsters + stat tables), `worldgen` (map + FOV), `persistence` (JSON save),
   `game` (loop, turns, rendering, events, endings), plus a thin `main.py` that
   only wires terminal + save + game and restores the cursor in `finally`.
2. **Fix the frame geometry first.** Pick constants (`MAP_W`, `MAP_H`,
   `PANEL_W`) and build every line to exactly one visible width. Verify with a
   test that asserts `len(frame) == N` and `visible_len(line) == W` for every
   line, for every level. Do this before adding content — wrapping bugs are
   invisible until a long label lands in a narrow panel.
3. **Render as a list of pre-coloured strings.** `paint(text, colour)` returns
   text + ANSI; `pad(text, width)` / `truncate(text, width)` strip ANSI with a
   regex to measure. Cells return **strings**, never `(char, colour)` tuples —
   joining `c[0]` picks the ESC byte and blanks the map.
4. **Draw one frame per keypress**: `\x1b[H` then each line followed by
   `\x1b[K\r\n`, flushed once. Hide the cursor at start, show it in `finally`.
5. **Turn structure**: player action → `end_turn()` → monsters act → status
   effects (poison, regen) → random events → death check. Prompts (`ask`,
   inventory, endings) redraw the frame with an overridden footer line and
   block on a key; do not build a mode state machine for menus.
6. **Worldgen**: rooms + L corridors, then flood-fill connectivity from the
   spawn to the stairs in a test across many seeds. Reserve the stair tile,
   place the objective (key/artifact/boss) in a room that is not the spawn,
   and never place hostiles within ~6 tiles of the spawn — otherwise the player
   loses half their HP before their first real decision.
7. **Persist meta-progress to JSON beside the game** (`save/memoire.json`),
   written to `path.tmp` then `os.replace`. Keep it schema-tolerant on load:
   iterate the defaults, ignore wrong types and corrupt files, never crash a
   save game. This is what makes deaths feel like continuity (returning
   skeleton with the old gear, unlocked lore, carried insight).
8. **Headless tests** (see `references/headless-testing.md`): a `FakeTerm`
   whose `draw` stores frames and whose `getkey` pops a scripted key list.
   Driver tests call the game API directly (place player, call `open_chest`,
   set `boss.hp`, pick an ending) — faster and more reliable than simulating
   walking.
9. **Verify in a real console last**: start the game in a background pty and
   drive it with `process_manage` (`write` for a single character, `submit`
   for Enter). This is the only check that exercises `msvcrt` and the ANSI
   frame together. Kill the process afterwards.

## Windows console specifics

See `references/windows-console.md` for the VT-enable snippet, `msvcrt` key
codes, and the `chcp`/UTF-8 rules. Start from `templates/launcher.bat` for the
double-click launcher: UTF-8, `py -3` then `python` fallback, `mode con`, and
`pause` only on error.

## Pitfalls

- **A `.bat` must be CRLF.** `write_file` emits LF; rewrite the file with
  `open(p,'rb').read().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')` before
  declaring it done. Labels and `goto` misparse on LF-only files.
- **From git-bash, launch a `.bat` with `cmd.exe /c file.bat`.** `cmd //c …`
  gets path-mangled and drops you into an interactive prompt that looks like a
  hung program.
- **Hotkeys live in the same namespace as the movement keys.** `j` is
  move-down in a hjkl scheme, so `if low == "j": open_journal()` placed after
  the KEYMAP check silently never fires (and a `j` reachable only in one mode
  makes it worse). Grep the KEYMAP before binding any menu letter, and use
  letters outside it (`i` sac, `o` journal, `r` wait).
- **One counter, one owner.** Mirroring `fragments` on both the `Game` and the
  `Player` makes the header and the side panel disagree (3/7 vs 0/7). Keep the
  run counter on the game object and write it through to the player only at
  the points that change it.
- **Meta bonuses granted every run compound.** `self.souvenirs = stored +
  bonus` then `stored = self.souvenirs` grows the pool each restart. Grant a
  legacy/perk bonus once (persisted `legacy_grants` list) and let the stored
  value be the only source of truth.
- **Dataclass positional-argument drift**: adding a field (e.g. `stack`) to an
  item dataclass silently turns every positional extra into that field, so a
  "potion effect" becomes a string `stack` and `item.stack -= 1` raises. Pass
  keyword arguments for dataclasses with more than ~4 fields, or build items
  through factories only.
- **An interaction that consumes no turn can soft-lock a scripted player.**
  When `interact()` scans neighbouring features it must skip exhausted ones
  (used shrine, opened chest, already-found secret) and pick the first *usable*
  one — otherwise standing between a spent shrine and a readable stele just
  re-opens the stele forever, no turn passes, and an autoplay harness spins to
  its key cap. In a mode with no exit (a final chamber), filter `exit` features
  out of the candidates or the player re-opens a door that is already shut.
- **Any in-combat prompt eats a key.** Mercy/parley dialogs fire mid-attack;
  scripted test key queues must contain plenty of `n` or the harness dies with
  "no more keys".
- **Do not show remembered monsters or loot in fog.** Explored tiles render dim
  decor only; monsters/items appear only inside the current FOV, otherwise the
  map leaks live positions.
- **Frame height is easy to miscount**: `top + title + sep + map + sep + status
  + sep + 3 log lines + sep + help + bottom` = 28 for 16 map rows. Assert the
  number, do not eyeball it.
- **Blocking on descent only when a monster is adjacent**, not merely visible —
  a "can't descend" rule keyed on line-of-sight strands the player next to
  harmless wanderers.
- **Renaming the game hits several hardcoded surfaces, not one constant.** The
  title is duplicated in `lore.TITLE` (title screen), as a literal in
  `game.frame()`'s header (often NOT derived from `lore.TITLE`), in
  `ui.Terminal`'s `SetConsoleTitleW`, the launcher `.bat` `title` line, and the
  `main.py` / `__init__.py` docstrings. After any rename, grep the OLD title
  string across the whole tree and fix every hit; then derive the frame header
  from `lore.TITLE` so the next rename is a one-line edit.
- **Anti-duplication needs a registry keyed on object identity, not on the
  id string alone.** A central `ItemManager` maps `item_id -> id(obj)` and
  refuses a claim when the id is known but the Python object differs — that
  catches the real bug (a deserialised copy) without blocking a legitimate
  move of the same object between inventory, ground and equipment. Keep a
  tombstone set for destroyed ids, and give loaders a separate `restore()`
  entry point: after a save/reload the objects are new instances with the old
  ids, so the normal `claim()` correctly rejects them during an in-session
  reload. Re-adding an object already in the same list must also be refused,
  or a ground pickup pushes the same object twice.
- **A companion needs its own inventory object, not a flag.** Subclass `list`
  into an `Inventory(owner, capacity, location)` whose `add()` claims through
  the manager and whose `append()` still registers (old code kept calling
  `append`); ownership mismatches return a readable refusal instead of an
  exception. Same for `Equipment`, whose `equip()` must remove from the bag
  *before* claiming the slot and hand the old item back to the bag.
- **Loot attribution belongs to the generator, guarded by a flag on the
  monster.** Generate drops once in `roll_loot(monster, owner, ...)` and set
  `monster.loot_generated = True` on the first call; a second call returns
  `[]`. Fighters pass `killer` into `on_monster_death(mon, killer=...)`, so a
  familiar kill routes to `on_familiar_kill` and never to the player's counter.
- **Put shared companion behaviour in a mixin, not copied per chapter.** Three
  chapters with the same `player/monsters/dungeon/ground/rng/log/modal` API
  share one `FamiliarField` mixin (`load/save/place/pickup/attack/turn/menus`);
  each chapter only wires `load_familiar()` in `new_run`, `place_familiar()`
  where it spawns the player, `familiar_turn()` at the end of `end_turn`, the
  glyph in `_cell` and the status suffix. Copying that block per chapter both
  duplicates work and drifts.
- **New item names overflow fixed-width panels.** A rarity suffix ("… ancienne")
  or a two-character marker added to a map cell breaks the frame by one column
  and the width assertion fires far from the cause. Truncate every item label
  the panel prints, and keep map cells at exactly one visible character
  (change the colour to flag ownership, not by prefixing a symbol).
- **Substring-based effect dispatch must match the stored key slug, not the
  concept name.** When `use_item` branches like `if "wisdom" in item.key`, the
  key the factory actually stored is the short slug (`p_sagesse`), so matching
  the conceptual effect label (`wisdom`) silently does nothing and the potion
  no-ops. Read the exact `f"p_{key}"` the factory builds and match a substring
  of that slug (or match the full key).

## Conventions for this user

- Game text and UI in French; report back in French, short: what was built,
  what was verified with real output, what remains.
- Ship the launcher with the game (`.bat` at the project root) and a README
  listing controls, mechanics and the test command.
- Prove it: run the test suite and paste the pass count, then actually launch
  the game. Do not claim a playable game without a real console run.
