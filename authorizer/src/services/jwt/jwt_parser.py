from datetime import UTC, datetime, timedelta
from typing import Any, cast

from eyemath_schemas import AccessPayload, RefreshPayload  # type: ignore[import-untyped]
from fastapi import HTTPException, status
from jose import JWTError, jwt  # type: ignore[import-untyped]
from jose.exceptions import ExpiredSignatureError  # type: ignore[import-untyped]
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import EnvTools, StringTools, TimeTools
from src.services.auth.sessions_manager import SessionsManager


class JwtParser:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.sessions_manager: Any = SessionsManager()
        self.private_key: str = self._read_key("private_key") 
        self.public_key: str = EnvTools.required_load_env_var("public_key")
        self.access_token_expire_minutes: int = int(EnvTools.required_load_env_var("ACCESS_TOKEN_EXPIRE_MINUTES"))
        self.refresh_token_expire_days: int = int(EnvTools.required_load_env_var("REFRESH_TOKEN_EXPIRE_DAYS"))
        self.algorithm = "RS256"


    def _read_key(self, key_type: str) -> str:
        path = self.config.get("jwt", key_type)
        try:
            match key_type:
                case "private_key":
                    with open(path, "rb") as key_file:
                        return key_file.read().decode("utf-8")
                case "public_key":
                    with open(path, "rb") as key_file:
                        return key_file.read().decode("utf-8")
                case _:
                    raise ValueError(f"Unsupported key_type: {key_type}")
        except Exception as ex:
            logger.critical(f"Error during reading process of {key_type}: {ex}")
            raise


    def validate_token(self, token: str) -> AccessPayload | RefreshPayload:
        try:
            return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
        
        except JWTError as ex:
            logger.error(f"JWT validation error: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


    def decode_token(self, token: str) -> dict[str, Any]:
        """
        Universal token decoding (for access and refresh).
        Returns payload (dict) on success, throws HttpException (401) on error.
        """
        try:
            payload = cast("dict[str, Any]", jwt.decode(token, self.public_key, algorithms=[self.algorithm]))
            return payload  # dict

        except ExpiredSignatureError as ex:
            logger.debug(f"Token expired: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

        except JWTError as ex:
            logger.debug(f"JWT validation error: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        except Exception as ex:
            logger.exception(f"Unexpected error while decoding token: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


    def generate_refresh_token(
        self,
        user_id: str,
        session_id: str,
        refresh_token: str,
        dsh: str,
        ish: str,
        make_old_refresh_token_used: bool = True
    ) -> str:
        if not make_old_refresh_token_used and refresh_token is not None and self.is_refresh_token_in_invalid_list(refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token already used")

        expires_at = int((datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)).timestamp())
        jwt_payload = RefreshPayload(
            sub=user_id,
            sid=session_id,
            exp=expires_at,
            dsh=dsh,
            ish=ish,
        )

        if make_old_refresh_token_used:
            self.make_refresh_token_invalid(refresh_token)

        return cast("str", jwt.encode(jwt_payload.model_dump(), self.private_key, algorithm=self.algorithm)) 


    def make_refresh_token_invalid(self, refresh_token: str) -> None:
        """
        Marks refresh as used (one-time).
        Creates the Invalid_refresh key:{hash_session_id}:{refresh_hash} from TTL to exp.
        """
        try:
            claims = cast("dict[str, Any]", jwt.get_unverified_claims(refresh_token))
            exp_val = claims.get("exp")
            exp_time_stamp: int | None = int(exp_val) if isinstance(exp_val, (int, str)) else None
        except Exception:
            exp_time_stamp = None

        now_ts = TimeTools.now_time_stamp()
        ttl: int = max(1, exp_time_stamp - now_ts) if exp_time_stamp is not None else 1

        key: str = f"Invalid_refresh:{refresh_token}"
        self.sessions_manager.valkey_service.valkey.set(key, "1", ex=ttl)


    def is_refresh_token_in_invalid_list(self, refresh_token: str) -> bool:
        key: str = f"Invalid_refresh:{refresh_token}"
        exists_val: int = int(self.sessions_manager.valkey_service.valkey.exists(key))
        return exists_val == 1
        
    
    def generate_access_token(
        self,
        user_id: str,
        session_id: str,
        refresh_token: str,
        make_old_refresh_token_used: bool = True
    ) -> str:
        if refresh_token is not None and self.is_refresh_token_in_invalid_list(refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token already used")

        expires_at = int((datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)).timestamp())
        jwt_payload = AccessPayload(
            sub=user_id,
            sid=session_id,
            exp=expires_at,
        )

        if make_old_refresh_token_used:
            self.make_refresh_token_invalid(refresh_token)

        return cast("str", jwt.encode(jwt_payload.model_dump(), self.private_key, algorithm=self.algorithm))
        
 

