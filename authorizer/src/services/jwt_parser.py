import colorama
from loguru import logger
import jwt
from typing import Any

from src.core.config import ConfigLoader


class JwtParser:
    def __init__(self):
        self.config = ConfigLoader()
        self.jwt_private = self.config.get("jwt", "private_key_path")
        self.jwt_public = self.config.get("jwt", "public_key_path")
        self.algoritm = "RS256"


    def encode_jwt(self, payload: dict) -> Any:
        return jwt.encode(
                payload,
                private_key=self.jwt_private.read_text(),
                algorithm=self.algoritm
            )
    

    def decode_jwt(self, token: str | bytes) -> Any:
        return jwt.decode(
                token,
                public_key=self.jwt_public.read_text(),
                algorithms=[self.algoritm]
            )
    
