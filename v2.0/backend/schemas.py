from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ============ 用户相关 ============
class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 患者相关 ============
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    symptoms: str
    medical_history: str = ""


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    symptoms: Optional[str] = None
    medical_history: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    symptoms: str
    medical_history: str
    diagnosis: str
    treatment: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ AI 分析相关 ============
class AnalyzeRequest(BaseModel):
    patient_id: int
    symptoms: str
    medical_history: str = ""


class AnalyzeResponse(BaseModel):
    diagnosis: str
    treatment: str
