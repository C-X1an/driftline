# Driftline Architecture

Driftline is an operational system that models configuration drift as incidents,
rather than as isolated changes or alerts. The architecture is designed to
capture system state over time, detect meaningful divergence from expected
baselines, and attach stable, reusable explanations to those events.

Driftline’s core abstraction is that configuration drift is not an event,
but a **stateful condition** that must be tracked, reasoned about, and resolved
over time.

This document describes the core concepts and design decisions behind Driftline.

---

## Core Concepts

### Source
A Source represents a monitored system or configuration domain. All snapshots,
drift signals, incidents, and explanations are scoped to a source.

### Snapshot
A Snapshot is a normalized representation of a source’s state at a point in time.
Snapshots are immutable and form the historical record used for comparison.

### Baseline
A Baseline is a snapshot explicitly marked as the reference state for a source.
All drift detection compares current snapshots against the active baseline.

Baselines are treated as operational decisions, not automatic system outcomes.

### Drift Signal
A Drift Signal represents detected divergence between the baseline snapshot and
a newer snapshot. It contains structured component-level differences and a
stable drift fingerprint.

### Risk Assessment
A Risk Assessment evaluates the operational severity of a drift signal, producing
a risk level and magnitude. Risk assessments drive incident creation.

### Incident
An Incident models drift as an operational event with a lifecycle:

OPEN → ACKED → RESOLVED

Incidents aggregate repeated drift detections and persist across time until
explicitly resolved. Resolution represents an operational decision, not the
erasure of historical context.

### Explanation
An Explanation is a deterministic, human-readable description of why a drift
matters operationally.

Explanations are attached to incidents but are not owned by them.
They represent reasoning about a *class of drift conditions*, not a single
occurrence, which allows reuse across repeated incidents caused by the same
underlying drift.

---

## Incident Lifecycle

- **OPEN**  
  Created when a new risk assessment exceeds thresholds. Indicates active drift.

- **ACKED**  
  Explicitly acknowledged by an operator to signal awareness without resolution.

- **RESOLVED**  
  Marks that the drift is no longer operationally relevant. Resolution may occur
  due to configuration reversion or baseline reset.

Incidents persist independently of explanations and retain historical context
after resolution.

---

## Explanation Model

Driftline explanations are:

- Deterministic
- Idempotent
- Cached by `explanation_key`

An `explanation_key` is derived from:
- baseline snapshot
- drift fingerprint
- assessed risk level

This ensures identical drift conditions always yield the same explanation.

Explanations encode operational reasoning, not raw change data, and are designed
to be trusted, stable, and reusable over time.

---

## Baseline Reset Semantics

Baseline resets are treated as first-class operational events.

When a baseline is reset:
- A new snapshot becomes the baseline
- All active incidents for the source are resolved
- A system-scoped baseline explanation is generated (idempotently)

Baseline explanations are not tied to risk assessments because they represent
intentional operator action, not detected drift.

This ensures that baseline changes are auditable, explainable, and do not
silently erase historical risk context.

---

## Why This Architecture

This architecture intentionally avoids:
- Alert spam
- Event-based noise
- Non-deterministic AI outputs
- Losing context across time

Tradeoffs made:
- Fewer alerts in exchange for higher signal quality
- Deterministic explanations over creative generation
- Explicit operator intent over automation

The result is a system optimized for trust, auditability, and operational clarity.
