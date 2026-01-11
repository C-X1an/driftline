# Driftline Security Model

Driftline is designed as an operational intelligence system, not a control plane.

It does not mutate production systems.
It does not perform remediation.
It does not execute external actions.

This is a deliberate design choice.

---

## Threat Model

Driftline assumes:

- production systems may be misconfigured
- configuration drift is expected
- operators may make mistakes
- historical context may be lost

Driftline does NOT assume:

- adversarial operators
- hostile input from untrusted networks
- public exposure of APIs

---

## Data Integrity

Driftline prioritizes:

- immutability of snapshots
- append-only incident history
- deterministic explanations

This ensures auditability and prevents silent state corruption.

---

## No Implicit Authority

Driftline never:

- modifies system state
- resets baselines automatically
- resolves incidents without operator intent

This prevents:
- unintended remediation
- automation cascades
- hidden system behavior

---

## Future Hardening (Planned)

- role-based access for baseline resets
- explanation signing
- audit log export
- tamper detection

These are intentionally deferred until core semantics are complete.
