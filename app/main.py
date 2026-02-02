from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import EmotionRequest, EmotionResponse
from app.emotion_model import detect_emotion
from app.risk_engine import calculate_risk
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from app.schemas import EmotionHistoryResponse,TokenResponse,UserRegister,UserLogin
from app.database import get_db
from app.models import EmotionHistory,User
from app.auth import hash_password, verify_password, create_access_token
from fastapi import FastAPI, Depends, HTTPException

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

@app.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login", response_model=TokenResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token}

