# Feature Pool — coverage measurement and widening discovery

Recipe to apply before **and** after any change to `feature_pool/scanner.py`.
The principle: a `0 hit` from the pool proves nothing about the existence of a capability; only a
coverage measurement against an `ast` inventory can settle it.

## 1. Measure before touching the code

```bash
cd /c/Users/celes/Documents/Hermes-Workspace/Life_mean_realm
./.venv/Scripts/python.exe - <<'PY'
import ast, collections, re, sys
from pathlib import Path
ROOT = Path('.')
SKIP = {'.venv','__pycache__','node_modules','.git','site-packages','crawled',
        'build','dist','code_lab_runs','debate_lab_runs','reports','tests'}
files = classes = 0
bad, pkgs = [], collections.Counter()
for pkg in sorted(ROOT.iterdir()):
    if not pkg.is_dir() or pkg.name.startswith('.') or pkg.name in SKIP:
        continue
    for f in pkg.rglob('*.py'):
        if set(f.parts) & SKIP:
            continue
        src = f.read_text(encoding='utf-8', errors='replace')
        n = len(re.findall(r'^class\s+(\w+)', src, re.M))
        files += 1; classes += n; pkgs[pkg.name] += n
        try:
            ast.parse(src, filename=str(f))
        except SyntaxError as e:
            bad.append((str(f), e.lineno, e.msg))
print(files, 'fichiers |', classes, 'classes |', len(bad), 'non parsables')
print(dict(pkgs.most_common(10)))
for b in bad[:10]: print('  ', b)
PY
```

Then on the pool side: `len(pool.registry.all_features)` **and** `len(scanner._build_scan_paths())`.

**The trap to check first: the number of retained files.** If `_build_scan_paths()`
returns far more files than the `ast` inventory, a generated folder is being scanned.
Measured on this repo: `code_lab_runs/` held **1104 `.py`** copied per run — without it in the
denylist, the scan goes from 839 to 1943 files and indexes execution duplicates.

## 2. Correct shape of the discovery

- Discover **through the filesystem**, never through a hard-coded list: every first-level
  folder except an explicit denylist. Packages added later (`pipeline_inspector`,
  `feature_pool`, `data`, `life_mean_extensions`, `hermes_cronjob_manager`) were invisible
  with the frozen list.
- Minimal denylist: `.venv`, `venv`, `node_modules`, `build`, `dist`, `.git`, `__pycache__`,
  `site-packages`, `crawled`, `reports`, `overrides`, `.pytest_cache`, `tests`, `docs`, `docker`,
  `External`, `benchmarks`, `scripts`, **and every `*_runs`** (`code_lab_runs`, `debate_lab_runs`).
- `tests/` is excluded **deliberately**: those are fixtures, not capabilities. A fixture
  named `FakeController` had been indexed as a feature.
- Classification: name keyword (historical behaviour) → suffix (`engine`, `controller`,
  `manager`, `worker`, `agent`) → **path** (`core/safety`→SAFETY, `core/router`→ROUTING,
  `life_mean_studio`→STUDIO, `pipeline_inspector`→OBSERVABILITY, `feature_pool`→METACOGNITION,
  `data`→PERSISTENCE, `legacy`→LEGACY…) → `TOOLS` as a last resort.
  Without the "path" stage, `PolicyGuard`, `ResourceGuard` and `ExperimentExecutionGate`
  never enter the registry.

## 3. Breaking down the numbers (to reproduce, not to assume)

`registered features = scanned classes − private/test classes − merges by homonymous name`

Control figures on this repo (after the fix):

| Measurement | Value |
|---|---|
| files retained by `_build_scan_paths()` | 839 |
| classes present | 1280 |
| private / `test`-prefixed classes | 70 |
| distinct class names | 1055 |
| registered features | **989** (221 merges) |
| coverage of non-private names | **100 %** |
| BROKEN | 0 (a single file of the repo does not parse, and it is out of scope) |
| `analyze_all` | 1.75 s |
| Studio build (989-row table) | 0.13 s |

Do not express the acceptance criterion as a raw feature count: `_register_feature`
merges homonyms, so any threshold calibrated on "number of classes" is wrong from the start.

## 4. Verification protocol after a change

```bash
QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -m pytest feature_pool/tests -q      # 13 passed
QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -m pytest pipeline_inspector/tests -q # 27 passed
QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -m pytest tests -q                    # baseline unchanged
```

Plus an offscreen smoke of the Studio (build < 5 s, `fp_table.rowCount()` = number of features)
and a **before/after delta** of the statuses: no `VALIDATED` may be downgraded without being
named, no feature may disappear without being explained.

Side effect to announce systematically: widening discovery multiplies false `VALIDATED`
(27 → 129 on foreign evidence) and Cartesian conflicts (8,190 → 242,638, still 0 high/medium).

## 5. Tests to maintain in `feature_pool/tests/test_feature_pool.py`

1. `sees_top_level_packages` — `PipelineInspector` and `FeatureAnalyzer` present, paths
   `pipeline_inspector/` and `feature_pool/` indexed.
2. `indexes_security_classes` — `PolicyGuard`, `ResourceGuard`, `ExperimentExecutionGate`,
   `PolicyViolation` in the registry.
3. `excludes_tests_and_generated_runs` — no `tests/`, `code_lab_runs/`,
   `debate_lab_runs/` path; `FakeController` absent.
4. `broken_count_is_bounded` — `BROKEN <= 3` and `len(statuses) > 500`.

These four tests are the fix's non-regression: without them, a return to a hard-coded
list or a forgotten denylist goes unnoticed.
