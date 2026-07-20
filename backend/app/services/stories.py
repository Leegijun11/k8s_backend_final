#service_stories_create : 디지털북 생성
#service_stories_list : b_id별 디지털북 목록
#service_stories_detail : 디지털북 상세
#service_stories_delete : 디지털북 삭제

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.scheme.stories import Story_Create, Story_Update
from app.db.crud.stories import Story_Crud
from app.db.crud.story_pages import Story_Page_Crud
from app.db.crud.milestones import Milestone_Crud

from app.ai.llm_story import ai_llm_story_run

from datetime import date
import copy


class Story_Service:

    # 디지털북 생성
    @staticmethod
    async def service_stories_create(db: AsyncSession, story: Story_Create, d_ids:list):
        try:
            diaries = await Story_Crud.crud_stories_get_diaries(db, story.b_id, story.start_date, story.end_date)

            if not diaries:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="해당 기간의 일기 정보가 없습니다"
                )
            
            milestones = await Milestone_Crud.crud_milestones_bm_date_list(db, story.b_id, story.start_date, story.end_date)

            if not milestones:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="해당 기간의 마일스톤 정보가 없습니다"
                )

            selected_milestones = []
            for m in milestones:
                if m.m_achieved is True:
                    selected_milestones.append(m)
                elif m.m_achieved is False and m.d_id in d_ids:
                    selected_milestones.append(m)
            
            print(d_ids)
            total_count = len(selected_milestones)
            if total_count < 8 or total_count > 16:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"동화책을 만들기 위한 일기 개수가 맞지 않습니다. (현재: {total_count}개)")
            
            selected_milestones = sorted(selected_milestones, key=lambda m: m.m_achieved_date)

            selected_diaries = []
            for milestone in selected_milestones:
                matched_diary = next((d for d in diaries if d.d_id == milestone.d_id), None)
                print(matched_diary.d_id)
                if matched_diary:
                    
                    cloned_diary = copy.copy(matched_diary)
                    cloned_diary.status = "True" if milestone.m_achieved else "False"
                    cloned_diary.app_milestone = milestone.milestone.app_milestone if milestone.milestone else ""
                    selected_diaries.append(cloned_diary)


            input_list = []
            for index, diary in enumerate(selected_diaries, start=1):
                input_list.append({
                    "page_num": index,
                    "status": diary.status,
                    "milestone_name": diary.app_milestone,
                    "diary": diary.d_content
                })

            llm, story_title = await ai_llm_story_run(input_list)
            print(f"AI가 생성한 스토리 개수({len(llm)}개)와 선택한 일기 개수({len(selected_diaries)}개)")
            if len(selected_diaries) != len(llm):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"AI가 생성한 스토리 개수({len(llm)}개)와 선택한 일기 개수({len(selected_diaries)}개)가 일치하지 않습니다. 다시 시도해 주세요."
                )

            story_db_data = story.model_dump(exclude={"start_date", "end_date"}) | {"s_name": story_title}

            new_story = await Story_Crud.crud_stories_create(db, story_db_data)

            pages_data = []
            for i, diary in enumerate(selected_diaries):
                pages_data.append({
                    "s_id": new_story.s_id,
                    "sp_num": i+1,
                    "sp_image": diary.d_image if diary.d_image else "",
                    "sp_content": llm[i]
                })
                    
            await Story_Page_Crud.crud_story_pages_multi_create(db, pages_data)

            await db.commit()
            await db.refresh(new_story)

            return new_story

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"디지털북 생성 실패: {e}")


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


    # 디지털북 사용 일기 선택 목록
    @staticmethod
    async def service_stories_diaries_select(db: AsyncSession, b_id: int, start_date: date, end_date: date):
        try:
            data = await Milestone_Crud.crud_milestones_bm_false_list(db, b_id, start_date, end_date)
            if not data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="해당 일기들을 찾을 수 없습니다"
                )
            return data
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"일기들을 불러오는데 실패했습니다: {e}"
            )