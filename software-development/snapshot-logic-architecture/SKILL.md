---
name: snapshot-logic-architecture
category: software-development
description: Use for LearningBus, Snapshot, and Security Gate logic.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [architecture, rbac, snapshot, learningbus]
    related_skills: [autonomous-decision-engine, life-mean]
---

# Snapshot Logic & State Architecture

## Core Philosophy
The system operates on a "Bridge" architecture where three independent states are fused into a single **Unified Snapshot** to create a dynamic, context-aware permission system.

## 1. The Three Independent States (Sources)
- **Security Gate (The Law):** Static RBAC (Role-Based Access Control). Defines absolute limits (e.g., "Only ADMIN can load models").
- **LearningBus (The Competency):** Dynamic logs of user actions. Captures raw evidence of what the user has learned or attempted.
- **Snapshot (The Bridge):** The logical fusion of the Gate and the Bus. It represents the "Source of Truth" for the current moment.

## 2. The Batch Process (Distillation)
The `BatchProcessor` acts as the compiler. It transforms raw logs into a stable state:
1. **Analysis:** Scans `LearningBus` for "acquis" (validated concepts).
2. **Diffing:** Compares new acquis against the previous `Snapshot`.
3. **Version_Manager:** Increments the version (v1.1.a -> v1.1.b) and generates a new `active_snap.json`.
4. **Rollback:** Can revert the `active_snap.json` to any previous version in the `snapshots/` directory.

## 3. Unified Snapshot Schema
The Snapshot is a single JSON object containing:
- `version`: String (e.g., "v1.2.a")
- `timestamp`: ISO8601
- `context`: 
    - `identity`: (Role, Permissions from Gate)
    - `competencies`: (List of validated acquis from Bus)
    - `constraints`: (Path limits, depth limits)
- `active_roadmap_step`: Current goal
- `build_notes`: The "thought process" (feedback) of the Batch.

## 4. The "Bridge" Logic (Decision Engine)
The Decision Router (`Routeur de Décision`) uses the Snapshot to authorize actions:
`Permission = (User_Role_Has_Right) AND (User_Has_Validated_Competency)`

## 5. Time Travel & Reconstruction
Because sources are independent, the system can reconstruct any past state by re-applying a specific Gate state and a specific Bus state to the Bridge logic.
