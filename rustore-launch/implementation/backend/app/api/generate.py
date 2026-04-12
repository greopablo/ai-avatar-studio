from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/generate", tags=["generate"])

class GenerateRequest(BaseModel):
    style_id: str
    user_id: str

@router.post("/avatar")
async def create_avatar(data: GenerateRequest):
    job_id = str(uuid.uuid4())[:8]
    return {
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    return {
        "job_id": job_id,
        "status": "completed",
        "urls": [f"https://cdn.example.com/{job_id}/avatar.png"]
    }
