from fastapi import FastAPI
from app.schemas import EmotionRequest, EmotionResponse
from app.emotion_model import detect_emotion
from app.risk_engine import calculate_risk

app = FastAPI()

@app.post("/detect-emotion", response_model=EmotionResponse)
def detect_emotion_api(request: EmotionRequest):
    emotion_data = detect_emotion(request.text)

    risk = calculate_risk(
        emotion=emotion_data["emotion"],
        confidence=emotion_data["confidence"]
    )

    return {
        "emotion": emotion_data["emotion"],
        "confidence": emotion_data["confidence"],
        "risk_level": risk
    }
