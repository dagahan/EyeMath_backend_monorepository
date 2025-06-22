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
        self.jwt_private = self.config.get("jwt", "private_key_path")
        self.jwt_public = self.config.get("jwt", "public_key_path")
        self.algoritm = "RS256"


    def _read_key(self, key_type: str) -> str:
        """Чтение ключа из файла"""
        path = self.config.get("jwt", key_type)
        try:
            with open(path, "r") as key_file:
                return key_file.read()
        except Exception as e:
            logger.critical(f"Ошибка чтения JWT ключа: {e}")
            raise
    

    def encode_jwt(self, payload: dict) -> str:
        """Кодирование JWT токена"""
        return jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm
        )
    

    def decode_jwt(self, token: str) -> Dict[str, Any]:
        """Декодирование и верификация JWT токена"""
        try:
            return jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError:
            logger.warning("JWT токен истек")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"Невалидный JWT токен: {e}")
            raise
    

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """Проверка JWT токена с обработкой ошибок"""
        try:
            payload = self.decode_jwt(token)
            return {
                "valid": True,
                "user_id": int(payload["sub"]),
                "username": payload["username"],
                "expires": payload["exp"]
            }
        except jwt.ExpiredSignatureError:
            return {"valid": False, "reason": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "reason": "Invalid token"}
        except Exception as e:
            logger.error(f"Ошибка верификации токена: {e}")
            return {"valid": False, "reason": "Verification error"}
    
