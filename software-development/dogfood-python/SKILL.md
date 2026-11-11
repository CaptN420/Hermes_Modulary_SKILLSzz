---
name: dogfood-python
version: 1.0.0
author: Hermes Agent
license: MIT
description: QA exploratory d'applications Python par exécution réelle.
category: software-development
metadata:
  hermes:
    tags: [qa, testing, debugging, python]
    related_skills: [dogfood, systematic-debugging]
---

# dogfood-python

## When to Use

Use this skill when you need to run exploratory QA on a Python application — exercise real entrypoints, find runtime bugs, reproduce failures, and inspect persisted state — rather than reason about the code from reading alone.

Goals:
- exercise real entrypoints and workflows
- find runtime bugs, edge cases, and broken state transitions
- reproduce failures with evidence
- inspect files, DB state, logs, events, and outputs
- avoid reporting speculative bugs

Workflow:
- discover entrypoints → run realistic scenarios → vary inputs/config/state → observe actual behavior → inspect persisted state → reproduce failures → minimize failing case → report evidence

Use when available: pytest, Hypothesis, coverage, pdb/debugpy, type checker/linter, CLI/API/library calls.

For each issue record:
- scenario
- expected behavior
- actual behavior
- exact command/input
- traceback/evidence
- reproducibility
- severity
- suspected component

Rules:
- real execution over code-reading assumptions
- no bug claim without reproduction evidence
- do not modify/fix during discovery unless requested
- distinguish FAIL, ERROR, INCONCLUSIVE, and PASS
- preserve artifacts needed to reproduce the issue
