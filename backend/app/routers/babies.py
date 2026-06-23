from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db 
from app.db.scheme.babies import Baby_Create, Baby_Update, Baby_Read
from app.services.babies import BabyService
from fastapi import Body

router = APIRouter(prefix="/babies", tags=["Baby"])

# 1. 아이 정보 등록
@router.post("/create", response_model=Baby_Read)
async def routers_babies_create(baby:Baby_Create, db:AsyncSession=Depends(get_db)):
    try:
        db_data=await BabyService.service_babies_create(baby, db)
        return db_data
    except HTTPException as ee:
        raise ee
    except Exception as e:
        raise HTTPException(status_code=400, detail="아이 정보 등록에 실패했습니다.") 

# 2. 아이 목록 조회
@router.get("/list", response_model=list[Baby_Read])
async def routers_babies_list(u_id:int, db:AsyncSession=Depends(get_db)):
    try:
        db_data=await BabyService.service_babies_list(u_id, db)
        return db_data
    except HTTPException as ee:
        raise ee
    except Exception as e:
        raise HTTPException(status_code=400, detail="아이들의 정보를 불러오는데 실패했습니다.")
    
# 3. 아이 세부 정보
@router.get("/{b_id}", response_model=Baby_Read)
async def routers_babies_read(b_id:int, db:AsyncSession=Depends(get_db)):
    try:
        db_data=await BabyService.service_babies_read(b_id, db)
        return db_data
    except HTTPException as ee:
        raise ee
    except Exception as e:
        raise HTTPException(status_code=400, detail="아이의 정보를 불러오는데 실패했습니다.")
    
# 4. 아이 정보 수정
@router.put("/edit", response_model=Baby_Read)
async def routers_babies_update(b_id:int=Body(...), baby:Baby_Update=Body(...), db:AsyncSession=Depends(get_db)):
    try:
        db_data=await BabyService.service_babies_update(b_id, baby, db)
        return db_data
    except HTTPException as ee:
        raise ee
    except Exception as e:
        raise HTTPException(status_code=400, detail="아이의 정보를 수정하는데 실패했습니다.")
    
# 5. 아이 정보 삭제
@router.delete("/del", response_model=Baby_Read)
async def routers_babies_delete(b_id:int, db:AsyncSession=Depends(get_db)):
    try:
        db_data=await BabyService.service_babies_delete(b_id, db)
        return db_data
    except HTTPException as ee:
        raise ee
    except Exception as e:
        raise HTTPException(status_code=400, detail="아이의 정보를 삭제하는데 실패했습니다.")