def risk_tier(magnitude: float) -> str:
    if magnitude < 0.2:
        return "LOW"
    elif magnitude < 0.6:
        return "MODERATE"
    else:
        return "HIGH"
