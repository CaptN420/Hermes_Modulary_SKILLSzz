---
name: captn-brain
category: software-development
description: CaptN-BRAIN CLI, optimisation tokens/contexte temps réel.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cli, llm, context, tokens, deterministic]
    related_skills: [autonomous-decision-engine, team-coding-workflow]
---

# CaptN-BRAIN — déterministe d'abord, LLM si nécessaire

Projet: `C:\Users\celes\Documents\Hermes-Workspace\Mia_Brain\CaptN-BRAIN-main`. Utilisatrice francophone; réponses concises en français. Valeur: code vérifié qui fonctionne.

## CLI Protocol (non-négociable)
Le skill CaptN Brain CLI est LA SEULE source de vérité pour toute opération. Règles :
1. Ne JAMAIS inventer commande/flag/argument/alias/syntaxe. Utiliser exactement la commande définie par le skill.
2. Ne pas remplacer une opération CLI par une commande shell improvisée.
3. Préférer la sortie déterministe et machine-readable quand elle existe.
4. Réutiliser les IDs/chemins/valeurs retournés par les commandes précédentes (pas de redécouverte).
5. Exécuter SEULEMENT le minimum de commandes requis.
6. Ne pas répéter une commande sauf si vérification/récupération l'exige.
7. Garder le traitement de sortie minimal : extraire seulement ce qui est nécessaire à l'action suivante.
8. Si l'opération requise n'est pas définie par le skill → STOP, signaler que la capacité CLI est indéfinie (jamais deviner).
9. Explications minimales. Exécution exacte prioritaire.

Execution model : Intent → CLI skill lookup → commande exacte → exécuter → parser le résultat → action suivante.
Le skill définit COMMENT interagir avec CaptN Brain ; l'agent décide QUELLE opération est requise ; CaptN Brain reste source de vérité de l'état.

Déterminisme : même intention + même état système → même opération CLI, même structure de commande, mêmes règles de sélection d'arguments. Pas de découverte inutile, pas d'action spéculative. Ne pas improviser quand une opération CLI exacte existe.

## Principe central
Route les tâches vers ~800 outils déterministes (évite les tokens LLM). Optimisation du contexte TOUJOURS activée par défaut.

## Wrapper + venv (unique point d'entrée)
Toute commande passe par le wrapper:
```bash
cd C:/Users/celes/Documents/Hermes-Workspace/Mia_Brain/CaptN-BRAIN-main
./venv/bin/python summon_agents.py <commande> [options]
```
(venv présent; sinon `python summon_agents.py`.) Commandes auto-découvertes depuis `captn/cli/` + `tools/*.py` via `register_cli()`. Ne jamais deviner un nom — lister avec `summon_agents.py --help`.

## Optimisation globale du contexte (flags — mettre AVANT la commande)
```bash
./venv/bin/python summon_agents.py [flags] <commande> [options]
```
| Flag | Défaut | Effet (optimisation tokens) |
|------|--------|------------------------------|
| `--cache-size N` | 1024 | Taille cache LRU outils (0=désactivé) |
| `--no-adaptive-routing` | ON | top_k=2 fixe (désactive routing adaptatif) |
| `--llm-fallback` | OFF | Fallback LLM si échec déterministe (opt-in) |
| `--token-profiling off\|summary\|verbose` | off | Profiling tokens |
| `--shadow-ab off\|shadow` | off | A/B shadow des poids adaptatifs |
| `--domain-filter` | off | Phase 2: garde seulement les outils du domaine |
| `--history-prune` | off | Phase 2: tronque les anciens résultats d'outils |
| `--max-tool-results N` | 5 | Max résultats gardés (history-prune) |
| `--max-tool-chars N` | 2000 | Max chars par résultat (history-prune) |
| `--max-tool-compress-chars N` | 5000 | Seuil compression agressive |
| `--tool-compress-keep N` | 500 | Chars gardés quand compression agressive |

## Commandes temps réel / optimisation tokens (sous `devtools`)
- `devtools token_orchestrator analyze|apply [--force]|log [--export out.jsonl]` — économiseur autonome, application dry-run par défaut
- `devtools token_profile status|test` — profiler Hermes
- `devtools hermes_profile status|demo|records|csv|clear` — profiler Hermes→OpenRouter réel via hook `pre_api_request`
- `devtools gap analyze|records` — écart 64k (heuristique) vs 150k (réel)
- `devtools reconcile demo|records` — réconcilie tokenizer local vs usage OpenRouter
- `devtools budget demo|status|telemetry records|record|clear|export` — Context Budget (sélection par pertinence)
- `devtools adaptive demo|status` — allocation dynamique des budgets

## DevTools économiseurs de tokens
- `codechunk f.py -f foo` / `-l 42` / `-c 5` — découpe par fonction/classe (--json)
- `imports f.py -u` / `--fix` — imports inutilisés, catégorise stdlib/third-party
- `context f.py -l 42` / `-f foo` / `-s 5` — contexte complet
- `lint f.py` / `--errors-only` / `--json` — détecte les fuites de contexte/erreurs
- `diff-ast old.py new.py` / `-c code -C code2` — diff structurel AST

## Fichiers clés
- `summon_agents.py` — CLI + flags globaux + `apply_optimization_flags()`
- `captn/cli/__init__.py` — auto-découverte (`auto_discover`)
- `captn/cli/_devtools.py` — registre sous-commandes devtools
- `captn/runtime/token_economy_orchestrator.py` — moteur économie autonome
- `captn/runtime/{token_profiler,hermes_profiler,token_gap,reconcile,context_budget,adaptive_manager}.py`
- `captn/daemon.py` — daemon persistant
- `docs/cli/commandes.md`, `docs/TOKEN_*.md` — référence

## Pitfalls
- **`--help` source de vérité**: commandes auto-découvertes; une commande listée peut manquer si son module échoue à l'import (échec silencieux, loggé en `logger.debug`).
- **venv unix=bin**: le venv utilise `bin/python` (structure POSIX) même sous Windows git-bash.
- **`apply` sans `--force`** reste en dry-run; 2 vars restent bloquées par ProductionGuard (approbation humaine requise).
- **`devtools token_orchestrator log --export`** écrit en JSONL; historique dans `logs/token_economy_decisions.jsonl`.
- Ne pas modifier des fichiers protégés (ProductionGuard) sans approbation.
