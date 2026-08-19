from jose import jwt,JWTError
from datetime import timedelta,datetime,timezone
from fastapi import HTTPException,status
from app.core.config import settings
from uuid import UUID,uuid4



def create_access_token(user_id : UUID, expires_delta: timedelta):
    encode = {"sub" : str(user_id)
              ,"type" : "access"}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp" : expires})
    return jwt.encode(encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM,)

def create_refresh_token(user_id: UUID, expires_delta: timedelta):
    jti = uuid4()
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": str(user_id),
        "type": "refresh",
        "jti": str(jti),
        "exp": expires}
    token = jwt.encode(encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM,)
    return token, jti, expires

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])

        user_id = payload.get("sub")
        token_type = payload.get("type")
        jti = payload.get("jti")
        expires_at = payload.get("exp")

        if token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token type")

        if user_id is None or jti is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid refresh token")

        return UUID(user_id), UUID(jti), datetime.fromtimestamp(
            expires_at,
            timezone.utc
        )

    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Refresh token is invalid or expired")