# Driftline Anti-Goals

Driftline is intentionally narrow in scope.

This document defines what Driftline explicitly does **not** try to be,
even if those directions might appear attractive.

---

## Driftline Is Not a Notification Engine

Driftline does not aim to send real-time alerts for every change.

Alert fatigue is a failure mode, not a feature.
Driftline models **persistent risk**, not transient events.

---

## Driftline Is Not a Change Feed

Driftline does not summarize diffs, commits, or configuration changes.

Raw change is cheap.
Understanding whether change **matters** is not.

---

## Driftline Is Not a CI or Deployment Tool

Driftline does not gate builds, block deploys, or enforce policy.

It is designed to observe systems **after** they exist in the real world.

---

## Driftline Is Not a Compliance Checklist

Driftline does not encode static rules or frameworks.

Risk is contextual and temporal.
Compliance is static.

---

## Driftline Is Not an AI Creativity System

Explanations in Driftline are deterministic and idempotent.

Creative or personalized explanations undermine trust.
Operators need consistency, not novelty.

---

## Why These Anti-Goals Exist

Each rejected direction trades short-term appeal for long-term clarity.

Driftline optimizes for:
- trust over excitement
- signal over volume
- operational memory over automation

Any future feature must preserve these properties.
