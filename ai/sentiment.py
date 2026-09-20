POSITIVE = {"great", "love", "loved", "useful", "honest", "helpful", "good", "clear", "credible", "strong"}
NEGATIVE = {"bad", "hate", "hated", "fake", "poor", "confusing", "expensive", "worst", "disappointed"}

def analyze_sentiment(text):
    words = [w.strip(".,!?;:()[]{}").lower() for w in text.split()]
    pos = sum(w in POSITIVE for w in words)
    neg = sum(w in NEGATIVE for w in words)
    total = max(pos + neg, 1)
    positive = round(60 + 30 * pos / total - 10 * neg / total)
    negative = round(10 + 30 * neg / total)
    positive = max(0, min(100, positive))
    negative = max(0, min(100-positive, negative))
    neutral = 100 - positive - negative
    return {
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "summary": "The demo model indicates the dominant sentiment and surfaces themes for human review. This is a prototype heuristic, not a production NLP model.",
    }
