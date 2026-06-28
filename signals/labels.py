def get_label(confidence: float) -> str:
    """
    Maps a confidence score to the transparency label shown to users.

    >= 0.65  → high-confidence AI
    0.40–0.64 → uncertain
    < 0.40   → high-confidence human
    """
    if confidence >= 0.65:
        return (
            "This content was likely generated with AI assistance. "
            "Our analysis detected patterns consistent with AI-generated text. "
            "If this is your original work, you can file an appeal below."
        )
    elif confidence >= 0.40:
        return (
            "Our system was unable to determine with confidence whether this content "
            "is human- or AI-written. It has been published without an attribution label. "
            "If you believe this classification is wrong, you can file an appeal."
        )
    else:
        return (
            "This content appears to be human-written. "
            "No AI-generation indicators were detected."
        )


if __name__ == "__main__":
    tests = [0.82, 0.55, 0.21]
    for score in tests:
        print(f"\nScore {score}:")
        print(f"  {get_label(score)}")