def green_score(logistics, digital, creator, accessibility):
    score = round(0.30*logistics + 0.25*digital + 0.25*creator + 0.20*accessibility)
    return {
        "score": score,
        "explanation": "Weighted demo index: logistics 30%, digital-first execution 25%, creator sustainability fit 25%, accessibility/inclusion 20%.",
    }
