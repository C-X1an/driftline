# Driftline — 60 Second Pitch

Driftline is an operational risk intelligence system for configuration drift.

Most tools react to changes as isolated events.
Driftline models drift as a persistent state that accumulates risk over time.

The system continuously captures normalized snapshots of system configuration,
compares them against explicit baselines, and evaluates drift severity.
When risk exceeds thresholds, Driftline creates incidents with clear lifecycles
and attaches deterministic explanations operators can trust.

The key design insight is that drift does not disappear just because alerts stop.
Incidents persist until resolved by reversion or intentional baseline resets.

Driftline is optimized for teams running real systems where understanding matters
more than alert volume.
