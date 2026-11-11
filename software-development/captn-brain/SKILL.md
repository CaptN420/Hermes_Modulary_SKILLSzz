---
name: captn-brain
category: software-development
description: Use for CaptN-BRAIN CLI token/context optimisation. Deterministic first.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cli, llm, context, tokens, deterministic]
    related_skills: [autonomous-decision-engine, team-coding-workflow]
---

# CaptN-BRAIN — deterministic first, LLM when necessary

Project: `C:\Users\celes\Documents\Hermes-Workspace\Mia_Brain\CaptN-BRAIN-main`. French-speaking user; concise answers in French. Value: verified code that works.

## CLI Protocol (non-negotiable)
The CaptN Brain CLI skill is the ONLY source of truth for any operation. Rules:
1. NEVER invent a command/flag/argument/alias/syntax. Use exactly the command defined by the skill.
2. Do not replace a CLI operation with an improvised shell command.
3. Prefer deterministic, machine-readable output when it exists.
4. Reuse the IDs/paths/values returned by previous commands (no re-discovery).
5. Run ONLY the minimum set of commands required.
6. Do not repeat a command unless verification/recovery requires it.
7. Keep output processing minimal: extract only what the next action needs.
8. If the required operation is not defined by the skill → STOP, report that the CLI capability is undefined (never guess).
9. Minimal explanations. Exact execution takes priority.

Execution model: Intent → CLI skill lookup → exact command → execute → parse the result → next action.
The skill defines HOW to interact with CaptN Brain; the agent decides WHICH operation is required; CaptN Brain remains the source of truth for state.

Determinism: same intent + same system state → same CLI operation, same command structure, same argument-selection rules. No pointless discovery, no speculative action. Do not improvise when an exact CLI operation exists.

## Core Principle
Routes tasks to ~800 deterministic tools (avoids LLM tokens). Context optimisation ALWAYS enabled by default.

## Wrapper + venv (single entry point)
Every command goes through the wrapper:
```bash
cd C:/Users/celes/Documents/Hermes-Workspace/Mia_Brain/CaptN-BRAIN-main
./venv/bin/python summon_agents.py <commande> [options]
```
(venv present; otherwise `python summon_agents.py`.) Commands auto-discovered from `captn/cli/` + `tools/*.py` via `register_cli()`. Never guess a name — list with `summon_agents.py --help`.

## Global context optimisation (flags — place BEFORE the command)
```bash
./venv/bin/python summon_agents.py [flags] <commande> [options]
```
| Flag | Default | Effect (token optimisation) |
|------|--------|------------------------------|
| `--cache-size N` | 1024 | Tool LRU cache size (0=disabled) |
| `--no-adaptive-routing` | ON | fixed top_k=2 (disables adaptive routing) |
| `--llm-fallback` | OFF | LLM fallback on deterministic failure (opt-in) |
| `--token-profiling off\|summary\|verbose` | off | Token profiling |
| `--shadow-ab off\|shadow` | off | A/B shadow of adaptive weights |
| `--domain-filter` | off | Phase 2: keep only tools from the domain |
| `--history-prune` | off | Phase 2: truncate old tool results |
| `--max-tool-results N` | 5 | Max results kept (history-prune) |
| `--max-tool-chars N` | 2000 | Max chars per result (history-prune) |
| `--max-tool-compress-chars N` | 5000 | Aggressive compression threshold |
| `--tool-compress-keep N` | 500 | Chars kept under aggressive compression |

## Real-time / token optimisation commands (under `devtools`)
- `devtools token_orchestrator analyze|apply [--force]|log [--export out.jsonl]` — autonomous saver, dry-run apply by default
- `devtools token_profile status|test` — Hermes profiler
- `devtools hermes_profile status|demo|records|csv|clear` — real Hermes→OpenRouter profiler via the `pre_api_request` hook
- `devtools gap analyze|records` — 64k (heuristic) vs 150k (actual) gap
- `devtools reconcile demo|records` — reconciles the local tokenizer against OpenRouter usage
- `devtools budget demo|status|telemetry records|record|clear|export` — Context Budget (relevance-based selection)
- `devtools adaptive demo|status` — dynamic budget allocation

## DevTools token savers
- `codechunk f.py -f foo` / `-l 42` / `-c 5` — split by function/class (--json)
- `imports f.py -u` / `--fix` — unused imports, categorises stdlib/third-party
- `context f.py -l 42` / `-f foo` / `-s 5` — full context
- `lint f.py` / `--errors-only` / `--json` — detects context leaks/errors
- `diff-ast old.py new.py` / `-c code -C code2` — structural AST diff

## Key files
- `summon_agents.py` — CLI + global flags + `apply_optimization_flags()`
- `captn/cli/__init__.py` — auto-discovery (`auto_discover`)
- `captn/cli/_devtools.py` — devtools subcommand registry
- `captn/runtime/token_economy_orchestrator.py` — autonomous economy engine
- `captn/runtime/{token_profiler,hermes_profiler,token_gap,reconcile,context_budget,adaptive_manager}.py`
- `captn/daemon.py` — persistent daemon
- `docs/cli/commandes.md`, `docs/TOKEN_*.md` — reference

## Pitfalls
- **`--help` is the source of truth**: commands are auto-discovered; a listed command may be missing if its module fails to import (silent failure, logged at `logger.debug`).
- **venv unix=bin**: the venv uses `bin/python` (POSIX layout) even on Windows git-bash.
- **`apply` without `--force`** stays in dry-run; 2 vars remain blocked by ProductionGuard (human approval required).
- **`devtools token_orchestrator log --export`** writes JSONL; history in `logs/token_economy_decisions.jsonl`.
- Do not modify protected files (ProductionGuard) without approval.
