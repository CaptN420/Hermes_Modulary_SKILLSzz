# Hermes Skills — 17 procedural skills (`def` profile)

Bundle of procedural skills for [Hermes Agent](https://hermes-agent.nousresearch.com): 17 skills that encode verified facts — exact paths, commands, numeric values, reproducible pitfalls — on the **PyBR0S** (Pygame fighting/RPG), **Mountain_Roy** (RTS), **Life_mean** (synthetic data lab) and **CaptN-BRAIN / Mia_Brain** projects, plus cross-cutting tooling (FastAPI, terminal games, exploratory QA, Windows venv, Hermes cron).

Repo rule: a skill is not decorative documentation. Every rule encodes a bug already paid for, with its cause and its fix, so a future session does not pay for it again.

## Installation

The Hermes loader infers the **category from the folder**, not from the frontmatter: respect the tree when copying.

```bash
git clone https://github.com/CaptN420/Hermes_Modulary_SKILLSzz.git
cd Hermes_Modulary_SKILLSzz
DEST="$HOME/AppData/Local/hermes/profiles/def/skills"   # Windows
# DEST="$HOME/.hermes/profiles/def/skills"              # Linux / macOS
cp -r game-dev software-development autonomous-ai-agents "$DEST"/
cp -r pygame-debugging python-venv-setup life-mean-dashboard-qa "$DEST"/
```

Check after copying: `skills_list()` must return the 17 names, each with its description.

## The 17 skills

| Category | Skills |
|---|---|
| `game-dev` | `pybr0s`, `sprite-management` |
| `software-development` | `pygame-asset-generation`, `mountain-roy`, `life-mean`, `life-mean-recent-lessons`, `snapshot-logic-architecture`, `captn-brain`, `team-coding-workflow`, `autonomous-decision-engine`, `dogfood-python`, `python-fastapi-apps`, `python-terminal-games` |
| `autonomous-ai-agents` | `hermes-cron-jobs` |
| root (uncategorized) | `pygame-debugging`, `python-venv-setup`, `life-mean-dashboard-qa` |

`pygame-asset-generation` is provided here but may be inactive on the Hermes side if it was archived (`.archive/` folder) — it is a bundle skill, not a dependency of the others.

## Reconstruction prompt

The complete spec below allows regenerating the bundle from scratch in a fresh session.

---


# PROMPT — Recreate the complete bundle of 17 home-grown skills (Hermes `def` profile)

Paste this prompt as-is into a fresh Hermes session (same machine, same user)
to regenerate the skills bundle developed on the PyBR0S, Mountain_Roy, Life_mean,
CaptN-BRAIN projects and the QA/dev tooling.

---

## ROLE

You are a Hermes agent that must rebuild a bundle of procedural skills from the
specification below. You write skills, not decorative documentation: every skill
encodes hard-won facts (exact paths, exact commands, reproducible pitfalls) so
that a future session does not relearn the same bugs.

## TARGET AND CONVENTIONS

- Skills root: `C:\Users\celes\AppData\Local\hermes\profiles\def\skills\`
- One skill = one folder + `SKILL.md` (+ `references/`, `scripts/`, `templates/` if listed).
- Mandatory YAML frontmatter:
  ```yaml
  ---
  name: <kebab-case-slug>
  description: <≤120 chars, format "Use when ... . <behavior>.">
  category: <software-development|game-dev|autonomous-ai-agents>
  version: 1.0.0
  author: Hermes Agent
  license: MIT
  metadata:
    hermes:
      tags: [ ... ]
      related_skills: [ ... ]
  ---
  ```
- Do NOT recreate the ~60 bundled skills (hermes-agent, github, systematic-debugging, dogfood,
  p5js, microsoft-office, etc.): they come back with the Hermes installation and are listed in
  `.bundled_manifest`. Only the 17 skills below are home-grown.
- Language: French for project skills (French-speaking user), English acceptable for
  generic tooling. Concise, imperative tone, one rule per lesson.
- Every project skill starts with: project path + "French-speaking user; concise
  replies; value = verified code that works".

- The `description` is used for **routing**: it must contain the tech, the symptom and the
  project name ("Debug Pygame apps: fog of war, state flow, DPI issues"). 120 characters is a
  ceiling, not a goal: never mutilate it to fit 60.

## EXECUTION MODE

Execute without asking for confirmation: write the files, report only at the end.
Proceed in 5 passes, with a control `skills_list()` after each (do not load the 17
at once in a single reasoning):

- **Pass 1 — PyBR0S game**: skills 1 → 4
- **Pass 2 — RTS + environments**: skills 5 → 6
- **Pass 3a — Life_mean (the heaviest)**: skills 7 → 9 — `life-mean` (+6 references),
  `life-mean-recent-lessons` (+6 references, 1 script), `life-mean-dashboard-qa`.
  One skill at a time: `SKILL.md` first, then its references; do not keep the 17 specs in mind.
- **Pass 3b — CaptN / Mia_Brain**: skills 10 → 13
- **Pass 4 — cross-cutting tooling**: skills 14 → 17

If context saturates mid-pass: finish the current skill, then resume at the next
boundary. Never leave a skill half-written — a partial skill is worse than a missing skill,
it will be loaded and mislead the next session.

If a fact in a spec looks wrong or inconsistent with the disk, do not block and do not ask:
write it as-is and list the discrepancy in the final report. A skill written with a flagged
discrepancy is worth more than a half-created bundle.

## WRITING RULES (non-negotiable)

1. No session narration, no meeting date: only the rule + the WHY.
   Single exception: a "lessons log" skill (whose description announces it as a dated journal)
   is dated per section — that is its value, and it is meant to be archived, not to last.
2. Every fact must be verifiable: path, command, numeric value, function name.
3. Explicitly flag the "looks broken but it's a stale test" and
   "passes in unit test but fails in game" pitfalls (the two classes of false diagnosis).
4. Separate: project facts (paths/constants) → project skill; reusable technical oracle
   (pygame, FastAPI, venv) → tooling skill; dated campaign lessons → "lessons" skill.
5. A skill must not exceed ~320 lines; beyond that, split into `references/<topic>.md`.

## CREATION ORDER (dependencies first)

1. `pybr0s` → 2. `sprite-management` → 3. `pygame-asset-generation` → 4. `pygame-debugging`
→ 5. `mountain-roy` → 6. `python-venv-setup` → 7. `life-mean`
→ 8. `life-mean-recent-lessons` → 9. `life-mean-dashboard-qa`
→ 10. `snapshot-logic-architecture` → 11. `captn-brain` → 12. `team-coding-workflow`
→ 13. `autonomous-decision-engine` → 14. `dogfood-python` → 15. `python-fastapi-apps`
→ 16. `python-terminal-games` → 17. `hermes-cron-jobs`

---

## SPECIFICATIONS

### 1. `pybr0s` (game-dev category)
Description: `Use when working on PyBR0S (Python/Pygame 2D fighting/RPG).`
Project: `C:\Users\celes\Documents\Hermes-Workspace\PyBR0SVARCHITECTURE-master` (v1.3).
Mandatory sections: Architecture Notes (audit), Hard-won facts, Running tests,
Verifying sprite/VFX rendering headless, File structure, Pitfalls, World Prototype Integration,
Autonomous Mode, Related Skills.
Hard facts to keep:
- Debt: `GameBaseMixin` = 864 lines / 12+ managers (god class); Player/Enemy ~70% duplicated;
  balance values scattered (`config.py`, `settings.py`, `combat_balance.py`);
  roguelite/perks/equipment untested. Good patterns to preserve: `ManagerRegistry`,
  `EventSystem`, data-driven design.
- Per-class skins: `core/sprite_animator.py`, `get_player_animator(class_name)` lazy + cached,
  `.upper()`-normalized; Knight→Samurai, Rogue→Martial Hero 2 (fallback), Mage→Martial Hero,
  Heavy→StaticAnimator, unknown→Rogue (never None). States idle/run/attack1/attack2/hurt/jump/
  fall/death, idle fallback. Enemies = Ice Golem via `StaticAnimator`. 40x60 rect unchanged,
  bottom-center anchoring, flip by `facing`, rectangle fallback.
- Asset rule: modify ONLY rendering/audio; never hitbox, damage, save, balance.
  367-test suite green BEFORE and AFTER.
- Combat: `DamageSystem.apply_damage(target, dmg, direction)` expects a SCALAR direction
  (a Vector2 breaks `apply_knockback`); armor absorbs BEFORE HP → a hit under ~30 armor
  leaves HP intact (false negative; test with damage > armor);
  `ComboSystem.on_hit(attacker, defender)` requires both arguments.
- Bug journal B1–B11 to summarize as rules: conditional local import → UnboundLocalError;
  save `coins` vs read `gold` (gold lost on load); `ARMOR_REGEN_RATE` 4.0 → softlock, fix 1.0;
  `apply_phase_2_damage(entity, damage, ko_threshold=250)`; centralized `SLOT_TO_CATEGORIES`
  (ring→ring1/ring2, amulet→amulet1/amulet2); `current_attacker` guard in `on_hit` = dead code
  that capped the combo at 1.1, ceiling aligned 2.5→3.0; stale balance tests → update the tests,
  not the design (HP 500, armor 250, regen 1.0, delay 2.5); save reads
  `p.equipment_manager` + dual-write `equipment`/`equipped_gear`; rage never activated
  (`rage_threshold` 80) and knockback off the documented contract.
- Tests: monkeypatch `pygame.event.wait = lambda t=0: pygame.event.poll()` BEFORE `import pygame`,
  otherwise `Game.__init__` (game_base.py:221) freezes under dummy driver. Use a loader script,
  not `python -m unittest discover`. System python 3.14 without pygame → Hermes venv.
- Headless verification: `Game` → `set_state(PLAYING)` → `ensure_player()` → `draw()`; position via
  `g.cam.apply(p.rect)` (camera not updated outside the loop → offset 0, zoom 1); count pixels
  ≠ background `(20,20,20)` / platform `(100,200,100)`; save and upscale x4 with clamping of the
  subsurface; test the fallback by renaming the folder; check `p.rect` is still 40x60.
- World prototype integration: `GameState.WORLD`, `self.world_manager=None`, `_enter_world()`,
  `_update_world(dt)`, `draw_world_screen()`, debug key, ESC → TITLE. Autonomous mode:
  `self.autonomous` flag, `_autonomous_input()`, `_autonomous_advance()`,
  replacement of `self.ctrl.get()` in game_loop, CLI arg `--autonomous`,
  `SDL_VIDEODRIVER=dummy` for headless.

### 2. `sprite-management` (game-dev)
Description: `Load and render sprite sheets for PyBR0S characters`
Content: `core/sprite_manager.py`; sheets 96x128 = 3x4 frames of 32x32; boss 288x384 = 9x12;
crop first frame `(0,0,32,32)` via PIL → alpha surface; target size
`max(60, w*1.5) x max(80, h*1.5)`; centering, flip by facing, 40x60 hitbox unchanged;
issues: multi-sprite artifacts (failed crop), sprites too small (scale factor),
bad alignment (center computation).

### 3. `pygame-asset-generation` (software-development)
Description: `Generate pixel art sprites for Pygame games; source free/CC0 external assets.`
Sections: Procedure (`assets/sprites` structure, PIL generation, SpriteManager, Windows venv,
renderer integration), Pitfalls, Mountain_Roy RTS Specifics, PyBR0S Game Flow, References.
Hard facts: Windows venv via the hermes-runtime python (`cpython-3.11.16`) because the default
python creates a Linux venv; `from PIL import Image`; mandatory rectangle fallback;
capitalized `CLASS_SKINS` vs lowercase `rpg.class_name` → `.capitalize()`; `reset_game()` must
preserve the NEW class; Mountain_Roy pitfalls (dynamic lambda with self, `on_building_built()`
and not `on_build()`, missing `display.flip()`, float camera → `int()`, DPI, reuse of
`display.get_surface()`); menu flow Start→Class→Map→Play / Load→Map→Play.
Linked files: `references/sprite-palette.md`, `references/free-asset-sourcing.md`,
`references/pygame-sprite-animation.md`, `scripts/itch_download.py`,
`templates/sprite_generator.py`.

### 4. `pygame-debugging` (root)
Description: `Debug Pygame apps: fog of war, state flow, DPI issues.`
**Budget: `SKILL.md` ≤ 320 lines** (reference state after splitting: 162). Breakdown:
- `SKILL.md`: Quick Reference (symptom → probable cause) + 7 actionable rules
  (one rule = one cause + one fix) + 5 generic Pygame pitfalls. No narrative.
- `references/mountain-roy-pitfalls.md`: the bug oracle extracted from the old SKILL.md
  (symptom → cause → fix → lesson: harvesting, movement, melee, XP, HUD, signatures).
- `references/mountain-roy-workflow.md`: the RTS systems lifecycle.
- `references/pygame-dpi-and-window.md`: **optional** — only if the DPI/window detail
  exceeds the 5 bullets of SKILL.md (otherwise it stays inline, no file for 20 lines).
Role: cross-cutting Pygame oracle + Mountain_Roy workshop. Quick Reference (black screen, invisible
units, input, off-screen window, resources, workers, erratic movement, melee that never
hits), plus:
- One movement path per unit; a `return` before deposit = worker that carries forever.
- `_find_and_assign_to_resource()`: diversify by type not carried (1.5x radius), otherwise the
  nearest; `max_carry_types` per faction; deposit at the nearest allied building.
- Collision separation (25 + radii 12 = ~49 px) > melee range 32 → hit impossible: set
  range 64, test `distance <= unit.range + target.radius`. Diagnose with a full `game.update()`
  call, not a movement-only harness.
- XP via `killed_by` propagated in `take_damage(damage, attacker=None)`; level-up must re-stat.
- `hasattr(target,'hp')` before access (`BuildingProgress`/`ResourceNode` targets).
- `draw()` override: signature identical to the parent, otherwise TypeError on polymorphic dispatch.
- Partial refactor: `git diff --stat` + full suite BEFORE touching anything; `create_unit` sets
  `.game` after construction; restore `Unit.to_dict` rather than inlining it; single-frame tests
  invalidated by a new timer → loop over frames, do not revert the design.
Linked file: `references/mountain-roy-workflow.md`.

### 5. `mountain-roy` (software-development)
Description: `Use when working on Mountain_Roy (Python/Pygame RTS).`
Project: `C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy`, tests
`./.venv/Scripts/python.exe -m pytest tests/ -q`.
Hard facts (all to keep): `pygame.init()` + `set_mode((100,100))` before imports; do not
call `g.update(dt)` in tests; timed harvesting (`harvest_progress >= 1.0`, ~1 s);
`create_unit` sets `.game` after construction; `Unit.to_dict()` must stay on the base;
`_enemy_workers()` vs `_enemy_combat()`; victory = enemy town hall destroyed (not total wipe);
survive objective = `objective.current = int(mission_timer)` live; population
`10 + 5*farm_count`; `_can_produce_unit` checks `faction.can_produce` before population;
`Mission.enemy_config` + `time_limit` serialized; `[G]` cycles `TIME_SCALES=(1,2,4,8,16)`;
NEVER reassign `self.units`/`self.buildings` (`[...]` slice assign, otherwise systems desync);
`Hero.unit_type='hero'`; hero not free (hero_hall, 250g/100w, resurrection);
`take_damage()` applies armor ONCE (pass raw damage); purge dead units in
`units` AND `selected_units`; 3 heroes/faction (`entities/hero_types.py`); synergy
(`Unit.get_synergy_bonus`); ranged balance (archer 16 dmg/1.0, mage 40/1.6) already fixed;
orc modifier 1.15 dmg/1.10 hp.
Add a key table (W worker, J builder, B build, 1-6 units, T research, H hero).

### 6. `python-venv-setup` (root)
Description: `Create and manage Python virtual environments on Windows.`
venv procedure, PowerShell vs bash activation, pip, verification, deactivation; pitfalls:
terminal = bash (not PowerShell), `.bat` with `cd /d` + `-m package.main`, Windows vs Linux venv,
pygame impossible to compile → precompiled wheel / `pygame-ce` for Python 3.14,
`SDL_VIDEO_WINDOW_POS/CENTERED/HIGHDPI_DISABLED`, `display.get_surface() or set_mode()`,
`display.flip()` mandatory, `type()` lambda with self broken, `mixer.init()` in try/except.

### 7. `life-mean` (software-development, ~314 lines + 6 references)
Description: `Use when working on the Life_mean synthetic data lab.`
Project: `C:/Users/celes/Documents/Hermes-Workspace/Life_mean_realm` (ADSG P0–P12, 501 tests).
Sections: When to Use, Verification rules (always on), Architecture truth, Subject tree
(`compare/subjects.py`), Dashboard Docker data sync (host `data/` → named volume), Compare UI
click-flow, Compare V1 (`compare/`), Life_mean Studio PySide6, Life_mean Lab Phase D, Test suite,
Zero-secrets/packaging, Wheel integrity, emptied files, P0/P1 repairs (2026-10-09),
"protocol" terminology audit, Code Lab RAW provenance, RAW evidence (pass-rates),
lab-wide timeline, AutoPilot/DebateEngine lifecycle (8d2392a), Debate Lab, Code Lab,
Context-State audit methodology (read-only), canonical state vs compressor mapping
(two parallel mechanisms NOT wired), GCM push headless Windows pitfall (wincred bypass),
defaultdict that mutates state (order-dependent verdict), code-lab E2E must force
`multi_agent=False`, Cluster Graph CG1 (`compare/graph.py`), hermes-orchestrator security review,
pitfalls, credentials/providers/tabs, process, `experimental/`.
References: `dashboard-api-extension.md`, `docker-and-provider-verification.md`,
`experiment-resume-and-checkpoints.md`, `history-rewrite-secret-purge.md`,
`recovering-emptied-source.md`, `verification-and-audit-discipline.md`.

### 8. `life-mean-recent-lessons` (software-development, ~244 lines + 6 references + 1 script)
Description: `Dated Oct 2026 journal of Life_mean lessons — temporary, archivable.`
Nature: **lessons log**, the only accepted exception to the "no dates" rule. The frontmatter must
announce it ("dated journal … temporary, archivable") so an agent knows the content is
perishable: when a lesson becomes a durable rule, promote it into `life-mean` and remove it
from here.
Lessons one per section, dated, without narrative: Agent Builder (2026-10-31), Historical Thinkers
& Patterns, Sentinel model config, provider provenance fix, GitHub access (Tailscale
blocks private), CaptN Runtime v1, Pipeline Inspector & Feature Pool, Docker permissions
(Errno 13), Studio that "does nothing" at launch, coverage ≠ inventory, bridge already
existing, "permission error" = classify the literal first, orchestrator vs permissions (two
systems not connected to the clients), P5 self-extension registries ("total: 0"), P6 persisted
observability, "blocked by a dependency" (verify the code exists), math tools (parse, do not sweep
the numbers), host tabs/telemetry, wiring ≠ supporting, runtime usage log, git on this
repo, "2 features out of 989" (recent window ≠ sample), 403 before reading the body =
aborted connection on Windows, `inspect.getsource` lies after a rewrite, verification gate
before the next patch, artifact durability/reproducibility/honesty, `pyproject.toml`
insufficient, test baseline + commands.
References: `dashboard-tabs.md`, `docker-run-volumes.md`, `durability-reproducibility.md`,
`feature-pool-discovery.md`, `incremental-ingestion-offsets.md`, `orchestrator-permissions.md` ;
script `scripts/audit-js-blocks.py`.

### 9. `life-mean-dashboard-qa` (root)
Description: `Use when QA-testing the Life_mean dashboard.`
Target `http://127.0.0.1:8080/dashboard`; canonical launcher `run_server.bat` (kills zombie
listeners, forwards `--host/--port`, `run_server.bat 9099`); equivalent
`python -m experiments.dashboard --port 8080`; SQL hardening (parameterized queries,
input validation); MIA v0 → Life_mean evolution; metrics gotcha; QA procedure; files.

### 10. `snapshot-logic-architecture` (software-development)
Description: `Use for LearningBus, Snapshot, and Security Gate logic.`
Three independent states (Security Gate = static RBAC, LearningBus = raw evidence,
Snapshot = bridge); `BatchProcessor` = compiler (acquired analysis → diff → Version_Manager
v1.1.a→v1.1.b → `active_snap.json` → rollback to `snapshots/`); unified schema
(version, timestamp, context.identity/competencies/constraints, active_roadmap_step,
build_notes); authorization = `Role_Has_Right AND Has_Validated_Competency`; reconstruction
of a past state by re-applying Gate + Bus.

### 11. `captn-brain` (software-development)
Description: `CaptN-BRAIN CLI, real-time token/context optimization.`
Project `C:\Users\celes\Documents\Hermes-Workspace\Mia_Brain\CaptN-BRAIN-main`.
Sections: CLI Protocol (the CLI is THE single source of truth), core principle
(deterministic first, LLM when needed), wrapper + single venv entry point, global context
optimization flags TO BE PLACED BEFORE the command, real-time commands under `devtools`,
token savers, key files, pitfalls.

### 12. `team-coding-workflow` (software-development)
Description: `Use when building a multi-role AI coding team pipeline.`
Sections: Architecture (junior/mid/senior/validator roles), Role Philosophies, Intelligent Turn
Resume, Validator Gates, Usage, Integration with Code Lab Engine, Pitfalls, Files.

### 13. `autonomous-decision-engine` (software-development)
Description: `Build telemetry-driven decision systems with pattern analysis.`
Sections: Overview, Architecture, 6-step Procedure (decision space, telemetry collection,
pattern analysis, decision rules, safety guardrails, logging), Decision Rules
Reference, CLI Integration (`captn/cli/_devtools.py`), Verification, Pitfalls, Files Structure.
Principle: models propose, the permission system authorizes.

### 14. `dogfood-python` (software-development)
Description: `Exploratory QA of Python apps through real execution.`
Workflow discover entrypoints → realistic scenarios → vary inputs/config → observe →
inspect persisted state → reproduce → minimize → report the evidence. For each issue:
scenario, expected, actual, exact command, traceback, reproducibility, severity, suspected
component. Rules: real execution > reading code; no claim without reproduction;
do not fix during discovery; distinguish FAIL/ERROR/INCONCLUSIVE/PASS.

### 15. `python-fastapi-apps` (software-development)
Description: `Use when building or extending a Python FastAPI web app.`
7-point procedure: baseline (existing suite green + count), do not rewrite the core,
SPA served by the same app (`Mount("/assets")`, `html[data-theme]`), `python-multipart` for
`UploadFile`, long jobs in daemon threads with an on-disk work-file + lazy reindexing
(survives restart), tests at 3 levels (unit / `httpx.AsyncClient(ASGITransport)` / E2E uvicorn+browser),
verify every criterion by real execution including failure paths.
Pitfalls: `JSONResponse` overrides the decorator's `status_code`; `__init__.py` shadowing a
submodule (`from . import export as export_mod`); non-reentrant `Lock` → `RLock`;
silent no-op mutator; encoding (utf-8 → cp1252 → latin-1 before detection);
multiple TestClients deadlock on Windows; singletons leaking between test files;
`write_file` refused after a partial read → `.new` + `mv -f`; CDP upload
`DOM.setFileInputFiles` + `change` event, poll and never use a fixed sleep; `pip-audit` exits 3
WHEN it finds vulnerabilities; normalize the severity vocabulary; `Mount` without
`.endpoint` or `.methods`.
References: `test-harness.md`, `audit-and-validation.md`.

### 16. `python-terminal-games` (software-development)
Description: `Use when building ASCII/terminal games in Python.`
Sections: When to Use, Procedure, Windows console specifics, Pitfalls, Conventions for this user.
References: `headless-testing.md`, `windows-console.md`; template `launcher.bat`.

### 17. `hermes-cron-jobs` (autonomous-ai-agents)
Description: `Schedule/edit Hermes cron jobs with Discord delivery.`
Hermes cron job creation/editing commands, Discord delivery, scheduling pitfalls;
template `templates/ai-morning-briefing-prompt.md` (autonomous morning briefing).

---

## FINAL VERIFICATION

Run and fix until green:

```bash
cd C:/Users/celes/AppData/Local/hermes/profiles/def/skills
# 1) the 17 folders exist
for s in pybr0s mountain-roy sprite-management pygame-asset-generation pygame-debugging \
  python-venv-setup snapshot-logic-architecture life-mean-dashboard-qa; do test -f "$s/SKILL.md" || echo "MISSING $s"; done
# 2) valid frontmatter + description present
for f in */SKILL.md software-development/*/SKILL.md autonomous-ai-agents/hermes-cron-jobs/SKILL.md; do
  head -1 "$f" | grep -q '^---$' || echo "BAD FRONTMATTER $f"
  grep -q '^description:' "$f" || echo "NO DESCRIPTION $f"
done
# 3) no empty or stub skill
find . -name SKILL.md -not -path './.archive/*' -size -1k
```

Then `skills_list()` must show **the 17 expected names** — verdict per name, never by total
(the number of bundled skills varies with the installed Hermes version), each with description and
category. Substance check: open
`pybr0s`, `mountain-roy`, `life-mean`, `pygame-debugging` and verify the numeric
facts are actually there (864 lines, 367 tests, 10+5*farms, harvest 1.0, armor 4.0→1.0, 40x60).

## EXPECTED OUTPUT

A short report: skills created (name, category, line count), support files
recreated, result of the 3 verifications, and any discrepancy accepted versus this specification.
