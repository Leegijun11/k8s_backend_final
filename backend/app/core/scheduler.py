from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.database import get_db
from app.db.models.babies import Baby
from app.db.models.parents import Parent
from app.services.diaries import Diary_Service
from app.db.crud.alarms import Alarm_Crud
from app.db.scheme.alarms import Alarm_Create
from sqlalchemy.future import select
from datetime import date, timedelta
import pytz

scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Seoul"))


async def generate_daily_diaries():
    """매일 정해진 시간에 모든 아기에 대해 그날 일기를 자동 생성 + 알림 발송"""
    async for db in get_db():
        try:
            result = await db.execute(select(Baby))
            babies = result.scalars().all()

            for baby in babies:
                try:
                    # 1. 일기 생성 (오늘 로그 있으면 생성, 없으면 None 반환 후 스킵)
                    new_diary = await Diary_Service.service_diaries_create_system(db, baby.b_id)

                    if new_diary is None:
                        print(f"[diary] b_id={baby.b_id} 오늘 로그 없음 - 일기 생성 스킵")
                        continue

                    print(f"[diary] b_id={baby.b_id} 일기 생성 완료")

                    # 2. 해당 아기의 active 부모 목록 조회
                    parent_result = await db.execute(
                        select(Parent).where(
                            Parent.g_id == baby.g_id,
                            Parent.p_state == "active"
                        )
                    )
                    parents = parent_result.scalars().all()

                    # 3. 각 부모에게 diary 타입 알림 생성
                    for parent in parents:
                        try:
                            alarm_data = Alarm_Create(
                                send_id=None,       # 시스템 발송
                                receive_id=parent.u_id,
                                g_id=baby.g_id,
                                a_type="diary"
                            )
                            await Alarm_Crud.crud_alarms_create(db, alarm_data)
                            print(
                                f"[alarm] u_id={parent.u_id} "
                                f"b_id={baby.b_id} diary 알림 생성 완료"
                            )
                        except Exception as e:
                            print(f"[alarm] u_id={parent.u_id} 알림 생성 실패: {e}")

                    await db.commit()

                except Exception as e:
                    print(f"[diary] b_id={baby.b_id} 일기 생성 실패: {e}")
                    await db.rollback()

        finally:
            break


def start_scheduler():
    scheduler.add_job(generate_daily_diaries, "cron", hour=10, minute=30)
    scheduler.start()
    print("[scheduler] 일기 자동 생성이 시작되었습니다.")