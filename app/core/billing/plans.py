# app/core/billing/plans.py

PLAN_LIMITS = {
    "FREE": {
        "EXPLANATION_GENERATED": 1,
    },
    "PRO": {
        "EXPLANATION_GENERATED": 100,
    },
    "ENTERPRISE": {
        "EXPLANATION_GENERATED": None,  # unlimited
    },
}
