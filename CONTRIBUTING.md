# Contributing to Driftline

Thanks for your interest in contributing to Driftline.

Driftline is an opinionated system with strong architectural constraints.
Please read this document before opening issues or pull requests.

---

## Project Philosophy

Driftline is built around a few non-negotiable ideas:

- Drift is a **state**, not an event
- Risk matters more than raw change
- Explanations must be deterministic and reusable
- Incidents must persist across time
- Baselines represent explicit operator intent

Any contribution must preserve these properties.

---

## What Makes a Good Contribution

Good contributions tend to:
- improve correctness or clarity
- reduce ambiguity in system behavior
- strengthen determinism or auditability
- clarify documentation or operator intent
- add tests that enforce invariants

Small, focused changes are preferred.

---

## What We Are Unlikely to Accept

The following are unlikely to be accepted without strong justification:

- alerting or notification features
- automatic incident resolution
- non-deterministic explanation generation
- UI or frontend work
- CI/CD or deployment gating logic
- features that optimize for noise over signal

These directions conflict with Driftline’s goals.

---

## Code Guidelines

- Favor explicit logic over clever abstractions
- Determinism > flexibility
- Avoid implicit side effects
- Make state transitions obvious
- Prefer idempotent operations

If behavior is important, it should be testable.

---

## Database & Migrations
