from __future__ import annotations

from contextlib import asynccontextmanager

import colorama  # type: ignore[import-untyped]
from eyemath_models import Base  # type: ignore[import-untyped]
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import ConfigLoader
from src.core.utils import EnvTools

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class DataBase:
    def __init__(self) -> None:
        self.config = ConfigLoader()

        self.engine: AsyncEngine | None = None
        self.async_session: async_sessionmaker[AsyncSession] | None = None

        self.db_host = EnvTools.get_service_ip("postgres")
        self.db_port = EnvTools.get_service_port("postgres")
        self.db_user = EnvTools.required_load_env_var("POSTGRES_USER")
        self.db_pwd = EnvTools.required_load_env_var("POSTGRES_PASSWORD")
        self.db_name = EnvTools.required_load_env_var("POSTGRES_DB")
        self.engine_config = (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pwd}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


    async def init_alchemy_engine(self) -> None:
        logger.info("Starting service..")

        self.engine = create_async_engine(
            url=self.engine_config,
            echo=self.config.get("db", "echo"),
            pool_size=10,          # active connections in pool
            max_overflow=20,       # extra connections beyond pool_size
            pool_timeout=15,
            pool_recycle=1800,
            pool_pre_ping=True,
            future=True,
        )

        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        if await self.test_connection():
            logger.info(f"{colorama.Fore.GREEN}Connection with database has been established!")
        else:
            raise RuntimeError(f"{colorama.Fore.RED}Cannot establish connection with database.")


    async def get_session(self) -> AsyncIterator[AsyncSession]:
        assert self.async_session is not None, "Database engine is not initialized"
        async with self.async_session() as session:
            yield session


    @asynccontextmanager
    async def session_ctx(self) -> AsyncIterator[AsyncSession]:
        assert self.async_session is not None, "Database engine is not initialized"
        async with self.async_session() as session:
            yield session


    async def test_connection(self) -> bool:
        assert self.async_session is not None, "Database engine is not initialized"
        try:
            async with self.async_session() as session:
                result = await session.execute(text("SELECT 1"))
                # SQLAlchemy возвращает Any; приведём к Optional[int] для строгой типизации
                value = cast("int | None", result.scalar())
                return value == 1
        except Exception as ex:
            logger.error(f"Database connection failed: {ex}")
            return False


    async def create_tables(self) -> None:
        assert self.engine is not None, "Database engine is not initialized"
        try:
            async with self.engine.connect() as conn:
                await conn.run_sync(Base.metadata.create_all)
                await conn.commit()
            logger.success("All tables created successfully")
        except Exception as ex:
            logger.error(f"Failed to create all tables from models: {ex}")


    async def drop_all_tables(self) -> None:
        assert self.engine is not None, "Database engine is not initialized"
        try:
            async with self.engine.connect() as conn:
                await conn.run_sync(Base.metadata.drop_all)

                await conn.execute(
                    text(
                        "DROP TYPE IF EXISTS payment_method_enum, "
                        "deliveries_status_enum, "
                        "delivery_groups_status_enum CASCADE"
                    )
                )
                await conn.commit()
        except Exception as ex:
            logger.error(f"Failed to drop all tables: {ex}")

            
