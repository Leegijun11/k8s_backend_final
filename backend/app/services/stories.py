#service_stories_create : 디지털북 생성
#service_stories_list : b_id별 디지털북 목록
#service_stories_detail : 디지털북 상세
#service_stories_delete : 디지털북 삭제

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.scheme.stories import Story_Create, Story_Update
from app.db.crud.stories import Story_Crud

from app.db.crud.story_pages import Story_Page_Crud

from app.ai.llm_story import ai_llm_story_run


class Story_Service:

    # 디지털북 생성
    @staticmethod
    async def service_stories_create(db: AsyncSession, story: Story_Create):
        try:
            diaries = await Story_Crud.crud_stories_get_diaries(db, story.b_id, story.start_date, story.end_date)

            if not diaries:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="해당 기간의 일기 정보가 없습니다"
                )
            
            if not story.s_name:
                title=f'{story.start_date}~{story.end_date} 제작 동화책'
            else:
                title=story.s_name

            story_data = {
                "s_name": title,
                "b_id": story.b_id,
            }

            new_story = await Story_Crud.crud_stories_create(db, story_data)

            pages_data = []

            for i, diary in enumerate(diaries):
                llm = await ai_llm_story_run(diary.d_content)
                
                pages_data.append({"s_id": new_story.s_id,
                                   "sp_num": i+1,
                                   "sp_image": diary.d_image,
                                   "sp_content": llm["sp_content"]})
                    
            await Story_Page_Crud.crud_story_pages_multi_create(db, pages_data)

            await db.commit()
            await db.refresh(new_story)

            return new_story

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"디지털북 생성 실패: {e}"
            )

    # b_id별 디지털북 목록
    @staticmethod
    async def service_stories_list(db: AsyncSession, b_id: int):
        try:
            stories = await Story_Crud.crud_stories_list(db, b_id)

            if not stories:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="책 목록을 불러오는데 실패했습니다"
                )

            return stories

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"책 목록을 불러오는데 실패했습니다: {e}"
            )

    # 디지털북 상세
    @staticmethod
    async def service_stories_detail(db: AsyncSession, s_id: int):
        try:
            story = await Story_Crud.crud_stories_detail(db, s_id)

            if not story:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="책을 불러오는데 실패했습니다"
                )

            return story

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"책을 불러오는데 실패했습니다: {e}"
            )

    # 디지털북 수정
    @staticmethod
    async def services_stories_update(db:AsyncSession,
                                      s_id:int,
                                      data:Story_Update):
        try:
            db_data = await Story_Crud.crud_stories_update(db, s_id, data)

            if not db_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="책 수정에 실패했습니다.")
            
            await db.commit()
            await db.refresh(db_data)

            return db_data

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"디지털북 수정 실패: {e}"
            )


    # 디지털북 삭제
    @staticmethod
    async def service_stories_delete(db: AsyncSession, s_id: int):
        try:
            deleted_story = await Story_Crud.crud_stories_del(db, s_id)

            if not deleted_story:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="책 삭제에 실패했습니다"
                )

            await db.commit()

            return {"msg": "책을 삭제하였습니다."}

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"책 삭제에 실패했습니다: {e}"
            )
        


    # 디지털북 페이지 목록
    @staticmethod
    async def service_stories_pages_list(db : AsyncSession, s_id : int):
        try:
            data = await Story_Page_Crud.crud_story_pages_list(db, s_id)

            if not data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="페이지 목록들을 찾을 수 없습니다")

            return data

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"페이지 목록들을 불러오는데 실패했습니다: {e}")


    # 디지털북 페이지 상세
    @staticmethod
    async def service_stories_pages_detail(db : AsyncSession, sp_id : int):
        try:
            data = await Story_Page_Crud.crud_story_pages_detail(db, sp_id)

            if not data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="해당 상세페이지를 찾을 수 없습니다")

            return data

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"해당 상세페이지를 불러오는데 실패했습니다: {e}")
        

    # 디지털북 페이지 삭제
    @staticmethod
    async def service_stories_pages_del(db : AsyncSession, sp_id : int):
        try:
            data = await Story_Page_Crud.crud_story_pages_del(db, sp_id)

            if not data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="해당 페이지 찾을 수 없습니다")

            await db.commit()

            return {"msg": "책을 삭제하였습니다."}

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"책 삭제에 실패했습니다: {e}"
            )