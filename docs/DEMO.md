# Driftline Demo

This demo walks through a complete Driftline lifecycle using a single source.

The goal is to demonstrate how Driftline models configuration drift as
operational risk over time — not as isolated events.

---

## Scenario

We operate a system with a simple configuration:

- `port = 8080`

This value represents a documented operational assumption.

---

## Step 1 — Establish a Baseline

We capture a snapshot and mark it as the baseline.

At this point:
- No drift exists
- No incidents exist
- The system is considered stable

---

## Step 2 — Drift Occurs

The system configuration changes:

- `port = 8080` → `port = 9090`

A new snapshot is captured.

Driftline compares this snapshot to the baseline and detects drift.

---

## Step 3 — Risk Is Assessed

The drift is evaluated for operational risk.

Because this change affects runtime behavior:
- Risk level is assessed as HIGH
- A magnitude is assigned

---

## Step 4 — Incident Is Created

An incident is created with status **OPEN**.

Important properties:
- The incident persists across time
- Repeated detections of the same drift do not create new incidents
- The incident represents an ongoing operational condition

---

## Step 5 — Explanation Is Attached

A deterministic explanation is generated and attached.

The explanation:
- Describes why the drift matters
- Is keyed by baseline, drift fingerprint, and risk level
- Will be reused if the same drift occurs again

---

## Step 6 — Incident Persists

Even if drift is detected repeatedly:
- No new incident is created
- The existing incident remains OPEN
- Historical context is preserved

---

## Step 7 — Baseline Is Reset

An operator explicitly resets the baseline.

This represents intentional acceptance of the new configuration.

Driftline:
- Captures a new baseline snapshot
- Resolves all active incidents for the source
- Records the baseline reset as an operational event

---

## Step 8 — History Is Preserved

After resolution:
- The incident remains queryable
- The explanation remains attached
- Timelines reflect creation, explanation, and resolution

No context is lost.

---

## Why This Matters

Most systems answer:
> “What changed?”

Driftline answers:
> “When did this become operational risk, and why?”

This demo represents the core mental model behind Driftline.
