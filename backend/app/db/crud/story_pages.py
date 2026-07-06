from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.story_pages import Story_Page 
from app.db.scheme.story_pages import Story_Page_Create


class Story_Page_Crud:
    # 동화책 페이지 생성
    @staticmethod
    async def crud_story_pages_create(db:AsyncSession,
                                      data: Story_Page_Create) -> Story_Page:          
        db_data=Story_Page(**data)
        db.add(db_data)
        await db.flush()
        return db_data
    

    # 동화책 페이지 연속 생성
    @staticmethod
    async def crud_story_pages_multi_create(db: AsyncSession, 
                                            datas: list[dict]) -> list[Story_Page]:          
        db_pages = [Story_Page(**data) for data in datas]
        db.add_all(db_pages)
        await db.flush()
        return db_pages

    
    # 동화책 페이지 목록
    @staticmethod
    async def crud_story_pages_list(db:AsyncSession, s_id:int) -> list[Story_Page] | None:
        result = await db.execute(select(Story_Page).filter(Story_Page.s_id == s_id))
        return result.scalars().all()
    

    # 동화책 페이지 상세
    @staticmethod
    async def crud_story_pages_detail(db:AsyncSession, sp_id:int) -> Story_Page | None:
        result = await db.execute(select(Story_Page).filter(Story_Page.sp_id == sp_id))
        return result.scalars().one_or_none()


    # 동화책 페이지 삭제
    @staticmethod
    async def crud_story_pages_del(db:AsyncSession, sp_id:int) -> Story_Page | None:
        db_data = await db.get(Story_Page, sp_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
    
