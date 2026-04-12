from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import hashlib

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    phone: str

class LoginRequest(BaseModel):
    phone: str
    code: str

SECRET_KEY = "avatar-ai-secret-key-change-in-production"
ALGORITHM = "HS256"

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register(data: RegisterRequest):
    user_id = hashlib.md5(data.phone.encode()).hexdigest()[:12]
    token = create_token(user_id)
    return {"token": token, "user_id": user_id}

@router.post("/login")
async def login(data: LoginRequest):
    user_id = hashlib.md5(data.phone.encode()).hexdigest()[:12]
    token = create_token(user_id)
    return {"token": token, "user_id": user_id}
