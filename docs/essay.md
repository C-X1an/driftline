# Why Configuration Drift Is a State, Not an Event

Modern systems rarely fail because of a single bad change.
They fail because small deviations accumulate silently until behavior no longer
matches assumptions.

Yet most operational tooling still treats drift as an event:
a diff, an alert, a notification that appears briefly and then disappears.

This mental model is the root cause of alert fatigue, missed risk, and brittle systems.

---

## The Problem With Change-Based Thinking

Most infrastructure and configuration tools are designed to answer one question:

> What changed?

They surface diffs, commits, alerts, and policy violations.
Each signal is treated independently, evaluated in isolation, and then dismissed
once acknowledged.

This approach assumes that:
- changes are discrete
- impact is immediate
- risk expires when alerts are closed

In real systems, none of these assumptions hold.

---

## Drift Is Not Noise, It Is Accumulation

Configuration drift rarely manifests as a sudden failure.
Instead, it compounds:

- a timeout slightly increased
- a feature flag left enabled
- a dependency version slowly diverging
- a runtime value drifting from documented intent

Each individual change may appear harmless.
Together, they alter system behavior in ways that are difficult to reason about.

Drift is not noisy.
It is quiet.

---

## Events Expire, Risk Persists

Alerts are ephemeral.
Once acknowledged, they disappear from dashboards and minds alike.

Risk does not.

A system that has drifted remains drifted until the underlying state changes.
Suppressing alerts does not reduce risk.
Closing tickets does not restore alignment.

Operational risk persists across time, even when no new events occur.

---

## Baselines Are Decisions, Not Facts

Most systems implicitly treat baselines as objective truth.
In practice, baselines are intentional decisions made by operators.

Choosing a baseline means declaring:
> “This state represents what we currently believe is correct.”

Baselines can be wrong.
They can be outdated.
They can be reset.

Treating baselines as explicit, auditable decisions acknowledges the human
judgment embedded in operational systems.

---

## Why Explanations Must Be Deterministic

Operators rely on explanations to build trust and understanding.
If identical drift conditions produce different explanations, confidence erodes.

Creative or non-deterministic explanations may be impressive,
but they are unsuitable for operational reasoning.

Explanations must be:
- stable
- repeatable
- auditable

Determinism is not a limitation.
It is a prerequisite for trust.

---

## What a Drift-Native System Looks Like

A drift-native system does not ask:
> “What just changed?”

It asks:
> “How far has reality diverged from what we believe to be true?”

Such a system:
- models state over time
- compares against explicit baselines
- evaluates risk, not raw change
- persists incidents until resolution
- reuses explanations for identical conditions

This shifts operations from reaction to understanding.

---

## Driftline

Driftline is an implementation of these ideas.

It models configuration drift as persistent operational risk,
not transient events.

By treating drift as a state, baselines as decisions,
and explanations as deterministic artifacts,
Driftline helps teams reason about system behavior over time
without alert fatigue or context loss.
