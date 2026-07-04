from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db 
from app.db.scheme.babies import Baby_Create, Baby_Update, Baby_Read
from app.services.babies import BabyService
from app.core.auth import auth_get_u_id
import os
import uuid
router = APIRouter(prefix="/babies", tags=["Baby"])

UPLOAD_DIR = "uploads/baby_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. 아이 정보 등록
@router.post("/create", response_model=Baby_Read)
async def routers_babies_create(baby:Baby_Create, u_id: int = Depends(auth_get_u_id),db:AsyncSession=Depends(get_db)):
    db_data=await BabyService.service_babies_create(db,u_id , baby)
    return db_data

# 2. 아이 목록 조회
@router.get("/list", response_model=list[Baby_Read])
async def routers_babies_list(u_id:int = Depends(auth_get_u_id), db:AsyncSession=Depends(get_db)):
    db_data=await BabyService.service_babies_list(u_id, db)
    return db_data
    
# 3. 아이 세부 정보
@router.get("/{b_id}", response_model=Baby_Read)
async def routers_babies_read(b_id:int, db:AsyncSession=Depends(get_db)):
    db_data=await BabyService.service_babies_read(b_id, db)
    return db_data
    
# 4. 아이 정보 수정
@router.put("/edit")
async def routers_babies_update(b_id:int, baby:Baby_Update, db:AsyncSession=Depends(get_db)):
    db_data=await BabyService.service_babies_update(b_id, baby, db)
    return {"message":"수정되었습니다.", "data":db_data}
    
# 5. 아이 정보 삭제
@router.delete("/del", response_model=Baby_Read)
async def routers_babies_delete(b_id:int, db:AsyncSession=Depends(get_db)):
    db_data=await BabyService.service_babies_delete(b_id, db)
    return db_data

@router.post("/upload_image")
async def router_babies_upload_image(file: UploadFile = File(...)):
    # 파일명 중복 방지를 위해 uuid 사용
    ext = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    image_url = f"/{file_path}"  # 또는 실제 서빙 URL 형식에 맞게
    return {"image_url": image_url}