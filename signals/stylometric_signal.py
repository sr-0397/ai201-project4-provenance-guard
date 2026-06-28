import re
import math

def stylometric_score(text: str) -> dict:
    """
    Returns {"score": float, "metrics": dict}
    score: 0.0 (human-like) to 1.0 (AI-like)

    Three metrics:
    1. Sentence length variance  — AI text is more uniform (low variance = high AI score)
    2. Type-token ratio (TTR)    — AI repeats words more (low TTR = high AI score)
    3. Punctuation diversity     — AI under-uses dashes, ellipses, exclamations (low diversity = high AI score)
    """

    # --- Sentence length variance ---
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) < 2:
        variance_score = 0.5  # not enough data
    else:
        lengths = [len(s.split()) for s in sentences]
        mean = sum(lengths) / len(lengths)
        variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        # High std_dev = human (variable). Low = AI (uniform).
        # Normalize: std_dev of ~8+ words = clearly human, ~2 or less = AI-like
        variance_score = max(0.0, min(1.0, 1.0 - (std_dev / 8.0)))

    # --- Type-token ratio (TTR) ---
    words = re.findall(r'\b[a-z]+\b', text.lower())
    if len(words) < 10:
        ttr_score = 0.5
    else:
        ttr = len(set(words)) / len(words)
        # High TTR = human (diverse vocab). Low TTR = AI (repetitive).
        # Normalize: TTR of 0.8+ = human, 0.4 or less = AI-like
        ttr_score = max(0.0, min(1.0, 1.0 - ((ttr - 0.4) / 0.4)))

    # --- Punctuation diversity ---
    expressive_punct = len(re.findall(r'[!?"\'\-–—…]', text))
    char_count = max(len(text), 1)
    punct_density = expressive_punct / char_count
    # High density = human. Low = AI.
    # Normalize: density of 0.04+ = human, near 0 = AI-like
    punct_score = max(0.0, min(1.0, 1.0 - (punct_density / 0.04)))

    # Combine three metrics equally
    combined = (variance_score + ttr_score + punct_score) / 3.0

    return {
        "score": round(combined, 4),
        "metrics": {
            "sentence_variance_score": round(variance_score, 4),
            "ttr_score": round(ttr_score, 4),
            "punctuation_score": round(punct_score, 4),
        }
    }


# Quick test — run: python signals/stylometric_signal.py
if __name__ == "__main__":
    tests = [
        ("Clearly AI", "Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous, it is equally essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment."),
        ("Clearly human", "ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was fine but they put WAY too much sodium in it and i was thirsty for like three hours after. my friend got the spicy version and said it was better. probably won't go back unless someone drags me there"),
        ("Formal human", "The relationship between monetary policy and asset price inflation has been extensively studied in the literature. Central banks face a fundamental tension between their mandate for price stability and the unintended consequences of prolonged low interest rates on equity and real estate valuations."),
        ("Lightly edited AI", "I've been thinking a lot about remote work lately. There are genuine tradeoffs — flexibility and no commute on one side, isolation and blurred work-life boundaries on the other. Studies show productivity varies widely by individual and role type."),
    ]
    for label, text in tests:
        result = stylometric_score(text)
        print(f"\n[{label}]")
        print(f"  Combined score: {result['score']}")
        print(f"  Variance score: {result['metrics']['sentence_variance_score']}")
        print(f"  TTR score:      {result['metrics']['ttr_score']}")
        print(f"  Punct score:    {result['metrics']['punctuation_score']}")