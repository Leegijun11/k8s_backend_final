from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.database import get_db
from app.db.models.babies import Baby
from app.services.diaries import Diary_Service
from app.db.scheme.diaries import Diary_Create
from sqlalchemy.future import select
from datetime import date
import pytz
from app.db.models.stories import Story
from app.services.stories import Story_Service
from app.db.scheme.stories import Story_Create
from datetime import date, timedelta

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

                # 생일로부터 정확히 1년 후인지 확인
                try:
                    first_birthday = birth.replace(year=birth.year + 1)
                except ValueError:
                    # 2월 29일 생일 등 윤년 예외 처리
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
    """매일 정해진 시간에 모든 아기에 대해 그날 일기를 자동 생성"""
    async for db in get_db():
        try:
            result = await db.execute(select(Baby))
            babies = result.scalars().all()

            today = date.today()

            for baby in babies:
                try:
                    diary_data = Diary_Create(b_id=baby.b_id, d_date=today)
                    await Diary_Service.service_diaries_create(db, diary_data)
                    print(f"[diary] b_id={baby.b_id} 일기 생성 완료")
                except Exception as e:
                    # 그날 로그/사진이 없는 아이는 실패해도 다음 아이로 넘어감
                    print(f"[diary] b_id={baby.b_id} 일기 생성 실패: {e}")
        finally:
            break  # get_db는 async generator라 한 번만 사용


def start_scheduler():
    # 매일 밤 21시(오후 9시)에 실행 - 원하는 시간으로 변경 가능
    scheduler.add_job(generate_daily_diaries, "cron", hour=16, minute=20)
    scheduler.add_job(generate_first_birthday_books, "cron", hour=16, minute=47)
    scheduler.start()
    print("[scheduler] 일기 자동 생성 + 첫 생일 디지털북 스케줄러가 시작되었습니다.")