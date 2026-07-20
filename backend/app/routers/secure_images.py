from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.auth import auth_get_u_id
from app.services.secure_images import SecureImage_Service

router = APIRouter(prefix="/secure-images", tags=["SecureImages"])


# 성장 일기 사진 (기존 /images/{b_id}/{date}/{filename} 정적 경로 대체)
@router.get("/growth/{i_id}")
async def router_secure_growth_photo(
    i_id: int,
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db),
):
    return await SecureImage_Service.get_growth_photo(db, u_id, i_id)


# 아이 프로필 사진 (기존 /uploads/baby_images/{filename} 정적 경로 대체)
@router.get("/baby/{b_id}/profile")
async def router_secure_baby_profile_photo(
    b_id: int,
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db),
):
    return await SecureImage_Service.get_baby_profile_photo(db, u_id, b_id)


# 로그인한 본인의 프로필 사진 (기존 /uploads/user_images/{filename} 정적 경로 대체)
# b_id/u_id를 파라미터로 받지 않고 항상 "나 자신"의 사진만 반환한다.
@router.get("/user/profile")
async def router_secure_my_profile_photo(
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db),
):
    return await SecureImage_Service.get_my_profile_photo(db, u_id)


# 공동 양육자(같은 케어그룹 멤버)의 프로필 사진
@router.get("/user/{target_u_id}/profile")
async def router_secure_partner_profile_photo(
    target_u_id: int,
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db),
):
    return await SecureImage_Service.get_partner_profile_photo(db, u_id, target_u_id)


# 경로 문자열 자체가 저장된 경우 (예: Diary.d_image)
# 예: /secure-images/by-path?path=images/10/20260720/uuid.png
@router.get("/by-path")
async def router_secure_image_by_path(
    path: str,
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db),
):
    return await SecureImage_Service.get_image_by_path(db, u_id, path)