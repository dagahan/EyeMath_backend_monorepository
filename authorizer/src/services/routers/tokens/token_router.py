from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from src.core.utils import StringTools

from src.services.jwt.jwt_parser import JwtParser
from src.services.auth.auth_service import AuthService
from src.services.auth.sessions_manager import SessionsManager

from eyemath_schemas import (  # type: ignore[import-untyped]
    RequestAccess,
    ResponseAccess,
    RequestRefresh,
    ResponseRefresh,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.services.db.database import DataBase


def get_token_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/tokens", tags=["tokens"])

    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    auth_service = AuthService(db)


    @router.get("/access", status_code=200, response_model=ResponseAccess)
    async def access(
        data: RequestAccess,
        session: AsyncSession = Depends(db.get_session),
    ) -> ResponseAccess:
        try:
            logger.debug(f"Test msg from user with access token: {data.access_token}")
            is_valid = await auth_service.validate_access_token(data.access_token)
            return ResponseAccess(valid=is_valid)
        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Cannot test an access token: {ex}")
            raise HTTPException(status_code=500, detail="Cannot test access token because of internal error.")


    @router.post("/refresh", status_code=201, response_model=ResponseRefresh)
    async def refresh(
        data: RequestRefresh,
        session: AsyncSession = Depends(db.get_session),
    ) -> ResponseRefresh:
        try:
            payload: Dict[str, Any] = jwt_parser.decode_token(data.refresh_token)

            session_id: str = payload.get("sid")
            user_id: str = payload.get("sub")

            if not isinstance(session_id, str) or not isinstance(user_id, str):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload.")

            if not sessions_manager.is_session_exists(session_id):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Session is expired.")

            logger.debug(f"New access and refresh tokens generated with refresh token for user: {user_id}")

            new_access_token = await auth_service.get_access_token_by_refresh_token(data.refresh_token)

            dsh_map: Dict[str, str] = sessions_manager.get_test_dsh()
            dsh_concat = "".join(str(dsh_map[k]) for k in sorted(dsh_map))
            dsh: str = StringTools.hash_string(dsh_concat)
            
            test_ish: str = sessions_manager.get_test_client_ip()
            
            new_refresh_token = jwt_parser.generate_refresh_token(
                user_id=user_id,
                session_id=session_id,
                refresh_token=data.refresh_token,
                dsh=dsh,
                ish=test_ish,
                make_old_refresh_token_used=True,
            )

            return ResponseRefresh(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Cannot refresh access token: {ex}")
            raise HTTPException(status_code=500, detail="Cannot refresh access token because of internal error.")



    return router


