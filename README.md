# Driftline

Operational risk intelligence for configuration drift.

Driftline detects configuration drift, models it as incidents,
and attaches deterministic explanations that operators can trust.

---

📖 **New to Driftline?**  
Start with the [Demo Walkthrough](docs/DEMO.md) to see how Driftline models
configuration drift as operational risk over time.

---

## Philosophy

Driftline is built on a simple belief:

> Configuration drift is a state that accumulates over time, not an event that happens once.

Most operational tools react to changes.
Driftline models risk.

---

## What Driftline Is Not

- Not a change summarizer
- Not a CI or PR bot
- Not a compliance scanner
- Not an alerting system
- Not an AI wrapper

Driftline is intentionally stateful, opinionated, and risk-focused.

---

## Who Driftline Is For

Driftline is designed for:
- engineers operating real systems
- teams dealing with long-lived configuration drift
- environments where alerts are cheap but understanding is expensive

It is not designed for toy demos or one-off change tracking.

---

## What Problem Does This Solve?

Configuration drift rarely causes immediate failures.
Instead, small deviations accumulate silently until systems behave in
unexpected and fragile ways.

Most tools surface raw changes or alerts.
Driftline models drift as operational risk that persists over time.

---

## How Driftline Works (High Level)

- Capture normalized system snapshots over time
- Define explicit baselines as reference points
- Detect drift relative to the active baseline
- Assess operational risk
- Create incidents with clear lifecycles
- Attach deterministic, reusable explanations

---

## Why Deterministic Explanations Matter

Operators need consistent reasoning, not creative output.
If the same drift produces different explanations, trust erodes.

Driftline explanations are deterministic and idempotent by design.

---

## API Overview

Driftline exposes endpoints for:
- incident listing and filtering
- incident timelines
- explanation metrics
- baseline reset operations

The API is designed to be composable with existing operational tooling.

---

## Why This Matters in Production

In real systems, configuration drift is inevitable.
What matters is not preventing drift, but understanding when it becomes risk.

Driftline helps teams:
- detect drift early without alert fatigue
- reason about operational impact, not just change
- preserve historical context across incidents
- make intentional baseline decisions without losing auditability

---

## Design Principles

Driftline is built around a small set of non-negotiable principles:

- Drift is a state, not an event
- Risk matters more than raw change
- Deterministic explanations build trust
- Incidents must persist across time
- Baselines are explicit operator decisions

These principles guide every architectural decision in the system.

---

## Project Status

Driftline is production-grade at the backend layer and under active iteration.

Current focus:
- hardening incident semantics
- explanation determinism guarantees
- operational UX via API design

Non-goals (for now):
- UI dashboards
- notification integrations
- automated remediation
