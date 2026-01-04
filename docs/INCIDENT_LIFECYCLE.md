# Incident Lifecycle

This document explains how incidents behave in Driftline from an operator’s
perspective.

---

## OPEN

An incident is OPEN when Driftline detects drift that exceeds risk thresholds.

OPEN means:
- drift is currently present
- the risk assessment indicates attention is required
- no resolution has occurred yet

Operators should:
- review the attached explanation
- determine whether the drift is expected
- decide whether to acknowledge or resolve

---

## ACKED

An incident is ACKED when an operator explicitly marks awareness.

ACKED means:
- the drift is known
- the risk is accepted temporarily
- monitoring continues

This state exists to distinguish “unknown” from “known but deferred”.

---

## RESOLVED

An incident is RESOLVED when the drift is no longer operationally relevant.

Resolution can occur when:
- configuration reverts to baseline
- a new baseline is intentionally set

Resolved incidents retain their explanations and timelines for audit and review.

---

## Explanations

Explanations are attached when incidents are created.
They explain why the drift matters, not just what changed.

Resolved incidents continue to display explanations because:
- they capture reasoning at the time of detection
- they support post-incident analysis
- they preserve operational context
