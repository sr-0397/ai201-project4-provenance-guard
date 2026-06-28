def combine_scores(llm_score: float, stylo_score: float) -> dict:
    """
    Combines LLM and stylometric scores into a calibrated confidence score.

    Weights: 60% LLM, 40% stylometric (LLM gets higher weight — captures
    semantic patterns that heuristics miss).

    Thresholds (asymmetric — biased against false positives):
      >= 0.65  → likely_ai
      0.40–0.64 → uncertain
      < 0.40   → likely_human
    """
    LLM_WEIGHT = 0.60
    STYLO_WEIGHT = 0.40

    confidence = round((LLM_WEIGHT * llm_score) + (STYLO_WEIGHT * stylo_score), 4)

    if confidence >= 0.65:
        attribution = "likely_ai"
    elif confidence >= 0.40:
        attribution = "uncertain"
    else:
        attribution = "likely_human"

    return {
        "confidence": confidence,
        "attribution": attribution,
    }


if __name__ == "__main__":
    cases = [
        ("Clearly AI",        0.91, 0.82),
        ("Clearly human",     0.12, 0.18),
        ("Formal human",      0.55, 0.71),
        ("Lightly edited AI", 0.48, 0.39),
    ]
    print(f"{'Case':<22} {'LLM':>6} {'Stylo':>6} {'Combined':>10} {'Attribution'}")
    print("-" * 60)
    for label, llm, stylo in cases:
        result = combine_scores(llm, stylo)
        print(f"{label:<22} {llm:>6.2f} {stylo:>6.2f} {result['confidence']:>10.4f}  {result['attribution']}")