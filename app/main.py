from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import EmotionRequest, EmotionResponse
from app.emotion_model import detect_emotion
from app.risk_engine import calculate_risk
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from app.schemas import EmotionHistoryResponse
from app.database import get_db
from app.models import EmotionHistory

app = FastAPI()


# ✅ CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (OK for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/detect-emotion", response_model=EmotionResponse)
def detect_emotion_api(
    request: EmotionRequest,
    db: Session = Depends(get_db)
):
    emotion_data = detect_emotion(request.text)

    risk = calculate_risk(
        emotion=emotion_data["emotion"],
        confidence=emotion_data["confidence"]
    )

    record = EmotionHistory(
        text=request.text,
        emotion=emotion_data["emotion"],
        confidence=emotion_data["confidence"],
        risk_level=risk
    )

    db.add(record)
    db.commit()

    return {
        "emotion": emotion_data["emotion"],
        "confidence": emotion_data["confidence"],
        "risk_level": risk
    }
    
@app.get("/emotion-history", response_model=List[EmotionHistoryResponse])
def get_emotion_history(db: Session = Depends(get_db)):
    records = (
        db.query(EmotionHistory)
        .order_by(EmotionHistory.created_at.desc())
        .limit(20)
        .all()
    )
    return records

