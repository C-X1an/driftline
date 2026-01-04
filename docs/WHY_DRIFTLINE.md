# Why Driftline Exists

## The Problem With Configuration Drift

Most production incidents are not caused by sudden changes.
They emerge from small, accumulated deviations between how a system is expected
to behave and how it actually behaves over time.

Existing tools surface:
- raw diffs
- alerts on individual changes
- noisy notifications

They do not model drift as an operational risk that persists, evolves, and
requires human judgment.

---

## Why Drift Is an Incident, Not a Diff

A diff answers “what changed.”
Operators need to know:
- whether the change matters
- whether it compounds existing risk
- whether action is required now or later

Driftline treats drift as an incident because:
- it persists over time
- it has operational impact
- it requires lifecycle management

This aligns drift handling with how teams already respond to outages and failures.

---

## Why Explanations Matter

Raw configuration data does not scale cognitively.
Operators need shared understanding, not just data.

Driftline explanations exist to:
- reduce interpretation cost
- standardize reasoning across teams
- preserve institutional knowledge

Explanations must be deterministic.
If the same drift produces different explanations, trust is lost.

---

## What Driftline Does Differently

Driftline:
- models system state over time
- anchors drift against explicit baselines
- aggregates repeated drift into incidents
- generates stable, reusable explanations
- treats baseline changes as intentional operations

This shifts drift management from reactive alert handling to proactive risk
management.

---

## Who Driftline Is For

Driftline is designed for:
- small teams running real production systems
- environments with frequent configuration change
- operators who value clarity over noise
- teams that want drift explained, not just detected
