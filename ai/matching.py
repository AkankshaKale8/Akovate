import pandas as pd

def match_creators(creators, brief):
    rows = []
    for _, c in creators.iterrows():
        score = round(
            0.30*c["audience_fit"] +
            0.25*c["content_fit"] +
            0.10*(100 if c["city"].lower() == "hyderabad" else 75) +
            0.15*min(c["engagement_rate"] * 10, 100) +
            0.10*c["sustainability_fit"] +
            0.10*c["budget_fit"]
        )
        explanation = (
            f"Audience fit {c['audience_fit']}/100, content fit {c['content_fit']}/100, "
            f"engagement {c['engagement_rate']}%, sustainability fit {c['sustainability_fit']}/100 "
            f"and budget fit {c['budget_fit']}/100."
        )
        rows.append({
            "creator": c["creator"],
            "city": c["city"],
            "category": c["category"],
            "match_score": score,
            "engagement_rate": c["engagement_rate"],
            "sustainability_fit": c["sustainability_fit"],
            "explanation": explanation,
        })
    return pd.DataFrame(rows).sort_values("match_score", ascending=False).reset_index(drop=True)
