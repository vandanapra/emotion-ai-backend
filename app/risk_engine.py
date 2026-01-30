def calculate_risk(emotion: str, confidence: float) -> str:
    """
    Returns: low | medium | high
    """

    # Base risk mapping
    medium_risk_emotions = {"sadness", "fear", "anger", "disgust"}

    if emotion in medium_risk_emotions:
        if confidence >= 0.85:
            return "high"
        return "medium"

    return "low"
