---
name: team-coding-workflow
description: Use when building a multi-role AI coding team pipeline.
category: software-development
version: 1.0.0
author: Hermes Agent
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, coding, team, workflow, junior, mid, senior, validator]
    related_skills: [codebase-inspection, autonomous-decision-engine]
---

# Team Coding Workflow

Three-tier AI developer team with deterministic validator gates between each phase.
Each role has a distinct philosophy — the pipeline simulates a real dev team.

## When to Use

- User wants code produced by a structured multi-role team
- User needs baseline → refinement → optimization progression
- User wants validator gates after each role's contribution
- User wants intelligent turn reprise (each agent reads previous work)

## Architecture

```
User Prompt
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ PHASE 0: ARCHITECT (Senior-level planning)          │
│   - Designs module structure                         │
│   - Defines API contracts                            │
│   - Sets test strategy                               │
│   Output: architecture_spec                          │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ PHASE 1: JUNIOR ("get it working")                  │
│   - First draft implementation                       │
│   - Happy-path tests                                 │
│   └─ VALIDATOR GATE 1 (compile + pytest)            │
└─────────────────────────────────────────────────────┘
    │ (intelligent reprise: mid reads junior's code)
    ▼
┌─────────────────────────────────────────────────────┐
│ PHASE 2: MID ("make it right")                      │
│   - Refactor for clarity                             │
│   - Error handling                                   │
│   - Test coverage                                    │
│   └─ VALIDATOR GATE 2                                │
└─────────────────────────────────────────────────────┘
    │ (intelligent reprise: senior reads mid's work)
    ▼
┌─────────────────────────────────────────────────────┐
│ PHASE 3: SENIOR ("make it robust")                  │
│   - Performance optimization                         │
│   - Security review                                  │
│   - Architecture validation                          │
│   └─ VALIDATOR GATE 3                                │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ PHASE 4: FINAL VALIDATOR (deterministic)            │
│   - Full test suite                                  │
│   - Static analysis                                  │
│   Verdict: PASS / FAIL                               │
└─────────────────────────────────────────────────────┘
```

## Role Philosophies

| Role     | Mindset                        | What they prioritize           |
|----------|--------------------------------|-------------------------------|
| JUNIOR   | "Get it working"              | Functional baseline, simple   |
| MID      | "Make it right"               | Error handling, coverage      |
| SENIOR   | "Make it robust"              | Performance, security, review |

## Intelligent Turn Reprise

Each subsequent agent receives the PREVIOUS agent's output and builds on it:
- MID receives: junior's source code + validator test output
- SENIOR receives: mid's source code + validator test output
- This prevents each agent from starting from scratch and ensures continuity

## Validator Gates

After each phase, `run_validator(workspace)` runs:
1. **Compile check** — every `.py` file must parse without SyntaxError
2. **Substantive check** — source must contain real code (not a dict literal)
3. **Pytest** — runs tests if present; fails if no tests ran

## Usage

```python
from pathlib import Path
from code_lab.team_workflow import TeamPipeline

ws = Path("/path/to/workspace")
pipeline = TeamPipeline(ws, language="python")

result = pipeline.run_full(
    prompt="Build a fibonacci function with tests",
    llm_client=real_llm_client,  # optional — deterministic fallback if None
)

print(pipeline.get_turn_summary())
```

## Integration with Code Lab Engine

The `TeamPipeline` is designed to be consumed by the existing `CodeLabEngine`:
- Each phase maps to a stage in the engine's pipeline
- Validator results feed into the engine's iteration tracking
- Turn summaries can be logged via the event bus

## Pitfalls

1. **LLM client required for multi-agent mode** — without it, each phase returns empty and the pipeline fails gracefully at Phase 0.
2. **Validator gate is strict** — if junior code doesn't compile, the pipeline stops. This is intentional: bad baseline → no point refining.
3. **Intelligent reprise requires readable source** — if the previous agent outputs garbage, the next agent inherits it. The validator gate catches this.
4. **Phantom output detection** — a file containing `{}` or `[]` compiles but fails the substantive check. The validator flags this as `phantom_output`.
5. **No silent fallbacks** — if an LLM call fails, the error is recorded and the pipeline continues to the next phase (with degraded input), never fabricating results.

## Files

- `code_lab/team_workflow.py` — implementation
- `tests/test_team_workflow.py` — tests (13 passing)
