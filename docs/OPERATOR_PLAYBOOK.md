# Driftline Operator Playbook

This document describes how Driftline is intended to be used by operators
during real system operation.

It is not a feature reference.
It is a decision guide.

---

## When an Incident Is OPEN

An OPEN incident indicates that drift is present and operationally relevant.

### Operator actions:
- Review the attached explanation
- Inspect the affected components
- Decide whether the drift is expected or accidental

Do **not** rush to resolve.
Driftline is designed to persist state until intent is clear.

---

## When to ACK an Incident

ACK signals awareness without resolution.

Use ACK when:
- the drift is understood
- remediation is planned
- the change is intentional but incomplete

ACK prevents loss of context while avoiding premature resolution.

---

## When to Resolve an Incident

Resolve only when:
- the system has returned to baseline, **or**
- a new baseline has been intentionally set

Resolution is a statement of confidence, not just absence of drift.

---

## When to Reset a Baseline

Resetting a baseline is an operational decision.

Do this when:
- the new system state is correct
- drift is no longer meaningful
- future comparisons should treat the current state as normal

Baseline resets resolve all active incidents for the source.

---

## How to Interpret Reused Explanations

If the same explanation appears across incidents, this is intentional.

It indicates:
- the same underlying drift condition
- recurring operational risk
- unresolved systemic issues

Reused explanations build long-term operational memory.

---

## What Driftline Will Never Do Automatically

- Auto-resolve incidents
- Auto-reset baselines
- Escalate without context

Human intent is always required.

---

## Mental Model

Think of Driftline as a **risk ledger**, not an alarm system.

It remembers what systems drifted,
why it mattered,
and whether anyone made a decision about it.
