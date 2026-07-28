from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter(prefix="/health", tags=["Health Check"])

# 1. 단순 서버 가동 상태 체크 (AWS ALB/Target Group용으로 유용)
@router.get("")
def health_check():
    return {"status": "ok", "message": "Server is running"}

# 2. RDS 데이터베이스 연결 상태까지 체크
@router.get("/db")
def db_health_check(db: Session = Depends(get_db)):
    try:
        # DB에 간단한 쿼리를 보내 연결이 살아있는지 확인
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        # 연결 실패 시 500 에러 반환 -> AWS가 비정상(Unhealthy)으로 감지 가능
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )
    
    