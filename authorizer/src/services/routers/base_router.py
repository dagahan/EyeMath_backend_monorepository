from typing import Any, Optional, Dict
from uuid import UUID as PythonUUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from fastapi.security import HTTPAuthorizationCredentials

from src.core.utils import ValidatingTools
from src.services.db.database import DataBase
from src.services.jwt.jwt_parser import JwtParser

from eyemath_models import User  # type: ignore[import-untyped]
from eyemath_schemas import UserDTO, UserRole  # type: ignore[import-untyped]


class BaseRouter:
    def __init__(self, db: DataBase) -> None:
        self.db = db
        self.jwt_parser = JwtParser()


    async def find_user_by_any_credential(self, session: AsyncSession, user_data: Any) -> User:
        from loguru import logger
        
        user_name = getattr(user_data, "user_name", None)
        email = getattr(user_data, "email", None)
        phone = getattr(user_data, "phone", None)
        
        logger.debug(f"Searching user by: user_name={user_name}, email={email}, phone={phone}")
        
        if user_name:
            query = select(User).where(User.user_name == user_name)
            logger.debug(f"Searching by username: {user_name}")
        elif email:
            query = select(User).where(User.email == email)
            logger.debug(f"Searching by email: {email}")
        elif phone:
            query = select(User).where(User.phone == phone)
            logger.debug(f"Searching by phone: {phone}")
        else:
            logger.error("No login credential provided")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Login (user_name, email or phone) is required")

        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found for credentials: user_name={user_name}, email={email}, phone={phone}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        logger.debug(f"User found: {user.id}")

        # Skip DTO validation for login - it's not necessary and can cause issues
        # The user object is already validated by the database constraints
        return user


    async def is_attribute_unique(
        self,
        session: AsyncSession,
        attribute: Any,
        value: Any,
        exclude_id: Optional[PythonUUID | str] = None,
    ) -> bool:
        model = attribute.class_
        if not hasattr(model, "__tablename__"):
            raise ValueError("Attribute must be a SQLAlchemy column property")

        query = select(model).where(attribute == value)
        if exclude_id is not None:
            query = query.where(model.id != exclude_id)

        result = await session.execute(query)
        return len(result.scalars().all()) == 0


    def http_ex_attribute_is_not_unique(self, attribute: Any, entity_name: str = "Entity") -> HTTPException:
        return HTTPException(
            status_code=400,
            detail=f"{entity_name} with this {getattr(attribute, 'key', str(attribute))} already exists"
        )


    async def get_payload_or_401(self, credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        if credentials is None or not credentials.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing.")
        return self.jwt_parser.decode_token(credentials.credentials)


    async def check_user_role(
        self,
        credentials: HTTPAuthorizationCredentials,
        session: AsyncSession,
    ) -> UserRole:
        payload: Dict[str, Any] = await self.get_payload_or_401(credentials)
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token missing sub.")

        async with self.db.session_ctx() as db_session:
            result = await db_session.execute(
                select(User).where(User.id == sub).options(noload("*"))
            )
            user: User | None = result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found."
                )

        return user.role