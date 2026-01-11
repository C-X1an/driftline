# How Driftline Differs From Other Approaches

Driftline does not attempt to replace existing tooling.
It addresses a different problem.

This document explains how Driftline’s model differs from
common approaches to configuration and incident management.

---

## Driftline vs Change Alerts

Change alerts focus on immediacy:
a file changed, a value changed, a rule was violated.

These alerts are typically acknowledged and discarded.

Driftline models persistence.
If drift continues to exist, the incident remains open.
Risk does not expire when alerts are silenced.

---

## Driftline vs CI and Git Diffs

CI systems compare declared intent to declared changes.
They operate before code reaches runtime.

Driftline observes runtime reality.
It evaluates how the live system behaves relative to its baseline,
regardless of how the state was introduced.

CI prevents mistakes.
Driftline detects divergence.

---

## Driftline vs Configuration Scanners

Configuration scanners focus on compliance:
whether systems match predefined rules or standards.

Driftline focuses on operational risk.
A configuration may be compliant yet risky,
or non-compliant yet operationally harmless.

Risk is contextual.
Driftline preserves that context.

---

## Driftline vs Incident Management Tools

Incident management tools track symptoms:
outages, pages, acknowledgements, resolutions.

Driftline tracks underlying drift.
It captures the conditions that lead to incidents
before user-facing failures occur.

Driftline incidents persist across time
until the system state meaningfully changes.

---

## Summary

Most tools answer:
> “What happened?”

Driftline answers:
> “What state is the system in, and how risky is that state?”

This distinction is subtle.
Its impact on operational clarity is not.
