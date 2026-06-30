#crud_forum_create 게시글 생성
#crud_forum_list 게시글 목록
#crud_forum_context 게시글 상세
#crud_forum_update 게시글 수정
#crud_forum_delete 게시글 삭제

from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.forums import Forums
from app.db.models.forumtags import ForumTag 
from app.db.scheme.forums import Forum_Create, Forum_Update

from app.db.models.babies import Baby
from app.db.models.babycharacters import BabyCharacter

from app.db.models.forumlikes import ForumLike

class Forums_CRUD:

    #게시글 생성
    @staticmethod
    async def crud_forum_create(db: AsyncSession, forum_data:Forum_Create , u_id:int):
        new_forum=Forums(
            u_id=u_id,
            b_id=forum_data.b_id,
            f_title=forum_data.f_title,
            f_content=forum_data.f_content,
            f_image=forum_data.f_image,
        )

        new_tag=ForumTag(
            ft_sleep=forum_data.forum_tag.ft_sleep,
            ft_food=forum_data.forum_tag.ft_food,
            ft_health=forum_data.forum_tag.ft_health,
            ft_play=forum_data.forum_tag.ft_play,

        )
        new_forum.forum_tag=new_tag


        db.add(new_forum)
        await db.commit()
        await db.refresh(new_forum)
        return new_forum



    #게시글 목록(태그 분류)
    @staticmethod
    async def crud_forum_list(db:AsyncSession,
                              tag: str | None = None,
                              baby_character: str | None= None,
                              sort: str | None = None,
                              u_id: int | None=None):
        list_forums=select(Forums).options(joinedload(Forums.forum_tag), joinedload(Forums.user))


        #태그 분류
        TAG_MAP={
            'sleep':ForumTag.ft_sleep,
            'food':ForumTag.ft_food,
            'health':ForumTag.ft_health,
            'play':ForumTag.ft_play,
        }
        
        if tag and tag in TAG_MAP:
            list_forums=list_forums.join(ForumTag).where(TAG_MAP[tag]==True)

        #아기 기질 분류
        CHARACTER_MAP = {
            'curiosity': BabyCharacter.c_curiosity,
            'active': BabyCharacter.c_active,
            'shy': BabyCharacter.c_shy,
            'eater': BabyCharacter.c_eater,
            'sleepy': BabyCharacter.c_sleepy,
            'charm': BabyCharacter.c_charm,
        }

        if baby_character and baby_character in CHARACTER_MAP:
            list_forums=list_forums.join(Forums.baby).join(Baby.character).where(CHARACTER_MAP[baby_character]==True)

        #정렬
        if sort == 'like':
            list_forums=list_forums.order_by(desc(Forums.f_like_count), desc(Forums.f_created_at))
        else:
            list_forums=list_forums.order_by(desc(Forums.f_created_at))

        result=await db.execute(list_forums)
        # return result.scalars().all()

        # 좋아요 표시 
        forums= result.scalars().all()
    
        if u_id and forums:
            forum_ids = [f.f_id for f in forums]
                
            liked_stmt = select(ForumLike.f_id).where(
                ForumLike.u_id == u_id,
                ForumLike.f_id.in_(forum_ids)
            )
            liked_result = await db.execute(liked_stmt)
            liked_set = set(liked_result.scalars().all()) 
                

            for f in forums:
                f.is_liked = f.f_id in liked_set
        else:

            for f in forums:
                f.is_liked = False

        return forums

    #게시글 상세
    @staticmethod
    async def crud_forum_context(db:AsyncSession, f_id: int, u_id: int | None = None):
        forums=select(Forums).options(joinedload(Forums.forum_tag),joinedload(Forums.user)).where(Forums.f_id==f_id)
        result=await db.execute(forums)
        return result.scalar_one_or_none()
    

    #게시글 수정
    @staticmethod
    async def crud_forum_update(db:AsyncSession, db_forum: Forums, forum_data: Forum_Update):
        update_forum=forum_data.model_dump(exclude_unset=True, exclude={"forum_tag"})
        for key, value in update_forum.items():
            setattr(db_forum, key, value)

        #태그 업데이트
        if forum_data.forum_tag:
            update_tags=forum_data.forum_tag.model_dump(exclude_unset=True)
            for key, value in update_tags.items():
                setattr(db_forum.forum_tag, key, value)   


        await db.commit()
        await db.refresh(db_forum)
        return db_forum

    
    #게시글 삭제
    @staticmethod
    async def crud_forum_delete(db:AsyncSession, db_forum: Forums):
        await db.delete(db_forum)
        await db.commit()
        return True