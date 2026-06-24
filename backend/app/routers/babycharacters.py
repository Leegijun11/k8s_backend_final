from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db 
from app.db.scheme.babycharacters import BabyCharacter_Create, BabyCharacter_Update, BabyCharacter_Read
from app.services.babycharacters import BabyCharacterService

router = APIRouter(prefix="/babycharacters", tags=["BabyCharacter"])

# 1. 아이 성향 정보 등록
@router.post("/create", response_model=BabyCharacter_Read)
async def routers_babycharacters_create(baby:BabyCharacter_Create, db:AsyncSession=Depends(get_db)):
    db_data=await BabyCharacterService.service_babycharacter_create(baby, db)
    return db_data
    
# 2. 아이 세부 정보 조회
@router.get("/{c_id}", response_model=BabyCharacter_Read)
async def routers_babycharacters_read(c_id:int, db:AsyncSession=Depends(get_db)):
    db_data=await BabyCharacterService.service_babycharacter_read(c_id, db)
    return db_data

# 3. 아이 정보 수정
@router.put("/edit", response_model=BabyCharacter_Read)
async def routers_babycharacters_update(c_id:int, baby:BabyCharacter_Update, db:AsyncSession=Depends(get_db)):
    db_data=await BabyCharacterService.service_babycharacter_update(c_id, baby, db)
    return db_data