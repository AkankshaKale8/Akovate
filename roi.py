def calculate_roi():
    spend = 500000
    revenue = 2400000
    reach = 820000
    conversions = 4800
    return {
        "spend": spend,
        "revenue": revenue,
        "reach": reach,
        "conversions": conversions,
        "roas": round(revenue / spend, 1),
        "cpa": round(spend / conversions),
    }
