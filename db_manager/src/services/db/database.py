import colorama
from eyemath_models.base_model import Base
from loguru import logger
from sqlalchemy import (
    text,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import ConfigLoader
from src.core.utils import EnvTools


class DataBase:
    def __init__(self,) -> None:
        self.config = ConfigLoader()
        self.engine = None
        self.db_host = None
        self.db_port = None
        self.db_user = None
        self.db_pwd = None
        self.db_name = None
        self.engine_config = None
        self.async_session = None


    async def init_alchemy_engine(self,) -> None:
        logger.info("Starting service..")

        self.db_host = EnvTools.get_service_ip("postgres")
        self.db_port = EnvTools.get_service_port("postgres")
        self.db_user = EnvTools.load_env_var("POSTGRES_USER")
        self.db_pwd = EnvTools.load_env_var("POSTGRES_PASSWORD")
        self.db_name = EnvTools.load_env_var("POSTGRES_DB")

        self.engine_config = (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        logger.debug(f"{self.engine_config}")
        self.engine = create_async_engine(
            url=self.engine_config,
            echo=False,
            pool_size=10, # count of active connections in pool
            max_overflow=20, # max amount of connections
            pool_timeout=15,
            pool_recycle=1800,
            pool_pre_ping=True,
            future=True,
        )

        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

        if await self.test_connection():
            logger.info(f"{colorama.Fore.GREEN}Connection with data base has been established!")
        else:
            raise Exception(f"{colorama.Fore.RED}Cannot establish connection with data base.")


    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            yield session

        
    async def test_connection(self) -> bool:
        try:
            async with self.async_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1

        except Exception as ex:
            logger.error(f"Database connection failed: {ex}")
            return False

    
    async def create_tables(self,) -> None:
        try:
            async with self.engine.connect() as conn:
                await conn.run_sync(Base.metadata.create_all)
                await conn.commit()
            logger.success("All tables created successfully")

        except Exception as ex:
            logger.error(f"Failed to create all tables from models: {ex}")


    async def drop_all_tables(self,) -> None:
        try:
            async with self.engine.connect() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            
                await conn.execute(text(
                    "DROP TYPE IF EXISTS payment_method_enum, "
                    "deliveries_status_enum, "
                    "delivery_groups_status_enum CASCADE"
                ))

                await conn.commit()
        
        except Exception as ex:
            logger.error(f"Failed to drop all tables: {ex}")
        
