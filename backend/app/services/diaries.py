#service_diaries_create : 일기 생성

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.diaries import Diary_Create, Diary_Update
from app.db.crud.diaries import Diary_Crud
from app.ai.llm_run import ai_llm_run
from datetime import date

class Diary_Service:

    # 일기 생성
    @staticmethod
    async def service_diaries_create(db: AsyncSession, diary: Diary_Create, ai_create: bool):
        try:
            if ai_create:
                log = await Diary_Crud.crud_diaries_get_log(db, diary.b_id, diary.d_date)

                if not log:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="해당 날짜의 로그 정보가 없습니다"
                    )
                
                images = await Diary_Crud.crud_diaries_get_images(db, diary.b_id, diary.d_date)

                if not images:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="해당 날짜의 이미지 정보가 없습니다"
                    )
                
                
                llm_result = await ai_llm_run(log.l_content)
                
                d_word = llm_result.get("d_word", "")
                target_words = [w.strip().lower() for w in d_word.split(",") if w.strip()]

                d_image = None
                for image in images:
                    label = image.i_label.lower() if image.i_label else ""
                    
                    if any(word in label for word in target_words):
                        d_image = image.i_image
                        break
                
                if not d_image and images:
                    d_image = images[0].i_image

                diary_data = {
                    "d_title": f"{diary.d_date} ai 일기",
                    "d_content": llm_result.get("d_content"),
                    "d_label": llm_result.get("d_label"),
                    "d_date": diary.d_date,
                    "d_image": d_image,  
                    "d_eat": llm_result.get("d_eat"),
                    "d_sleep": llm_result.get("d_sleep"),
                    "d_toilet": llm_result.get("d_toilet"),
                    "d_temp": llm_result.get("d_temp"),
                    "b_id": diary.b_id,
                }

                new_diary = await Diary_Crud.crud_diaries_create(db, diary_data)
            
            else:
                user_diary_data = diary.model_dump() 
                new_diary = await Diary_Crud.crud_diaries_create(db, user_diary_data)

            await db.commit()
            await db.refresh(new_diary)

            return new_diary

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"일기 생성 실패: {e}"
            )
        
    # 날짜별 일기 목록
    @staticmethod
    async def service_diaries_list(db: AsyncSession, b_id: int, d_date: date):
        try:
            diaries = await Diary_Crud.crud_diaries_list(db, b_id, d_date)

            if not diaries:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="일기를 불러오는데 실패했습니다"
                )

            return diaries

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"일기를 불러오는데 실패했습니다: {e}"
            )
        

    # 일기 상세
    @staticmethod
    async def service_diaries_detail(db: AsyncSession, d_id: int):
        try:
            diary = await Diary_Crud.crud_diaries_detail(db, d_id)

            if not diary:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="일기를 불러오는데 실패했습니다"
                )

            return diary

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"일기를 불러오는데 실패했습니다: {e}"
            )
    
    # 일기 수정
    @staticmethod
    async def service_diaries_update(db: AsyncSession, d_id: int, update_diary: Diary_Update):
        try:
            update_data = update_diary.model_dump(exclude_unset=True)

            updated_diary = await Diary_Crud.crud_diaries_update(db, d_id, update_data)

            if not updated_diary:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="일기 수정에 실패했습니다"
                )

            await db.commit()
            await db.refresh(updated_diary)

            return updated_diary

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"일기 수정에 실패했습니다: {e}"
            )
        
    # 일기 삭제
    @staticmethod
    async def service_diaries_delete(db: AsyncSession, d_id: int):
        try:
            deleted_diary = await Diary_Crud.crud_diaries_del(db, d_id)

            if not deleted_diary:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="일기 삭제에 실패했습니다"
                )

            d_date = deleted_diary.d_date

            await db.commit()

            return {"msg": f"{d_date} 일기를 삭제하였습니다."}

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"일기 삭제에 실패했습니다: {e}"
            )