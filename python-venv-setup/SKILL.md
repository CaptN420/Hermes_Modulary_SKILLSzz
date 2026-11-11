---
name: python-venv-setup
category: root
description: Create and manage Python virtual environments on Windows.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [python, venv, environment, windows, powershell]
---

# Python Virtual Environment Setup on Windows

## When to Use

- User wants to create a new Python virtual environment
- User needs to install dependencies for a project
- User wants to manage Python packages in an isolated environment

## Prerequisites

Python 3.11+ installed (verify with `python --version`).

## Procedure

### 1. Create the venv

```powershell
python -m venv .venv
```

This creates `.venv/` in the current directory.

### 2. Enable Execution Policy (if needed)

If you get an error like "cannot be loaded because running scripts is disabled":

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r path/to/requirements.txt
```

Or install specific packages:

```powershell
pip install pygame>=2.5.0,<3.0.0
```

### 4. Verify Installation

```powershell
python --version
pip list
```

### 5. Deactivate When Done

```powershell
deactivate
```

## Pitfalls

1. **Terminal tool runs bash, not PowerShell** — On Windows, the terminal tool uses git-bash/MSYS, so PowerShell commands (`Remove-Item`, `Set-ExecutionPolicy`) will fail with "command not found". Use POSIX equivalents: `rm -rf` instead of `Remove-Item`, and skip ExecutionPolicy changes if using bash.

2. **Batch files must use correct working directory** — When creating `.bat` files to run Python projects, the script must `cd /d` to the project root (where `main.py` or the package lives), not a subdirectory. Use `-m module.name` syntax rather than calling `python main.py` directly, because the module path is relative to the project root.

   **Correct pattern:**
   ```batch
   @echo off
   cd /d "C:\path\to\project_root"
   "C:\path\to\venv\Scripts\python.exe" -m package.main
   pause
   ```

   **Why:** The Python interpreter resolves module paths relative to the current working directory. If you `cd` into a subdirectory, `-m package.main` will fail because it can't find the package at the expected location.

2. **venv activation script differs by shell** — PowerShell uses `Activate.ps1`, bash uses `activate`. The terminal tool runs bash, so use `.venv/Scripts/activate` or call pip directly via `.venv/Scripts/pip.exe`.

3. **requirements.txt path must be absolute on Windows** — When using the terminal tool, pass full paths like `C:/Users/celes/Documents/project/requirements.txt` rather than relative paths that may not resolve correctly.

4. **pygame fails to build from source on Windows** — `pip install pygame` tries to compile from source and requires MSYS2/pacman which is rarely installed. Use pre-built wheels or pygame-ce instead.

5. **pygame-ce for Python 3.14+** — The original `pygame` package doesn't support Python 3.14 on Windows. Use `pygame-ce` (community fork) instead:
   ```bash
   uv pip install pygame-ce
   # or with pip:
   venv/Scripts/pip.exe install pygame-ce
   ```
   **Why:** pygame-ce 2.5.8+ provides pre-built wheels for Python 3.14 on Windows, avoiding source compilation issues.

6. **pygame display black screen on Windows** — When the window appears black or off-screen, add these environment variables BEFORE `pygame.init()`:
   ```python
   import os
   os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
   os.environ['SDL_VIDEO_CENTERED'] = '1'
   os.environ['SDL_VIDEO_HIGHDPI_DISABLED'] = '1'
   ```
   Windows DPI scaling can position the window outside the visible area.

7. **pygame.display.set_mode() creates new surface** — Calling `set_mode()` after env vars are set can create a second window or fail silently. Use `pygame.display.get_surface()` first, fall back to `set_mode()` only if no surface exists:
   ```python
   self.screen = pygame.display.get_surface() or pygame.display.set_mode((WIDTH, HEIGHT))
   ```

8. **Missing pygame.display.flip() causes black screen** — The game loop MUST call `pygame.display.flip()` after drawing. Without it, the screen stays black even though rendering happens.

9. **Dynamic type lambdas with self don't work** — Creating classes dynamically with `type('Name', (), {...})` and assigning lambda methods that reference `self` fails because lambdas capture by reference but aren't bound correctly:
   ```python
   # BROKEN - lambda receives no self
   obj.method = lambda self: self.amount <= 0

   # FIXED - use proper class from module
   from systems.economy import ResourceNode
   obj = ResourceNode(x, y, 'gold', 500)
   ```

10. **Audio fallback when mixer unavailable** — When the audio device is not available, `pygame.mixer.init()` raises `pygame.error`. Always wrap in try/except and disable audio gracefully:
    ```python
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except pygame.error:
        self.audio_enabled = False
        self.sounds = {}
        return
    ```

## Quick Reference

| Task | Command |
|------|---------|
| Create venv | `python -m venv .venv` |
| Activate (PowerShell) | `\.venv\Scripts\Activate.ps1` |
| Activate (bash) | `.venv/Scripts/activate` |
| Install deps | `pip install -r requirements.txt` |
| Deactivate | `deactivate` |
| Delete venv | `rm -rf .venv` (bash) or `Remove-Item -Recurse -Force .venv` (PowerShell) |
