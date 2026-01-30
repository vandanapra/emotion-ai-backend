from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base"
)

def detect_emotion(text: str):
    result = emotion_classifier(text)

    # HuggingFace ALWAYS returns list of dicts here
    emotion_data = result[0]

    return {
        "emotion": emotion_data["label"],
        "confidence": round(float(emotion_data["score"]), 2)
    }
