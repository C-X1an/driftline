# Driftline FAQ

This document answers common questions about Driftline’s design,
scope, and intended use. It is written to clarify intent, tradeoffs,
and non-goals rather than to market features.

---

## What problem does Driftline actually solve?

Driftline solves the problem of **silent operational risk caused by configuration drift over time**.

In real systems, failures rarely happen immediately after a change.
Instead, small deviations accumulate until the system becomes fragile,
unpredictable, or difficult to reason about.

Most tools focus on *detecting changes*.
Driftline focuses on *modeling risk* that persists across time.

---

## How is this different from config diffing or change detection?

Config diffing answers:
> “What changed?”

Driftline answers:
> “Is the system currently operating outside its intended state, and does that pose risk?”

Key differences:
- Driftline is **stateful**, not event-driven
- Driftline tracks **persistence of drift**, not one-off changes
- Driftline aggregates repeated detections into a single incident
- Driftline preserves historical context even after resolution

---

## Why model incidents instead of emitting alerts?

Alerts are ephemeral.  
Risk is persistent.

Driftline models drift as **incidents** because:
- risk exists even when no new changes occur
- repeated alerts hide the true duration of a problem
- operators need a stable object to reason about over time

Incidents remain OPEN until the underlying risk is resolved or explicitly acknowledged.

---

## Why are explanations deterministic?

Operators must be able to trust explanations.

If the same drift condition produces different explanations across runs,
confidence erodes quickly.

Driftline explanations are:
- deterministic
- idempotent
- cached and reused

The same drift conditions always produce the same explanation.
This builds trust, auditability, and long-term confidence in the system.

---

## Why are explanations reusable across incidents?

Driftline separates **cause** from **occurrence**.

The same underlying drift can:
- recur after resolution
- affect multiple systems
- resurface after a baseline reset

Reusing explanations ensures:
- consistent reasoning
- reduced cognitive load
- stable operational narratives

Incidents may be transient, but explanations represent enduring insight.

---

## Why are baselines explicit instead of automatic?

Baselines represent **intent**, not observation.

Automatically shifting baselines hides risk and erases accountability.
Driftline requires explicit baseline resets to ensure:

- operators consciously accept new system state
- historical drift remains auditable
- incidents are resolved intentionally, not silently

Baseline resets are treated as first-class operational events.

---

## What happens when drift goes away on its own?

If the system returns to its baseline state:
- the incident is resolved
- historical context is preserved
- explanations remain attached for auditability

Driftline does not delete or collapse history.
Resolution is a state transition, not data loss.

---

## What happens when a baseline is reset?

When a baseline is reset:
- a new snapshot becomes the reference state
- all active incidents for that source are resolved
- a baseline-reset explanation is generated (idempotently)

Baseline explanations are system-scoped and not tied to risk assessments,
because they represent **operator intent**, not detected drift.

---

## Why is there no UI?

Driftline is API-first by design.

Early focus is on:
- correctness
- semantics
- determinism
- integration flexibility

A UI can be built later.
Semantics cannot be fixed easily once exposed.

---

## Is Driftline an AI product?

No.

AI is used only where it provides **structured, deterministic value**.
Driftline avoids non-deterministic or creative outputs.

The core system remains:
- rules-driven
- stateful
- explainable
- auditable

---

## Who is this NOT for?

Driftline is not designed for:
- toy projects
- one-off configuration diffs
- teams seeking instant alerting
- environments without operational ownership

It is intentionally opinionated and favors clarity over convenience.

---

## What are the current limitations?

Current limitations include:
- no UI
- no notification integrations
- limited source types
- manual baseline management

These are deliberate tradeoffs to preserve correctness and trust early.

---

## What would Driftline look like in a larger organization?

In larger environments, Driftline could:
- model drift budgets per system
- track long-horizon risk accumulation
- correlate drift across dependencies
- integrate with incident management tooling

The core abstraction — drift as persistent risk — remains unchanged.
