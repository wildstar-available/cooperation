from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ============ 用户相关 ============
class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True


# ============ 患者相关 ============
class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)
    gender: str = Field(pattern=r"^(男|女|其他)$")
    symptoms: str = Field(min_length=1, max_length=2000)
    medical_history: str = Field(default="", max_length=2000)


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
        orm_mode = True


# ============ AI 分析相关 ============
class AnalyzeRequest(BaseModel):
    patient_id: int
    symptoms: str
    medical_history: str = ""


class AnalyzeResponse(BaseModel):
    diagnosis: str
    treatment: str
