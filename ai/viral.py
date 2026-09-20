def viral_score(hook, format_name):
    score = 55
    actions = []
    if "?" in hook:
        score += 8
    if len(hook.split()) <= 12:
        score += 8
    if format_name in {"Reel", "YouTube Short"}:
        score += 8
    if any(x in hook.lower() for x in ["ai", "secret", "how", "why", "proof", "mistake"]):
        score += 8
    actions.extend([
        "Open with the tension or curiosity gap in the first 2 seconds.",
        "Use one clear proof point instead of multiple claims.",
        "End with a simple comment, save or share prompt.",
    ])
    return {"score": min(score, 100), "actions": actions}
