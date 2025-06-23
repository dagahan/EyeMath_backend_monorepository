import colorama
from loguru import logger
import jwt
import bcrypt
from typing import Any

from src.core.config import ConfigLoader
from typing import Any, Optional, Dict


class JwtParser:
    def __init__(self):
        self.config = ConfigLoader()
        self.private_key = self._read_key("private_key_path")
        self.public_key = self._read_key("public_key_path")
        self.algorithm = "RS256"


    def _read_key(self, key_type: str) -> str:
        path = self.config.get("jwt", key_type)
        try:
            with open(path, "r") as key_file:
                return key_file.read()
        except Exception as e:
            logger.critical(f"Ошибка чтения JWT ключа: {e}")
            raise
    

    def encode_jwt(self, payload: dict) -> str:
        return jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm
        )
    

    def decode_jwt(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm]
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Невалидный JWT токен: {e}")
            raise
    

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        try:
            payload = self.decode_jwt(token)
            return {
                "result": True,
                "user_id": int(payload["sub"]),
            }
        except jwt.ExpiredSignatureError:
            return {"result": False, "reason": "Token expired"}
        except jwt.InvalidTokenError:
            return {"result": False, "reason": "Invalid token"}
        except Exception as e:
            logger.error(f"Ошибка верификации токена: {e}")
            return {"result": False, "reason": "Verification error"}
    
