from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.babies import Baby
from app.db.models.parents import Parent


async def get_baby_or_none(db: AsyncSession, b_id: int) -> Baby | None:
    """b_id로 Baby 레코드를 조회한다. 없으면 None."""
    return await db.get(Baby, b_id)


async def is_user_in_baby_care_group(db: AsyncSession, u_id: int, g_id: int) -> bool:
    """u_id가 g_id(케어그룹)의 멤버(Parent)인지 확인한다."""
    stmt = select(Parent.p_id).where(
        Parent.u_id == u_id,
        Parent.g_id == g_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def get_authorized_baby(db: AsyncSession, u_id: int, b_id: int) -> Baby:
    """
    u_id가 b_id 아이의 케어그룹 멤버인지 확인하고, 맞으면 Baby를 반환한다.
    아니면 baby가 없거나(404) 권한이 없는 것(403)이므로 None 대신 예외를 던지도록
    상위 서비스 레이어에서 처리한다. 여기서는 순수 조회/확인만 담당한다.
    """
    baby = await get_baby_or_none(db, b_id)
    if baby is None:
        return None

    allowed = await is_user_in_baby_care_group(db, u_id, baby.g_id)
    if not allowed:
        return None

    return baby


async def shares_care_group(db: AsyncSession, u_id: int, target_u_id: int) -> bool:
    """
    u_id와 target_u_id가 하나 이상의 케어그룹을 함께 쓰는(=공동 양육자 관계인)
    사이인지 확인한다. 프로필 사진처럼 "본인 것"이 아니라 "같은 그룹 멤버 것"을
    조회할 때 쓰는 인가 체크.
    """
    if u_id == target_u_id:
        return True

    my_group_ids = select(Parent.g_id).where(Parent.u_id == u_id)
    stmt = select(Parent.p_id).where(
        Parent.u_id == target_u_id,
        Parent.g_id.in_(my_group_ids),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None