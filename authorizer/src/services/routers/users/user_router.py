from __future__ import annotations

from typing import Any, Optional, Dict, TYPE_CHECKING
import uuid

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from src.core.utils import StringTools
from src.services.jwt.jwt_parser import JwtParser
from src.services.auth.auth_service import AuthService
from src.services.media_process.media_processor import MediaProcessor
from src.services.s3.s3 import S3Client
from src.services.auth.sessions_manager import SessionsManager
from src.services.routers.base_router import BaseRouter

from eyemath_models import User, Image  # type: ignore[import-untyped]
from eyemath_schemas import (  # type: ignore[import-untyped]
    RegisterResponse,
    LoginResponse,
    LogoutResponse,
    BanResponse,
    UnbanResponse,
    UploadAvatarResponse,
    UserCreateDTO,
    LoginRequest,
    BanRequest,
    UnbanRequest,
    UserRole,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.services.db.database import DataBase
    


def get_user_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])

    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    bearer_scheme = HTTPBearer()
    auth_service = AuthService(db)
    s3_service = S3Client()
    media_processor = MediaProcessor()


    @router.post("/register", status_code=201, response_model=RegisterResponse)
    async def register(
        data: UserCreateDTO,
        session: "AsyncSession" = Depends(db.get_session)
    ) -> RegisterResponse:
        
        if data.email and not await base_router.is_attribute_unique(session, User.email, data.email):
            raise base_router.http_ex_attribute_is_not_unique(User.email, "User")
        
        if data.phone and data.phone != "0000000000" and not await base_router.is_attribute_unique(session, User.phone, data.phone):
            raise base_router.http_ex_attribute_is_not_unique(User.phone, "User")

        if data.user_name and not await base_router.is_attribute_unique(session, User.user_name, data.user_name):
            raise base_router.http_ex_attribute_is_not_unique(User.user_name, "User")

        try:
            user = User(
                user_name=data.user_name,
                hashed_password=data.password.get_secret_value(),
                first_name=data.first_name.capitalize(),
                last_name=data.last_name.capitalize(),
                middle_name=data.middle_name.capitalize(),
                email=data.email,
                phone=data.phone or "0000000000",  # Default phone if not provided
                role=data.role,
            )

            session.add(user)
            await session.flush()
            await session.refresh(user)

            user_id: str = str(user.id) # converting to string because JSON can't serialize UUID :/

            dsh_map: Dict[str, str] = sessions_manager.get_test_dsh()
            dsh_concat = "".join(str(dsh_map[k]) for k in sorted(dsh_map))
            dsh: str = StringTools.hash_string(dsh_concat)

            session_create_result = sessions_manager.create_session(
                user_id=user_id,
                user_agent=dsh_map["user_agent"], 
                client_id=dsh_map["client_id"],
                local_system_time_zone=dsh_map["local_system_time_zone"],
                platform=dsh_map["platform"],
                ip=StringTools.hash_string(sessions_manager.get_test_client_ip()),
            )

            session_id: str = session_create_result["session_id"]

            test_ish: str = sessions_manager.get_test_client_ip()
            
            refresh_token = jwt_parser.generate_refresh_token(
                user_id=user_id,
                session_id=session_id,
                refresh_token="",
                dsh=dsh,
                ish=test_ish,
                make_old_refresh_token_used=False,
            )

            access_token: str = jwt_parser.generate_access_token(
                user_id=user_id,
                session_id=session_id,
                refresh_token=refresh_token,
                make_old_refresh_token_used=False,
            )

            await session.commit()

        except Exception as ex:
            logger.error(f"Couldn't add an object. {ex}")
            raise HTTPException(status_code=500, detail="Cannot register a new user because of internal error.")
        
        logger.debug(f"Registered user with UUID {user.id}")

        return RegisterResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        

    @router.post("/login", status_code=201, response_model=LoginResponse)
    async def login(
        data: LoginRequest,
        session: "AsyncSession" = Depends(db.get_session)
        ) -> LoginResponse:

        try:
            logger.debug(f"Login attempt with data: user_name={getattr(data, 'user_name', None)}, email={getattr(data, 'email', None)}, phone={getattr(data, 'phone', None)}")
            user: User = await base_router.find_user_by_any_credential(session, data)

            if not user.verify_password(data.password.get_secret_value()):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive.")

            user_id: str = str(user.id)
            
            dsh_map: Dict[str, str] = sessions_manager.get_test_dsh()
            dsh_concat = "".join(str(dsh_map[k]) for k in sorted(dsh_map))
            dsh: str = StringTools.hash_string(dsh_concat)

            session_create_result = sessions_manager.create_session(
                user_id=user_id,
                user_agent=dsh_map["user_agent"], 
                client_id=dsh_map["client_id"],
                local_system_time_zone=dsh_map["local_system_time_zone"],
                platform=dsh_map["platform"],
                ip=StringTools.hash_string(sessions_manager.get_test_client_ip()),
            )

            session_id: str = session_create_result["session_id"]
            
            test_ish: str = sessions_manager.get_test_client_ip()
            
            refresh_token = jwt_parser.generate_refresh_token(
                user_id=user_id,
                session_id=session_id,
                refresh_token="",
                dsh=dsh,
                ish=test_ish,
                make_old_refresh_token_used=False,
            )

            access_token: str = jwt_parser.generate_access_token(
                user_id=user_id,
                session_id=session_id,
                refresh_token=refresh_token,
                make_old_refresh_token_used=False,
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Login error: {ex}")
            raise HTTPException(status_code=500, detail="Internal server error.")

        logger.debug(f"User {user.id} logged in (session {session_id})")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )


    @router.post("/logout", status_code=200, response_model=LogoutResponse)
    async def logout(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession"= Depends(db.get_session),) -> LogoutResponse:
        """
        Logout: Accepts the access_token, extracts the sid from the token, and deletes the corresponding session.
        """
        try:
            payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)

            sid = payload.get("sid")
            if not sid:
                logger.debug(f"Access token missing session id (sid) claim: {payload}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token missing session id (sid).")

            try:
                sessions_manager.delete_session(sid)
                if sessions_manager.is_session_exists(sid):
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot delete session.")

            except Exception as ex:
                logger.exception(f"Error while deleting session {sid} {ex}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

            return LogoutResponse(
                succsess=True,
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Logout error: {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")


    @router.post("/ban", status_code=200, response_model=BanResponse)
    async def ban_user(
        data: BanRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
        ) -> BanResponse:
        """
        The user's ban. Requires valid access from the administrator.
        """
        try:
            role = await base_router.check_user_role(credentials, session)
            if role not in (UserRole.admin, UserRole.god):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin rights required.")
                
            try:
                ban_user_id: str = data.ban_user_id if isinstance(data.ban_user_id, str) else str(data.ban_user_id)
            except Exception:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ban_user_id.")

            await auth_service.ban_user(user_id=ban_user_id)
            sessions_manager.delete_all_sessions_for_user(ban_user_id)
            return BanResponse(
                succsess=True
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Ban user error: {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


    @router.post("/unban", status_code=200, response_model=UnbanResponse)
    async def unban_user(
        data: UnbanRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
        ) -> UnbanResponse:
        """
        The user's unban. Requires valid access from the administrator.
        """
        try:
            role = await base_router.check_user_role(credentials, session)
            if role not in (UserRole.admin, UserRole.god):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin rights required.")

            try:
                unban_user_id: str = data.unban_user_id if isinstance(data.unban_user_id, str) else str(data.unban_user_id)
            except Exception:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ban_user_id.")

            await auth_service.unban_user(user_id=unban_user_id)
            return UnbanResponse(
                succsess=True
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Unban user error: {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


    @router.post("/upload_avatar", status_code=200, response_model=UploadAvatarResponse)
    async def upload_avatar(
        data: UploadFile = File(...),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> UploadAvatarResponse:
        payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)
        sub_val = payload.get("sub")
        if not isinstance(sub_val, str) or not sub_val:
            raise HTTPException(status_code=400, detail="Invalid user id in token")
        sub: str = sub_val

        user: User = await session.get(
                User, sub
            )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not data.content_type or not data.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image/* allowed")

        raw = await data.read()

        result = media_processor.process_image(raw, data.content_type)

        filename: str = data.filename or "avatar" 
        key = s3_service.make_key(sub, filename, result.meta.mime)

        try:
            await s3_service.upload_bytes(
                data=result.data,
                key=key,
                content_type=result.meta.mime,
            )

        except Exception as ex:
            logger.error(f"there is an exception during the avatar uploading for user: {sub}\n{ex}")
            raise HTTPException(status_code=502, detail=f"S3 upload failed.")

        try:
            img = Image(
                media_type="image",
                bucket=s3_service.bucket_name,
                key=key,
                mime=result.meta.mime,
                size=result.meta.size,
                checksum_sha256=result.meta.checksum_sha256,
                width=result.meta.width,
                height=result.meta.height,
                exif_stripped=result.meta.exif_stripped,
                colorspace=result.meta.colorspace,
            )

            session.add(img)

            await session.flush()
            await session.refresh(img)

            user.profile_image_id = img.id
            await session.flush()
            await session.commit()

        except Exception:
            await session.rollback()
            try:
                await s3_service.delete_object(key)

            except Exception:
                pass
            raise HTTPException(status_code=500, detail="Failed to save avatar")

        return UploadAvatarResponse(
            succsess=True,
        )



    return router