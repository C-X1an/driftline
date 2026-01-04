# Driftline Guarantees

Driftline makes the following guarantees by design:

## Deterministic Explanations
Identical drift conditions always produce the same explanation.
No explanation is regenerated unless inputs materially change.

## Incident Persistence
Incidents represent operational state, not transient events.
They persist across time until explicitly resolved.

## Baseline Explicitness
Baselines are never inferred.
They are always the result of an explicit operator action.

## Auditability
Historical incidents, explanations, and baseline resets are preserved.
Resolution does not erase context.

## Idempotency
Repeated drift detections do not create duplicate explanations
or fragment operational understanding.
