from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.diaries import Diary_Create, Diary_Update
from app.db.scheme.babymilestones import BabyMilestone_Create, BabyMilestone_Update
from app.db.crud.diaries import Diary_Crud
from app.db.crud.babies import Baby_Crud
from app.db.crud.milestones import Milestone_Crud
from app.ai.llm_run import ai_llm_run
from datetime import date, datetime, timezone

class Diary_Service:

    # 일기 생성
    @staticmethod
    async def service_diaries_create(db: AsyncSession, diary: Diary_Create, ai_create: bool, u_id: int):
        try:
            # ★ 추가: 이 b_id가 로그인한 u_id의 그룹 아기인지 확인
            has_access = await Diary_Crud.crud_check_diary_access(db, diary.b_id, u_id)
            if not has_access:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="일기를 작성할 권한이 없습니다")

            if ai_create:
                raw_text = diary.original_text

                if not raw_text:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="일기를 생성할 원문 텍스트가 없습니다."
                    )
                
                images = await Diary_Crud.crud_diaries_get_images(db, diary.b_id, diary.d_date)
                             
                baby_date = await Baby_Crud.crud_babies_detail(db, diary.b_id)
                b_date = baby_date.b_birth

                if isinstance(b_date, datetime):
                    b_date = b_date.date()
                elif isinstance(b_date, str):
                    b_date = datetime.strptime(b_date, "%Y-%m-%d %H:%M:%S").date()

                days=(date.today()-b_date).days
                age=int(days/30.43)
                age=max(0,age)
                
                # log.l_content 대신 raw_text를 AI로 넘겨줍니다.
                llm_result = await ai_llm_run(raw_text, age)
                d_i_label = llm_result.get("d_i_label", "")

                clean_labels = [lbl.strip() for lbl in d_i_label.split(",")]
                print(f"[clean_labels]: {clean_labels}")
                d_image = diary.d_image 

                if not d_image and images:
                    for image in images:
                        label = (image.i_label or "").strip()
                        print(f"[image label]: '{label}' / in clean_labels: {label in clean_labels}")
                        if label in clean_labels:
                            d_image = image.i_image
                            print(f"[매칭 성공]: {d_image}")
                            break

                # images/ -> uploads/ 기준으로 경로 자르기
                if d_image:
                    d_image = d_image.replace("\\", "/")
                    if "uploads/" in d_image:
                        d_image = "uploads/" + d_image.split("uploads/", 1)[1]

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


                m_content = llm_result.get("d_mile")
                print(m_content)
                m_names = [m["item"].strip() for m in m_content if isinstance(m, dict) and m.get("item")] if isinstance(m_content, list) else []
                    
                for m_name in m_names:
                    current_status = False

                    if isinstance(m_content, list):
                        for ms_obj in m_content:
                            if isinstance(ms_obj, dict) and ms_obj.get("item", "").strip() == m_name:
                                current_status = bool(ms_obj.get("status", False))
                                break
                            
                    print(m_name, age)
                    m_find = await Milestone_Crud.crud_milestones_find(db, m_name, age+2)
                    
                    if m_find is not None:
                        print(m_find)
                        bm_find = await Milestone_Crud.crud_milestones_babymilestone_find(db, m_find, diary.b_id)
                        
                        bm_data = {
                                    "b_id": diary.b_id,
                                    "d_id": new_diary.d_id,
                                    "m_id": m_find,
                                    "m_achieved": current_status,
                                    "m_achieved_date": new_diary.d_date
                                }

                        if bm_find is None:
                            await Milestone_Crud.crud_milestones_babymilestone_create(db, BabyMilestone_Create(**bm_data))

                        else:
                            if bm_find.m_achieved is False:
                                await Milestone_Crud.crud_milestones_babymilestone_create(db, BabyMilestone_Create(**bm_data))
                            
                            elif bm_find.m_achieved is True:
                                pass

            else:
                user_diary_data = diary.model_dump()
                user_diary_data.pop("original_text", None) 
                
                if user_diary_data.get("d_image"):
                    img_path = user_diary_data["d_image"].replace("\\", "/")
                    if "uploads/" in img_path:
                        user_diary_data["d_image"] = "uploads/" + img_path.split("uploads/", 1)[1]
                        
                new_diary = await Diary_Crud.crud_diaries_create(db, user_diary_data)

            await db.commit()
            await db.refresh(new_diary)
            return new_diary

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"일기 생성 실패: {e}")


    # 날짜별 일기 목록 (이미 완료됨, 그대로 유지)
    @staticmethod
    async def service_diaries_list(db: AsyncSession, b_id: int, d_date: date, u_id: int):
        try:
            has_access = await Diary_Crud.crud_check_diary_access(db, b_id, u_id)
            if not has_access:
                raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
            diaries = await Diary_Crud.crud_diaries_list(db, b_id, d_date)
            return diaries
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"일기 목록을 불러오는데 실패했습니다: {e}")


    # 일기 상세 (이미 완료됨, 그대로 유지)
    @staticmethod
    async def service_diaries_detail(db: AsyncSession, d_id: int, u_id: int):
        try:
            diary = await Diary_Crud.crud_diaries_detail(db, d_id)
            if not diary:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기를 불러오는데 실패했습니다")
            has_access = await Diary_Crud.crud_check_diary_access(db, diary.b_id, u_id)
            if not has_access:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="일기를 볼 권한이 없습니다")
            return diary
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"일기를 불러오는데 실패했습니다: {e}")


    # 일기 수정
    @staticmethod
    async def service_diaries_update(db: AsyncSession, d_id: int, update_diary: Diary_Update, u_id: int):
        try:
            diary = await Diary_Crud.crud_diaries_detail(db, d_id)
            if not diary:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다")

            has_access = await Diary_Crud.crud_check_diary_access(db, diary.b_id, u_id)
            if not has_access:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다")

            update_data = update_diary.model_dump(exclude_unset=True)

            if update_data.get("d_image"):
                img_path = update_data["d_image"].replace("\\", "/")
                if "uploads/" in img_path:
                    update_data["d_image"] = "uploads/" + img_path.split("uploads/", 1)[1]

            updated_diary = await Diary_Crud.crud_diaries_update(db, d_id, update_data)

            if not updated_diary:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기 수정에 실패했습니다")

            await db.commit()
            await db.refresh(updated_diary)
            return updated_diary

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"일기 수정에 실패했습니다: {e}")


    # 일기 삭제
    @staticmethod
    async def service_diaries_delete(db: AsyncSession, d_id: int, u_id: int):
        try:
            diary = await Diary_Crud.crud_diaries_detail(db, d_id)
            if not diary:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다")

            has_access = await Diary_Crud.crud_check_diary_access(db, diary.b_id, u_id)
            if not has_access:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="삭제 권한이 없습니다")

            deleted_diary = await Diary_Crud.crud_diaries_del(db, d_id)

            if not deleted_diary:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기 삭제에 실패했습니다")

            d_date = deleted_diary.d_date
            await db.commit()
            return {"msg": f"{d_date} 일기를 삭제하였습니다."}

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"일기 삭제에 실패했습니다: {e}")