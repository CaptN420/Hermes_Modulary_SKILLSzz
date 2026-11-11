---
name: autonomous-decision-engine
description: Build telemetry-driven decision systems with pattern analysis.
category: software-development
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autonomous, decision-engine, telemetry, optimization, patterns]
    related_skills: [systematic-debugging, test-driven-development]
---

# Autonomous Decision Engine

## Overview

Build systems that collect telemetry, analyze patterns, and make deterministic recommendations.

**Core principle:** Decisions must be traceable, reproducible, and safe.

**When to use:** When a system has observable metrics (token usage, latency, error rates) and needs to optimize configuration automatically.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Telemetry      │────▶│  Pattern        │────▶│  Decision       │
│  Collection     │     │  Analyzer       │     │  Engine         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                      │
                                                      ▼
                                               ┌─────────────────┐
                                               │  Recommendation │
                                               │  (mode, confidence)│
                                               └─────────────────┘
                                                      │
                                                      ▼
                                               ┌─────────────────┐
                                               │  Production     │
                                               │  Guard          │
                                               └─────────────────┘
```

## Procedure

### 1. Define Decision Space

Before collecting telemetry, define:
- What modes/configurations exist?
- What are the decision thresholds?
- What actions can be taken?

**Example:** Token economy has 4 modes: `off`, `fixed`, `adaptive`, `canary`.

```python
class BudgetMode(str, Enum):
    OFF = "off"
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    CANARY = "canary"
```

### 2. Collect Telemetry

Aggregate metrics from all relevant sources:
- Runtime telemetry (hermes_profiler, context_budget)
- Performance data (latency, error rates)
- Configuration state (current mode, thresholds)

**Pitfall:** Don't collect raw user content — only scalar metrics.

```python
class TelemetrySummary:
    total_requests: int = 0
    budget_enabled_requests: int = 0
    avg_reduction_pct: float = 0.0
    overflow_count: int = 0
    system_exceeded_count: int = 0
```

### 3. Analyze Patterns

Identify trends that trigger decisions:
- Overflow patterns → enable adaptive mode
- Low savings → consider switching modes
- System pressure → manual review needed
- Tool irrelevance → enable necessity gate

**Pitfall:** Each pattern must have a clear threshold — don't use fuzzy logic.

```python
class PatternAnalysis:
    has_overflow: bool = False
    insufficient_savings: bool = False
    system_pressure: bool = False
    tool_irrelevance: bool = False
```

### 4. Apply Decision Rules

Use deterministic rules to generate recommendations:
- Rule 1: `overflow_count > 0` → enable adaptive (confidence: 90%)
- Rule 2: `avg_reduction_pct < 5%` → consider switching modes (confidence: 70%)
- Rule 3: `system_exceeded_count > 0` → manual review (confidence: 50%)

**Pitfall:** Confidence scores must reflect actual certainty — don't inflate them.

```python
class DecisionRecommendation:
    current_mode: str = "off"
    recommended_mode: str = "fixed"
    confidence: float = 0.0      # 0.0-1.0
    reasoning: List[str] = []
    expected_savings_pct: float = 0.0
    risks: List[str] = []
```

### 5. Enforce Safety Guards

Critical environment variables require production guard approval:
- `CAPTN_CONTEXT_BUDGET` — protected
- `CAPTN_ADAPTIVE_ROUTING` — protected

**Pitfall:** Always default to `dry_run=True` for recommendations.

```python
def apply_recommendation(self, dry_run: bool = True) -> Dict[str, Any]:
    # Check ProductionGuard constraints
    if var in ("CAPTN_CONTEXT_BUDGET", "CAPTN_ADAPTIVE_ROUTING"):
        if not dry_run:
            logger.warning("BLOCKED: %s requires production guard approval", var)
```

### 6. Log All Decisions

Every decision must be auditable:
- Timestamp
- Input telemetry summary
- Identified patterns
- Recommendation with reasoning
- Confidence score
- Expected outcomes

**Pitfall:** Export decisions to JSONL for analysis — don't lose the audit trail.

```python
def export_decision_log(self, path: str) -> str:
    with open(path, "w", encoding="utf-8") as f:
        for record in self.decision_log:
            f.write(json.dumps(record, default=str) + "\n")
```

## Decision Rules Reference

| Rule | Condition | Action | Confidence |
|------|-----------|--------|------------|
| 1 | `overflow_count > 0` | Enable adaptive mode | 90% |
| 2 | `avg_reduction_pct < 5%` with fixed | Consider switching to adaptive | 70% |
| 3 | `system_exceeded_count > 0` | Manual review recommended | 50% |
| 4 | High T3 tool drops | Enable necessity gate | 60% |
| 5 | Canary shows >10% better savings | Promote to adaptive | 80% |

## CLI Integration

Register commands in `_devtools.py`:

```python
# In captn/cli/_devtools.py
try:
    from captn.runtime.token_economy_orchestrator import register_cli as _reg_orch
    _reg_orch(dev_sub)
except Exception as exc:
    logger.warning("devtools token_orchestrator not available: %s", exc)
```

Expose subcommands:
- `analyze` — Show current state and recommendation
- `apply` — Apply recommendation (dry-run by default)
- `log` — View decision history

## Verification

Test the orchestrator with sample data:

```python
from captn.runtime.token_economy_orchestrator import TokenEconomyOrchestrator

orch = TokenEconomyOrchestrator(dry_run=True)
rec = orch.analyze_and_recommend()

print(f"Current: {rec.current_mode}")
print(f"Recommended: {rec.recommended_mode}")
print(f"Confidence: {rec.confidence:.0%}")
print(f"Reasoning: {rec.reasoning}")
```

Expected output:
- Fresh install (no telemetry): recommends `fixed` mode
- Overflow detected: recommends `adaptive` mode with 90% confidence
- Low savings: recommends switching to `adaptive` with 70% confidence

## Pitfalls

1. **Collecting raw user content** — Only collect scalar metrics, never prompt/memory/tool content.
2. **Inflating confidence scores** — Confidence must reflect actual certainty, not optimism.
3. **Skipping dry-run mode** — Always default to `dry_run=True` for safety.
4. **Losing audit trail** — Export all decisions to JSONL for analysis.
5. **Ignoring ProductionGuard** — Critical env vars require human approval.

## Files Structure

```
captn/runtime/token_economy_orchestrator.py  # Main orchestrator
captn/cli/_devtools.py                       # CLI registration
scripts/token_orchestrator_demo.py           # Demo/testing
logs/token_economy_decisions.jsonl          # Decision history
docs/TOKEN_ECONOMY_ORCHESTRATOR.md         # Documentation
```
