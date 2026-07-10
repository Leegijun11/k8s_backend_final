from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.users import User 
from app.db.scheme.users import User_Create, User_Update


class User_Crud:
    # 유저 회원가입
    @staticmethod
    async def crud_users_signup(db:AsyncSession, 
                               user: User_Create, 
                               hashed_pw:str) -> User:          
        data = user.model_dump()
        data["u_pw"] = hashed_pw
        
        db_data=User(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 유저 정보
    @staticmethod
    async def crud_users_me(db:AsyncSession, u_id:int) -> User | None:
        result = await db.execute(select(User).filter(User.u_id == u_id))
        return result.scalars().first()


    # 유저 아이디 찾기
    @staticmethod
    async def crud_users_u_account_by_udata(db: AsyncSession, 
                                           u_name: str, 
                                           u_email: str, 
                                           u_phone: str) -> User | None:
        result = await db.execute(select(User)
                                  .filter(User.u_name == u_name, 
                                          User.u_email==u_email,
                                          User.u_phone==u_phone))
        return result.scalars().first() 
    

    # 유저 비밀번호 찾기
    @staticmethod
    async def crud_users_u_pw_by_udata(db: AsyncSession,
                                       u_account :str,
                                       u_name: str,
                                       u_email: str,
                                       u_phone: str) -> User | None:
        result = await db.execute(select(User)
                                  .where(User.u_account==u_account, 
                                          User.u_name == u_name, 
                                          User.u_email==u_email,
                                          User.u_phone==u_phone))
        return result.scalars().first() 
    

    # 유저 정보 수정
    @staticmethod
    async def crud_users_update(db:AsyncSession, 
                               u_id:int, 
                               user:User_Update)->User|None:
        db_data=await db.get(User, u_id)
        
        if db_data:           
            update_data= user.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None
    

    # 유저 삭제
    @staticmethod
    async def crud_users_del(db:AsyncSession , u_id:int)->User|None:
        db_data = await db.get(User, u_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
    

    # 유저 토큰 업데이트
    @staticmethod
    async def crud_users_update_token(db: AsyncSession, 
                                     u_id: int, 
                                     token: str | None)->User:
        db_data = await db.get(User, u_id)
        
        if db_data:
            db_data.refresh_token = token
            await db.flush()
        
        return db_data
 


     #입력한(u_account)아이디 정보 가져오기
    @staticmethod
    async def crud_users_get_by_account(db:AsyncSession, u_account: str)-> User | None:
        result=await db.execute(select(User).filter(User.u_account==u_account))
        return result.scalars().first()
    
    # 이메일 중복검사
    @staticmethod
    async def crud_users_get_by_email(db: AsyncSession, u_email: str) -> User | None:
        result = await db.execute(select(User).filter(User.u_email == u_email))
        return result.scalars().first()
    
    # 전화번호 중복검사
    @staticmethod
    async def crud_users_get_by_phone(db: AsyncSession, u_phone: str) -> User | None:
        result = await db.execute(select(User).filter(User.u_phone == u_phone))
        return result.scalars().first()
