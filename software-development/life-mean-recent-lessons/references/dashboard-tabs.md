# Ajouter un onglet au dashboard Life_mean (`experiments/ui/dashboard.html`)

Le dashboard est un fichier HTML unique (~5 900 lignes, 4 blocs `<script>`) qui contient son propre JS.
Aucun framework, aucun build : chaque onglet se déclare à **quatre endroits**, et un oubli donne un
onglet qui ne s'ouvre pas ou une table vide.

## 1. Les quatre points de contact

1. **Bouton de navigation** dans la barre :
   `<button class="tab-btn" data-tab="<nom>" onclick="switchTab('<nom>', this)">Libellé</button>`
2. **Panneau** : `<div id="panel-<nom>" class="tab-panel">…</div>` — l'`id` doit valoir
   `panel-` + le `data-tab`, sinon `switchTab` ne trouve rien et l'onglet reste sur le précédent.
3. **Hook dans `switchTab(name, btn)`** : `if (name === '<nom>') loadX();` — sans lui le panneau
   s'affiche mais ne charge jamais ses données (tableau vide silencieux).
4. **Fonction JS** `loadX()` + un `render()` séparé quand il y a un filtre, pour ne pas refaire de
   fetch à chaque changement de filtre.

## 2. Conventions à réutiliser

- `API_BASE = '/api'` ; `piGet(path)` / `piEsc(value)` existent déjà (échappement HTML obligatoire).
- Classes existantes : `card`, `subtitle`, `pi-table`, `pi-badge`, `empty-state`, `tab-btn`.
  Un `<td colspan="N" class="empty-state">` doit toujours porter **un message**, jamais du vide.
- Pattern « provenance » : afficher d'où vient la donnée plutôt que le seul chiffre —
  « run rehydraté depuis le résumé persisté — 4/4 traces conservées »,
  « 14 observées / 989 chargées — 4500 événements sur 25 populations (tronqué) ».
  Un compteur sans couverture se lit comme un total ; une table vide sans raison se lit comme une panne.
- Une source indisponible affiche **sa raison** (texte d'erreur du payload), pas une valeur plausible.

## 3. Pièges qui coûtent le plus de temps

- **Un `const`/`let` redéclaré dans le même bloc `<script>` neutralise tout le bloc** : les onglets
  cessent de répondre sans erreur visible dans l'UI. Vérifier chaque bloc isolément :
  `python "<skill_dir>/scripts/audit-js-blocks.py" experiments/ui/dashboard.html`
  (sortie attendue : `[OK] bloc N` pour chacun). Un OK prouve qu'un doublon n'est pas passé.
- **Ne pas blâmer l'UI avant d'avoir interrogé l'API dans la page.**
  `js("fetch('/api/pipeline/features').then(r=>r.json()).then(d=>{window.__probe=JSON.stringify(...)})")`
  puis relire `window.__probe` : ça sépare « la route ne rend rien » de « le rendu ne s'applique pas ».
  Un chargement lourd (4–5 s sur 1 M d'événements) ressemble à un bug si on ne laisse pas le temps.
- **L'image Docker `COPY` le code** : tant que l'image n'est pas reconstruite, le navigateur sert
  l'ancien HTML. `docker compose build dashboard && docker compose up -d`, puis vérifier que le
  contenu attendu est bien servi.
- **Les tests Python ne valident pas le rendu.** `test_dashboard_ui.py` vérifie des chaînes/alias, pas
  qu'un onglet fonctionne : la preuve est un vrai navigateur (voir §4).

## 4. Recette de vérification (celle qui compte)

1. `audit-js-blocks.py` sur le HTML → tous les blocs `[OK]`.
2. Reconstruire l'image si le code change, sinon lancer le dashboard hôte :
   `.venv/Scripts/python -m experiments.dashboard --port 8082 --host 127.0.0.1`
   (le port 8080 est pris par le conteneur ; l'hôte voit en plus les collecteurs Windows réels).
3. Piloter le navigateur : `new_tab(url)`, puis
   `js("switchTab('<nom>', [...document.querySelectorAll('.tab-btn')].find(b=>b.dataset.tab==='<nom>'))")`,
   attendre (3–10 s selon l'API), et lire `innerText` de chaque zone :
   compteur, ligne de provenance, 2–3 lignes du tableau.
4. Tester le filtre dans les deux sens (total → filtré) et vérifier le compte affiché, pas seulement
   la présence de lignes.
5. `capture_screenshot()` pour l'œil humain — utile mais **pas** une preuve à la place des `innerText`.

## 5. Exemples réels (structure à copier)

- Onglet **Système** (`panel-system`, `sysLoad`) : cartes Defender + table des événements, ligne
  `degraded` quand une source ne répond pas (`not a Windows host` dans le conteneur Linux).
- Onglet **Traces** (`panel-traces`, `trLoad`/`trFetch`/`trSetRule`/`trRender`) : `<select>` des runs
  depuis `GET /api/experiments`, filtre par règle, table `heure · règle · tâche · entrée · sortie`,
  et note de provenance (`d.rehydrated`, `restored_totals.traces`, `traces_absent_reason`).
