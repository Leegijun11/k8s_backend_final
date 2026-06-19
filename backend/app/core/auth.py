from fastapi import Request, Response, HTTPException, Depends, status
from jwt import ExpiredSignatureError, InvalidTokenError
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models.users import User
from app.core.settings import settings
from app.core.jwt_handle import verify_token, create_access_token


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, autologin: bool = False) -> None:
    access_max_age = int(settings.access_token_expire.total_seconds()) if autologin else None

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=access_max_age,
        httponly=True,
        secure=False,
        samesite="Lax"
    )

    refresh_max_age = int(settings.refresh_token_expire.total_seconds()) if autologin else None

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        secure=False,
        samesite="Lax"
    )


async def auth_get_u_id(request: Request, response: Response) -> int:
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if access_token:
        try:
            u_id = verify_token(access_token)
            if u_id:
                return u_id
        except ExpiredSignatureError:
            pass
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid Token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Session expired")

    try:
        u_id = verify_token(refresh_token)
        
        new_access = create_access_token(u_id=u_id, data={"sub": str(u_id)})
        response.set_cookie(
            key="access_token",
            value=new_access,
            max_age=int(settings.access_token_expire.total_seconds()),
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return u_id

    except (ExpiredSignatureError, InvalidTokenError):
        raise HTTPException(status_code=401, detail="Refresh token expired")


async def get_optional(request: Request) -> Optional[int]:
    token = request.cookies.get("access_token")

    if not token:
        return None

    try:
        return verify_token(token)
    except (ExpiredSignatureError, InvalidTokenError):
        return None