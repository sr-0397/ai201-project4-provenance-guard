import re
import math

def stylometric_score(text: str) -> dict:

    # --- Sentence length variance ---
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) < 2:
        variance_score = 0.5
    else:
        lengths = [len(s.split()) for s in sentences]
        mean = sum(lengths) / len(lengths)
        variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        # std_dev < 2 → uniform → AI-like (high score)
        # std_dev > 7 → variable → human-like (low score)
        variance_score = max(0.0, min(1.0, 1.0 - ((std_dev - 2.0) / 5.0)))

    # --- Average word length ---
    # AI favors longer, formal words. Human casual writing uses shorter words.
    # avg < 4.0 chars → casual human (low score)
    # avg > 6.5 chars → formal/AI-like (high score)
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    if len(words) < 5:
        word_len_score = 0.5
    else:
        avg_word_len = sum(len(w) for w in words) / len(words)
        word_len_score = max(0.0, min(1.0, (avg_word_len - 4.0) / 2.5))

    # --- Punctuation diversity ---
    # AI under-uses expressive punctuation like !, ?, --, ...
    # density > 0.05 → expressive → human-like (low score)
    # density < 0.01 → flat → AI-like (high score)
    expressive_punct = len(re.findall(r'[!?"\'\-–—…]', text))
    punct_density = expressive_punct / max(len(text), 1)
    punct_score = max(0.0, min(1.0, 1.0 - (punct_density / 0.05)))

    combined = (variance_score + word_len_score + punct_score) / 3.0

    return {
        "score": round(combined, 4),
        "metrics": {
            "sentence_variance_score": round(variance_score, 4),
            "word_length_score": round(word_len_score, 4),
            "punctuation_score": round(punct_score, 4),
        }
    }


if __name__ == "__main__":
    tests = [
        ("Clearly AI",       "Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous, it is equally essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment."),
        ("Clearly human",    "ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was fine but they put WAY too much sodium in it and i was thirsty for like three hours after. my friend got the spicy version and said it was better. probably won't go back unless someone drags me there"),
        ("Formal human",     "The relationship between monetary policy and asset price inflation has been extensively studied in the literature. Central banks face a fundamental tension between their mandate for price stability and the unintended consequences of prolonged low interest rates on equity and real estate valuations."),
        ("Lightly edited AI","I've been thinking a lot about remote work lately. There are genuine tradeoffs — flexibility and no commute on one side, isolation and blurred work-life boundaries on the other. Studies show productivity varies widely by individual and role type."),
    ]
    for label, text in tests:
        result = stylometric_score(text)
        print(f"\n[{label}]")
        print(f"  Combined score:  {result['score']}")
        print(f"  Variance score:  {result['metrics']['sentence_variance_score']}")
        print(f"  Word len score:  {result['metrics']['word_length_score']}")
        print(f"  Punct score:     {result['metrics']['punctuation_score']}")