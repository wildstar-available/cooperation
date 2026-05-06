from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import models
import schemas
from database import engine, get_db, Base
from auth import (
    verify_password, get_password_hash, create_access_token, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ai_client import analyze_medical

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI 医疗诊断助手")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# ============ 首页 ============
@app.get("/")
async def root():
    return FileResponse("frontend/index.html")


# ============ 认证接口 ============
@app.post("/api/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 检查用户是否存在
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# ============ 患者管理接口 ============
@app.get("/api/patients", response_model=list[schemas.PatientResponse])
async def get_patients(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patients = db.query(models.Patient).filter(
        models.Patient.owner_id == current_user.id
    ).all()
    return patients


@app.post("/api/patients", response_model=schemas.PatientResponse)
async def create_patient(
    patient: schemas.PatientCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_patient = models.Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        symptoms=patient.symptoms,
        medical_history=patient.medical_history,
        owner_id=current_user.id
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.get("/api/patients/{patient_id}", response_model=schemas.PatientResponse)
async def get_patient(
    patient_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.owner_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    return patient


@app.put("/api/patients/{patient_id}", response_model=schemas.PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: schemas.PatientUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.owner_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")

    update_data = patient_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient


@app.delete("/api/patients/{patient_id}")
async def delete_patient(
    patient_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.owner_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")

    db.delete(patient)
    db.commit()
    return {"message": "删除成功"}


# ============ AI 分析接口 ============
@app.post("/api/analyze", response_model=schemas.AnalyzeResponse)
async def analyze(
    request: schemas.AnalyzeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 验证患者是否属于当前用户
    patient = db.query(models.Patient).filter(
        models.Patient.id == request.patient_id,
        models.Patient.owner_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")

    # 调用 AI 分析
    result = await analyze_medical(request.symptoms, request.medical_history)

    # 更新患者记录
    patient.diagnosis = result["diagnosis"]
    patient.treatment = result["treatment"]
    db.commit()
    db.refresh(patient)

    return schemas.AnalyzeResponse(
        diagnosis=result["diagnosis"],
        treatment=result["treatment"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
