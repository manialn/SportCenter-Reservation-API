from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.enumsfile.enum import UserRole
from app.database import get_db
from app.models import User
from app.core.config import settings
from app.core.redis_client import redis_client


db_dependency = Annotated[AsyncSession, Depends(get_db)]
form_data = Annotated[OAuth2PasswordRequestForm, Depends()]

passwordbearer = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


#redis
async def get_redis():
    return redis_client
#user_dependency
async def get_current_access(token: Annotated[str, Depends(passwordbearer)], db: db_dependency):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
user_dependency = Annotated[User,Depends(get_current_access)]

#admin_dependency
async def get_current_admin(user: user_dependency):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="you cant do it"
        )
    return user

admin_dependency = Annotated[User,Depends(get_current_admin)]

