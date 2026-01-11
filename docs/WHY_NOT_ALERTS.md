# Why Driftline Is Not an Alerting System

Most operational tooling is built around alerts.

Alerts are fast, reactive, and easy to trigger — but they are fundamentally
incapable of modeling long-lived operational risk.

Driftline exists because alerts fail at the exact moment understanding matters most.

---

## Alerts Model Events, Not State

Alerts answer one question:

> “Did something change right now?”

They do not answer:

- How long has the system been diverging?
- Has this deviation happened before?
- Is the risk accumulating or stabilizing?
- Was this divergence intentional?
- Why does this drift matter operationally?

Once an alert fires and is cleared, context is lost.

---

## Operational Risk Persists Even When Alerts Stop

Configuration drift rarely causes immediate failure.

Instead:
- Small deviations accumulate
- Teams normalize broken states
- Baselines quietly rot
- Risk compounds invisibly

Alerting systems optimize for **reaction speed**, not **situational understanding**.

Driftline models drift as a **state that persists across time**.

---

## Incidents vs Alerts

Alerts are disposable.
Incidents are durable.

Driftline incidents:
- Persist until explicitly resolved
- Aggregate repeated drift
- Preserve historical context
- Represent ongoing operational risk

This mirrors how real operators reason about systems.

---

## Determinism Beats Creativity in Operations

Many modern tools generate explanations dynamically.

This creates a dangerous failure mode:
- The same issue produces different explanations
- Operator trust erodes
- Accountability becomes unclear

Driftline explanations are deterministic and reusable.

The same drift under the same conditions always yields the same explanation.

This is a non-negotiable property.

---

## Driftline Complements Alerts — It Does Not Replace Them

Alerts are useful for:
- Immediate failures
- Paging humans
- Time-sensitive response

Driftline is useful for:
- Understanding why systems are fragile
- Tracking long-lived risk
- Making intentional baseline decisions
- Preserving operational memory

The two systems serve different purposes.

Driftline intentionally does not do alerting.
