def campaign_impact(roi, sentiment, viral, green):
    score = round(
        25*min(roi["roas"]/5, 1) +
        25*sentiment["positive"]/100 +
        25*viral["score"]/100 +
        25*green["score"]/100
    )
    return {
        "impact_score": score,
        "summary": "Akovate combines performance, brand health, content readiness and responsible-campaign signals into one decision-support view.",
        "actions": [
            "Prioritize high-fit creators and document the reason for each match.",
            "Use sentiment themes to refine messaging before the next content batch.",
            "Repurpose high-readiness formats while retaining authentic creator voice.",
            "Track sustainability actions alongside business outcomes.",
        ],
    }
