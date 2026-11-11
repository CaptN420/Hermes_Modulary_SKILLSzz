# Feature Pool — mesure de couverture et élargissement de la découverte

Recette à appliquer avant **et** après toute modification de `feature_pool/scanner.py`.
Le principe : un `0 hit` du pool ne prouve rien sur l'existence d'une capacité ; seule une
mesure de couverture face à un inventaire `ast` permet de conclure.

## 1. Mesurer avant de toucher au code

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

Puis côté pool : `len(pool.registry.all_features)` **et** `len(scanner._build_scan_paths())`.

**Le piège à vérifier en premier : le nombre de fichiers retenus.** Si `_build_scan_paths()`
renvoie beaucoup plus de fichiers que l'inventaire `ast`, un dossier généré se fait scanner.
Mesuré sur ce dépôt : `code_lab_runs/` contenait **1104 `.py`** copiés par run — sans lui dans la
denylist, le scan passe de 839 à 1943 fichiers et indexe des doublons d'exécution.

## 2. Forme correcte de la découverte

- Découvrir **par système de fichiers**, jamais par liste codée en dur : tout dossier de premier
  niveau sauf denylist explicite. Les paquets ajoutés après coup (`pipeline_inspector`,
  `feature_pool`, `data`, `life_mean_extensions`, `hermes_cronjob_manager`) étaient invisibles
  avec la liste figée.
- Denylist minimale : `.venv`, `venv`, `node_modules`, `build`, `dist`, `.git`, `__pycache__`,
  `site-packages`, `crawled`, `reports`, `overrides`, `.pytest_cache`, `tests`, `docs`, `docker`,
  `External`, `benchmarks`, `scripts`, **et tout `*_runs`** (`code_lab_runs`, `debate_lab_runs`).
- `tests/` est exclu **volontairement** : ce sont des fixtures, pas des capacités. Un fixture
  nommé `FakeController` avait été indexé comme feature.
- Classement : mot-clé du nom (comportement historique) → suffixe (`engine`, `controller`,
  `manager`, `worker`, `agent`) → **chemin** (`core/safety`→SAFETY, `core/router`→ROUTING,
  `life_mean_studio`→STUDIO, `pipeline_inspector`→OBSERVABILITY, `feature_pool`→METACOGNITION,
  `data`→PERSISTENCE, `legacy`→LEGACY…) → `TOOLS` en dernier recours.
  Sans l'étage « chemin », `PolicyGuard`, `ResourceGuard` et `ExperimentExecutionGate`
  n'entrent jamais dans le registre.

## 3. Décomposition des nombres (à reproduire, pas à supposer)

`features enregistrées = classes scannées − classes privées/test − fusions par nom homonyme`

Chiffres de contrôle sur ce dépôt (après correctif) :

| Mesure | Valeur |
|---|---|
| fichiers retenus par `_build_scan_paths()` | 839 |
| classes présentes | 1280 |
| classes privées / préfixées `test` | 70 |
| noms de classes distincts | 1055 |
| features enregistrées | **989** (221 fusions) |
| couverture des noms non privés | **100 %** |
| BROKEN | 0 (1 seul fichier du dépôt ne parse pas, et il est hors périmètre) |
| `analyze_all` | 1,75 s |
| construction du Studio (table 989 lignes) | 0,13 s |

Ne pas exprimer le critère d'acceptation en nombre brut de features : `_register_feature`
fusionne les homonymes, donc tout seuil calibré sur « nb de classes » est faux d'avance.

## 4. Protocole de vérification après modification

```bash
QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -m pytest feature_pool/tests -q      # 13 passed
QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -m pytest pipeline_inspector/tests -q # 27 passed
QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -m pytest tests -q                    # baseline inchangé
```

Plus un smoke offscreen du Studio (construction < 5 s, `fp_table.rowCount()` = nb de features)
et un **delta avant/après** des statuts : aucune `VALIDATED` ne doit être rétrogradée sans être
nommée, aucune feature ne doit disparaître sans être expliquée.

Effet de bord à annoncer systématiquement : élargir la découverte multiplie les faux `VALIDATED`
(27 → 129 sur preuve étrangère) et les conflits cartésiens (8 190 → 242 638, toujours 0 high/medium).

## 5. Tests à maintenir dans `feature_pool/tests/test_feature_pool.py`

1. `sees_top_level_packages` — `PipelineInspector` et `FeatureAnalyzer` présents, chemins
   `pipeline_inspector/` et `feature_pool/` indexés.
2. `indexes_security_classes` — `PolicyGuard`, `ResourceGuard`, `ExperimentExecutionGate`,
   `PolicyViolation` dans le registre.
3. `excludes_tests_and_generated_runs` — aucun chemin `tests/`, `code_lab_runs/`,
   `debate_lab_runs/` ; `FakeController` absent.
4. `broken_count_is_bounded` — `BROKEN <= 3` et `len(statuses) > 500`.

Ces quatre tests sont la non-régression du correctif : sans eux, un retour à une liste codée en
dur ou l'oubli d'une denylist ne se voit pas.
