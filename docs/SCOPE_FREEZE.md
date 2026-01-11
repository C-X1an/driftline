# Driftline v1 Scope Freeze

This document defines the explicit scope boundaries for Driftline v1.

The goal of this freeze is to preserve conceptual integrity, prevent feature drift,
and ensure Driftline remains a coherent operational system rather than a collection
of loosely related capabilities.

---

## In Scope (v1)

Driftline v1 is focused exclusively on:

- Modeling configuration drift as **persistent operational risk**
- Capturing **immutable snapshots** of system state
- Comparing snapshots against **explicit baselines**
- Aggregating drift into **long-lived incidents**
- Attaching **deterministic, reusable explanations**
- Preserving **historical context across time**
- Exposing a clean, composable **API-first interface**

---

## Explicitly Out of Scope (v1)

The following are intentionally excluded from Driftline v1:

- UI dashboards or visualization layers
- Alerting, paging, or notification delivery
- CI / PR / GitHub-native integrations
- Automated remediation or self-healing
- Policy enforcement or compliance checking
- Real-time streaming guarantees
- Human-in-the-loop approval workflows
- Machine-learning–based explanation generation

---

## Non-Goals

Driftline v1 does **not** attempt to:

- Replace alerting systems
- Summarize changes for human review
- Predict failures
- Optimize for immediate reaction time
- Provide end-to-end platform coverage

---

## Rationale

Driftline intentionally prioritizes:

- Determinism over creativity
- Persistence over immediacy
- Understanding over reaction speed
- Explicit operator intent over automation

Expanding scope before these guarantees are rock-solid would weaken trust,
auditability, and long-term system clarity.

---

## Scope Changes

Any expansion beyond this scope requires:

- A written design note
- A clear invariants analysis
- A justification grounded in operational reality

Until then, this scope is frozen.
