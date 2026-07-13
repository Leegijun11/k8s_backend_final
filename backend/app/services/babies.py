from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.babies import Baby_Create, Baby_Update
from app.db.scheme.care_groups import CareGroup_Create
from app.db.crud.babies import Baby_Crud
from app.db.crud.care_groups import CareGroup_Crud
from app.db.crud.records import Record_Crud
from app.db.scheme.records import Record_Create
from fastapi import HTTPException
from app.db.crud.parents import Parent_Crud
from app.db.scheme.parents import Parent_Create


class BabyService:

    # 1. 아이 정보 등록
    @staticmethod
    async def service_babies_create(db: AsyncSession, u_id: int, baby: Baby_Create):
        if baby.b_height <= 0 or baby.b_weight <= 0:
            raise HTTPException(status_code=400, detail="키와 몸무게는 0보다 커야 합니다.")

        try:
            existing_parent = await Parent_Crud.crud_parents_get_by_u_id(db, u_id)

            if existing_parent and existing_parent.g_id is not None:
                g_id = existing_parent.g_id
            else:
                new_group = CareGroup_Create(creator_id=u_id)
                care_group = await CareGroup_Crud.crud_caregroups_create(db, new_group)
                g_id = care_group.g_id

            baby_dict = baby.model_dump()
            baby_dict["g_id"] = g_id

            db_baby = await Baby_Crud.crud_babies_create(db, baby_dict)

            if existing_parent:
                existing_parent.current_b_id = db_baby.b_id
            else:
                member_data = Parent_Create(
                    p_role="parent",
                    p_category="guardian",
                    p_state="active",
                    g_id=g_id,
                    u_id=u_id,
                    current_b_id=db_baby.b_id,
                )
                await Parent_Crud.crud_parents_create(db, parent=member_data)

            await db.commit()
            await db.refresh(db_baby)

            return db_baby

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"{e} 아이 정보 등록에 실패했습니다."
            )

    # 2. 아이 목록 조회
    @staticmethod
    async def service_babies_list(db: AsyncSession, u_id: int):
        try:
            parent_data = await Parent_Crud.crud_parents_get_by_u_id(db, u_id)

            if (
                parent_data is None
                or parent_data.g_id is None
                or parent_data.p_state != "active"
            ):
                return []

            db_data = await Baby_Crud.crud_babies_list(db, u_id)
            return db_data

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"아이들의 정보를 불러오는 중 서버 오류가 발생했습니다 : {e}"
            )

    # 3. 아이 세부 정보
    @staticmethod
    async def service_babies_read(db: AsyncSession, b_id: int):
        try:
            db_data = await Baby_Crud.crud_babies_detail(db, b_id)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"아이의 세부 정보 로드 실패 : {e}"
            )

        if db_data is None:
            raise HTTPException(
                status_code=404,
                detail="해당 아이 정보를 찾을 수 없습니다."
            )

        return db_data

    # 4. 아이 정보 수정
    @staticmethod
    async def service_babies_update(
        db: AsyncSession,
        b_id: int,
        baby: Baby_Update
    ):
        if (
            (baby.b_height is not None and baby.b_height <= 0)
            or
            (baby.b_weight is not None and baby.b_weight <= 0)
        ):
            raise HTTPException(
                status_code=400,
                detail="키와 몸무게는 0보다 커야 합니다."
            )

        try:
            exist_baby = await Baby_Crud.crud_babies_detail(db, b_id)

            if exist_baby is None:
                raise HTTPException(
                    status_code=400,
                    detail="아이의 정보를 수정하는데 실패했습니다."
                )

            # 먼저 babies 업데이트
            db_data = await Baby_Crud.crud_babies_update(db, b_id, baby)

            if db_data is None:
                raise HTTPException(
                    status_code=400,
                    detail="아이의 정보를 수정하는데 실패했습니다."
                )

            # 수정 후 값으로 record 저장
            new_record = Record_Create(
                b_id=db_data.b_id,
                r_height=db_data.b_height,
                r_weight=db_data.b_weight
            )
            await Record_Crud.crud_records_create(db, new_record)

            await db.commit()
            await db.refresh(db_data)

            return db_data

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail="아이의 정보를 수정하는데 실패했습니다."
            )

    # 5. 아이 정보 삭제
    @staticmethod
    async def service_babies_delete(db: AsyncSession, b_id: int):
        try:
            exist_baby = await Baby_Crud.crud_babies_detail(db, b_id)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="아이 정보 확인 중 오류가 발생했습니다."
            )

        if exist_baby is None:
            raise HTTPException(
                status_code=404,
                detail="삭제할 아이의 정보가 존재하지 않습니다."
            )

        try:
            db_data = await Baby_Crud.crud_babies_del(db, b_id)
            await db.commit()
            return db_data

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="아이의 정보를 삭제하는데 실패했습니다."
            )