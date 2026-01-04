# Driftline — Whiteboard Explanation

## 1. The Problem

In real systems, configuration rarely fails immediately.  
Instead, small deviations accumulate silently over time until the system becomes fragile and unpredictable.

Most operational failures occur long after the original change, when context is already lost and teams can no longer explain *why* the system behaves the way it does.

Existing tools surface changes or alerts, but they do not model ongoing operational risk.

---

## 2. Why Existing Tools Fail

Most operational tooling is event-driven and stateless:

- Change detectors report *what changed*, not whether it matters
- Alerting systems fire repeatedly without modeling persistence
- Risk is evaluated moment-by-moment instead of over time
- Explanations vary between runs, eroding operator trust
- Historical context disappears once alerts are cleared

These tools optimize for reaction speed, not understanding.

---

## 3. Core Insight

**Drift is not an event — it is a state that persists over time.**

Operational risk emerges from:
- how long reality diverges from expectations
- how severe that divergence becomes

To reason about risk, systems must model **state, history, and intent**, not just changes.

Driftline is built around this insight.

---

## 4. Key Entities and State

Driftline models configuration drift as a state machine:

- **Snapshot**  
  An immutable, normalized record of system state at a point in time.

- **Baseline**  
  An explicitly chosen snapshot representing intended system state.

- **Drift Signal**  
  Structured divergence between the baseline and a newer snapshot, with a stable fingerprint.

- **Risk Assessment**  
  Evaluation of operational severity and magnitude derived from a drift signal.

- **Incident**  
  A persistent operational event that represents ongoing risk.

- **Explanation**  
  A deterministic, reusable description of why the drift matters operationally.

Data flows forward, but incidents persist until explicitly resolved.

---

## 5. Incident Lifecycle

Incidents represent ongoing risk, not one-off alerts.

- **OPEN** — drift exceeds thresholds and is actively present  
- **ACKED** — operators are aware, but risk still exists  
- **RESOLVED** — drift is no longer operationally relevant  

Incidents are resolved explicitly, either by reverting configuration or by resetting the baseline.

This preserves accountability and historical context.

---

## 6. Deterministic Explanations

Operators must be able to trust explanations.

Driftline explanations are:
- deterministic
- idempotent
- cached and reused

The same drift conditions always produce the same explanation.

Explanations are attached to incidents but are not owned by them, allowing reuse across repeated incidents caused by the same underlying drift.

This avoids “AI roulette” and builds long-term operator confidence.

---

## 7. Tradeoffs and Non-Goals

Driftline makes deliberate tradeoffs:

- No UI dashboards — API-first by design
- No auto-remediation — intent remains human-driven
- Fewer alerts — higher signal quality
- Slower analysis — stronger guarantees and determinism

These choices prioritize trust, auditability, and correctness over speed.

---

## 8. What I’d Build Next

The next step is long-horizon risk modeling.

Instead of evaluating drift at a single point in time, Driftline can score risk based on:
- duration of drift
- repeated reoccurrence
- baseline churn frequency

This enables concepts like **drift budgets** and **risk decay**, moving from detection toward strategic operational insight.
