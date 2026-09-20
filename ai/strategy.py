def generate_strategy(objective, product, budget, duration, audience, sustainability):
    creator_count = 8 if budget >= 400000 else 5
    cadence = "3-4 short-form assets/week" if duration <= 30 else "2-3 assets/week"
    target_roas = "4.0x+" if objective == "Sales" else "3.5x+"

    pillars = [
        "Problem → insight → proof",
        "Creator-led education",
        "Social proof and community participation",
        "Short-form content repurposing",
    ]
    if sustainability:
        pillars.append("Responsible production and measurable green actions")

    return {
        "positioning": f"{product} should be positioned around credible, human-led value for {audience}.",
        "creator_count": creator_count,
        "cadence": cadence,
        "target_roas": target_roas,
        "pillars": pillars,
        "measurement": "Track reach, qualified engagement, attributed conversions, ROAS, sentiment, creator fit and sustainability indicators.",
    }
