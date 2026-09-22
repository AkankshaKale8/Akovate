def calculate_roi(brief=None):
    brief = brief or {}
    spend = int(float(brief.get("budget", 500000) or 500000))
    objective = str(brief.get("objective", "Awareness")).lower()

    multiplier = {
        "awareness": 4.8,
        "leads": 4.4,
        "sales": 5.1,
        "app installs": 4.2,
        "community growth": 3.9,
        "engagement": 4.2,
    }.get(objective, 4.5)

    revenue = int(spend * multiplier)
    reach = int(spend * 1.64)
    conversions = max(1, int(spend / 104))

    return {
        "spend": spend,
        "revenue": revenue,
        "reach": reach,
        "conversions": conversions,
        "roas": round(revenue / spend, 1),
        "cpa": round(spend / conversions),
    }
