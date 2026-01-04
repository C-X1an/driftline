# Driftline Demo Walkthrough

This walkthrough demonstrates how Driftline detects, explains, and manages
configuration drift over time.

## Scenario

We start with a system that has a known-good baseline configuration.

## Step 1: Baseline Established
- A baseline snapshot is captured
- No incidents exist

## Step 2: Configuration Drift Introduced
- A configuration value changes
- Driftline detects divergence
- A risk assessment is generated
- An incident is created

## Step 3: Explanation Generated
- A deterministic explanation is attached
- Operators can see *why* the drift matters

## Step 4: Drift Persists
- Drift continues across time
- No duplicate explanations are generated
- Incident remains OPEN

## Step 5: Baseline Reset
- Operator resets the baseline
- Incident is RESOLVED
- Baseline reset explanation is recorded

## Outcome

Driftline preserved:
- historical context
- operator intent
- reasoning behind decisions
