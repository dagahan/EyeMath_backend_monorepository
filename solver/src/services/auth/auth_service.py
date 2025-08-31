from eyemath_models import User # type: ignore[import-untyped]
from fastapi import HTTPException, status
from jose import JWTError  # type: ignore[import-untyped]
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import noload

from typing import Any
from src.services.auth.sessions_manager import SessionsManager
from src.services.db.database import DataBase
from src.services.jwt.jwt_parser import JwtParser


class AuthService:
    def __init__(self, db: DataBase) -> None:
        self.db = db
        self.jwt_parser = JwtParser()
        self.sessions_manager = SessionsManager()
        self.access_token_expire_minutes: int = self.jwt_parser.access_token_expire_minutes
        self.refresh_token_expire_days: int = self.jwt_parser.refresh_token_expire_days


    async def authenticate_user(self, identifier: str, password: str) -> User:
        async with self.db.session_ctx() as session:
            result = await session.execute(
                select(User)
                .where(
                    (User.email == identifier) | (User.phone == identifier)
                )
            )
            user = result.scalars().first()
            
            if not user or not User.verify_password(password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account deactivated"
                )
                
            return user

    
    async def validate_access_token(self, access_token: str) -> bool:
        try:
            payload: dict[str, Any] = self.jwt_parser.decode_token(access_token)

            user_id = payload.get("sub")
            session_id = payload.get("sid")
            expire = payload.get("exp")

            if not session_id or not user_id or not expire:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )

            session = self.sessions_manager.get_session(str(session_id))
            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session expired"
                )

            session_user_id = getattr(session, "sub", None)
            if session_user_id is not None and str(session_user_id) != str(user_id):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not match session user"
                )

            return True

            return True

        except JWTError as ex:
            logger.error(f"Access token error: {ex}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )


    async def get_access_token_by_refresh_token(self, refresh_token: str) -> str:
        try:
            payload = self.jwt_parser.validate_token(refresh_token)
            
            if not payload.get("dsh"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
                
            session_id = payload.get("sid")
            user_id = payload.get("sub")
            
            if not session_id or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
                
            if not self.sessions_manager.is_session_exists(session_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session isn't exist."
                )
            
            return self.jwt_parser.generate_access_token(
                user_id=user_id,
                session_id=session_id,
                refresh_token=refresh_token,
                make_old_refresh_token_used=True,
            )
            
        except JWTError as ex:
            logger.error(f"Refresh token error: {ex}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )


    async def set_is_active_user(
        self,
        user_id: str,
        option: bool
    ) -> None:
        async with self.db.session_ctx() as session:
            try:
                result = await session.execute(
                                select(User)
                                .where(User.id == user_id)
                                .options(noload("*"))
                            )
                user = result.scalar_one_or_none()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )

                user.is_active = option
                    
                await session.commit()
            
            except Exception as ex:
                logger.error(f"Couldn't ban user during the exception: {ex}")
                raise HTTPException(status_code=500, detail="Couldn't ban user during the server error.")
        

    async def ban_user(self, user_id: str) -> None:
        '''
        just synonim to set set_is_active_user(False).
        '''
        await self.set_is_active_user(user_id, False)


    async def unban_user(self, user_id: str) -> None:
        '''
        just synonim to set set_is_active_user(True).
        '''
        await self.set_is_active_user(user_id, True)


