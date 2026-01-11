# Driftline Invariants

This document defines the non-negotiable guarantees of the Driftline system.

These invariants are treated as correctness properties, not best-effort behavior.

---

## 1. Explanation Determinism

Identical drift conditions must always produce the same explanation.

Driftline guarantees:
- same baseline
- same drift fingerprint
- same risk level

→ same explanation_id

No regeneration is allowed.

---

## 2. Incident Persistence

Once created, an incident persists until explicitly resolved.

Incidents are not auto-closed by time, silence, or alert suppression.

---

## 3. Baseline Intent

Baselines are explicit operator decisions.

The system must never automatically redefine intent.

---

## 4. Auditability

All state transitions must be reconstructible from stored data.

No implicit behavior is allowed.

---

## 5. Idempotency

All state transitions must be safe to repeat.

No duplicate incidents.
No duplicate explanations.
No duplicate baseline events.
