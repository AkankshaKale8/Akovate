import pandas as pd


def match_creators(creators, brief):
    audience_text = str(brief.get("audience", "")).lower()
    objective = str(brief.get("objective", "")).lower()
    budget = float(brief.get("budget", 500000) or 500000)

    rows = []

    for _, c in creators.iterrows():
        location_fit = 100 if str(c["city"]).lower() == "hyderabad" else 75
        engagement_fit = min(float(c["engagement_rate"]) * 10, 100)

        score = round(
            0.30 * c["audience_fit"]
            + 0.25 * c["content_fit"]
            + 0.10 * location_fit
            + 0.15 * engagement_fit
            + 0.10 * c["sustainability_fit"]
            + 0.10 * c["budget_fit"]
        )

        strengths = []
        tradeoffs = []

        if c["audience_fit"] >= 90:
            strengths.append("strong audience alignment")
        else:
            tradeoffs.append("audience fit can be improved")

        if c["content_fit"] >= 92:
            strengths.append("strong content-format fit")
        else:
            tradeoffs.append("content fit is not the strongest signal")

        if c["engagement_rate"] >= 7:
            strengths.append("above-average engagement")
        else:
            tradeoffs.append("engagement is more moderate")

        if c["sustainability_fit"] >= 88:
            strengths.append("good sustainability alignment")

        if location_fit == 100:
            strengths.append("same-city collaboration advantage")
        else:
            tradeoffs.append("requires remote or travel coordination")

        objective_note = f"for the {objective or 'campaign'} objective"
        audience_note = (
            f" against the audience brief: {audience_text[:70]}"
        )

        explanation = (
            f"Recommended {objective_note}{audience_note}. "
            f"Score is based on audience (30%), content (25%), "
            f"location (10%), engagement (15%), sustainability (10%) "
            f"and budget (10%)."
        )

        rows.append(
            {
                "creator": c["creator"],
                "city": c["city"],
                "category": c["category"],
                "match_score": score,
                "engagement_rate": c["engagement_rate"],
                "audience_fit": c["audience_fit"],
                "content_fit": c["content_fit"],
                "sustainability_fit": c["sustainability_fit"],
                "budget_fit": c["budget_fit"],
                "strengths": (
                    ", ".join(strengths)
                    if strengths
                    else "Balanced fit"
                ),
                "tradeoffs": (
                    ", ".join(tradeoffs)
                    if tradeoffs
                    else "No major trade-off in demo data"
                ),
                "explanation": explanation,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("match_score", ascending=False)
        .reset_index(drop=True)
    )
