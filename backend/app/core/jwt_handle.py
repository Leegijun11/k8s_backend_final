from passlib.context import CryptContext

from datetime import datetime, timedelta, timezone
import jwt
import uuid

from app.core.settings import settings


pwd_crypt=CryptContext(schemes=["bcrypt"])

def get_password_hash(password:str):
    trunc_password=password.encode('utf-8')[:72]
    return pwd_crypt.hash(trunc_password)


def verify_password(plain_pw:str, hashed_pw:str)->bool:
    trunc_password=plain_pw.encode('utf-8')[:72]
    return pwd_crypt.verify(trunc_password,hashed_pw)


def create_token(u_id:int, expires_delta:timedelta, **kwargs) -> str:
    to_encode=kwargs.copy()
    expire=datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"u_id":u_id, "exp":expire})
    encoded_jwt=jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_access_token(u_id:int, **kwargs)->str:
    return create_token(u_id=u_id, expires_delta=settings.access_token_expire_seconds, **kwargs)


def create_refresh_token(u_id:int) -> str:
    return create_token(u_id=u_id, jti=str(uuid.uuid4()), expires_delta=settings.refresh_token_expire_seconds)


def decode_token(token:str)->dict:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm]
    )


def verify_token(token:str)->int:
    playload=decode_token(token)
    return playload.get("u_id")
