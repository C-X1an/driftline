# Driftline Design Notes

This document explains several intentional design decisions in Driftline.
These choices are opinionated and trade flexibility for clarity and trust.

---

## Why Drift Is Modeled as State, Not Events

Most monitoring systems treat change as an event.
This leads to alert storms, duplicated signals, and lost context.

Driftline models drift as *state*:
- drift persists until resolved
- repeated detections reinforce the same incident
- resolution is explicit and meaningful

This allows operators to reason about ongoing risk rather than reacting to noise.

---

## Why Incidents Persist Across Time

Incidents in Driftline are not notifications.
They represent an operational condition.

An incident remains OPEN or ACKED as long as the underlying drift exists.
This preserves context and prevents fragmentation of understanding across time.

Resolution marks a true change in operational reality.

---

## Why Explanations Are Deterministic and Reused

Driftline explanations are keyed and cached.

If identical drift conditions occur:
- the explanation is reused
- wording does not change
- meaning remains stable

This avoids the trust erosion caused by non-deterministic AI output.
Operators should never question whether the system is “making things up.”

---

## Why Baselines Are Explicit Operator Decisions

Baselines are never inferred or auto-shifted.

A baseline represents an intentional statement:
“This is what we believe is correct.”

Resetting a baseline:
- resolves active incidents
- creates an audit trail
- preserves historical explanations

This makes baseline changes visible, reversible, and accountable.

---

## Tradeoffs Accepted

Driftline intentionally accepts:
- fewer alerts
- slower initial detection
- more operator intent

In exchange for:
- higher signal quality
- stable reasoning
- long-term operational clarity

These tradeoffs are deliberate.
