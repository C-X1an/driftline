def get_usage_status(db, org, event_type: str):
    """
    Returns:
    {
        "used": int,
        "limit": int | None,
        "remaining": int | None,
        "percent": float | None,
    }
    """
