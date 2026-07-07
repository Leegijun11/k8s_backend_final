from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.database import get_db
from app.db.models.babies import Baby
from app.db.models.parents import Parent
from app.services.diaries import Diary_Service
from app.db.scheme.diaries import Diary_Create
from app.db.crud.alarms import Alarm_Crud
from app.db.scheme.alarms import Alarm_Create
from sqlalchemy.future import select
from datetime import date, timedelta
import pytz
from app.db.models.stories import Story
from app.services.stories import Story_Service
from app.db.scheme.stories import Story_Create

scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Seoul"))


async def generate_first_birthday_books():
    """매일 자정(00:00)에 실행, 오늘이 만 1세 생일인 아기를 찾아 디지털북 자동 생성"""
    async for db in get_db():
        try:
            result = await db.execute(select(Baby))
            babies = result.scalars().all()
            today = date.today()

            for baby in babies:
                birth = baby.b_birth
                if isinstance(birth, str):
                    birth = date.fromisoformat(birth)
                elif hasattr(birth, "date"):
                    birth = birth.date()

                try:
                    first_birthday = birth.replace(year=birth.year + 1)
                except ValueError:
                    first_birthday = birth.replace(year=birth.year + 1, day=28)

                if today == first_birthday:
                    try:
                        story_data = Story_Create(
                            b_id=baby.b_id,
                            start_date=birth,
                            end_date=today
                        )
                        await Story_Service.service_stories_create(db, story_data)
                        print(f"[story] b_id={baby.b_id} 첫 생일 디지털북 생성 완료")
                    except Exception as e:
                        print(f"[story] b_id={baby.b_id} 첫 생일 디지털북 생성 실패: {e}")
        finally:
            break


async def generate_daily_diaries():
    """매일 정해진 시간에 모든 아기에 대해 그날 일기를 자동 생성 + 알림 발송"""
    async for db in get_db():
        try:
            result = await db.execute(select(Baby))
            babies = result.scalars().all()
            today = date.today()

            for baby in babies:
                try:
                    # 1. 일기 생성
                    diary_data = Diary_Create(b_id=baby.b_id, d_date=today)
                    await Diary_Service.service_diaries_create(db, diary_data, ai_create=True)
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
    scheduler.add_job(generate_daily_diaries, "cron", hour=16, minute=20)
    scheduler.add_job(generate_first_birthday_books, "cron", hour=16, minute=47)
    scheduler.start()
    print("[scheduler] 일기 자동 생성 + 첫 생일 디지털북 스케줄러가 시작되었습니다.")