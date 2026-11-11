# Windows console setup for ANSI terminal games

## Enable ANSI / VT processing

Windows 10+ supports the escape sequences the game needs, but a freshly
started `python.exe` may not have VT enabled on its stdout handle. Enable it
once at startup; failure is non-fatal because Windows Terminal already has it.

```python
def _enable_vt() -> None:
    import ctypes
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)          # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # VT_PROCESSING
```

Then `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` and set
`PYTHONUTF8=1` in the launcher. Windows Terminal + `chcp 65001` + a font with
box-drawing glyphs (Consolas, Cascadia Mono) renders `╔═╗│▓·†Φ` correctly.

## Keyboard input (`msvcrt`)

`msvcrt.getwch()` returns one character, unicode-aware, **no echo** — use it,
not `getch()`. Extended keys arrive as a prefix (`\x00` or `\xe0`) followed by
a scancode, so read twice:

| scancode | key |
|---|---|
| `H` | UP |
| `P` | DOWN |
| `K` | LEFT |
| `M` | RIGHT |
| `S` | DELETE |

`\r` → Enter, `\x08`/`\x7f` → Backspace, `\x1b` → ESC. Provide a POSIX branch
(`tty.setraw` + `termios`) so the game also runs under CI/WSL; read 2 more
bytes after ESC to decode arrow sequences.

## Frame drawing without flicker

```python
buf = ["\x1b[H"]
for line in lines:
    buf.append(line)
    buf.append("\x1b[K\r\n")
sys.stdout.write("".join(buf))
sys.stdout.flush()
```

`\x1b[K` clears leftover characters when a line gets shorter. Hide the cursor
at start (`\x1b[?25l`) and restore it (`\x1b[?25h`) in a `finally`, including
on traceback — otherwise the user's shell loses its cursor after a crash.

## ANSI colours

Use 256-colour SGR (`\x1b[38;5;{n}m`). Pick an explicit palette per biome:
walls dark (238–242), floors (245–246 or a hue), hazards red/orange, artifacts
gold, lore cyan/purple. Dim remembered geometry with a darker colour code
rather than the `\x1b[2m` attribute, which some conhost font/driver combos
ignore.

## Launcher notes

- `chcp 65001 >nul` before Python starts, plus `set PYTHONUTF8=1` and
  `set PYTHONIOENCODING=utf-8`.
- `mode con: cols=84 lines=34 >nul 2>nul` once the frame is 79×28 plus a
  blank top line; the `>nul 2>nul` keeps it working in redirected consoles.
- Resolve Python with `where py` → `py -3`, then `where python` → `python`, and
  print an install hint if neither exists. Avoid depending on a venv.
- `cd /d "%~dp0"` so double-clicking from Explorer works regardless of the
  working directory.
- Only `pause` on the error branch; a clean exit should close the window.
