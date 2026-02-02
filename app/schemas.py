from pydantic import BaseModel
from datetime import datetime

class EmotionRequest(BaseModel):
    text: str

class EmotionResponse(BaseModel):
    emotion: str
    confidence: float
    risk_level: str
    
class EmotionHistoryResponse(BaseModel):
    text: str
    emotion: str
    confidence: float
    risk_level: str
    created_at: datetime

    class Config:
        orm_mode = True
