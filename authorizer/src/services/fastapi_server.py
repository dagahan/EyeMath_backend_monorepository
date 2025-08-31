import uvicorn
from fastapi import FastAPI
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.services.db.database import DataBase
from src.services.routers.tokens.token_router import get_token_router
from src.services.routers.users.user_router import get_user_router


class Server:
    def __init__(self) -> None:
        self.data_base = DataBase()
        self.config = ConfigLoader()
        self.app = FastAPI(
            title="Authorizer",
            description="Authorization service.",
            version="0.0.1"
        )
        self.uvicorn_config = uvicorn.Config(
            app=self.app,
            host=EnvTools.get_service_ip(self.config.get("project", "name")),
            port=int(EnvTools.get_service_port(self.config.get("project", "name"))),
            reload=True,
            log_level="info"
        )

        self.server: uvicorn.Server | None = None

        @self.app.on_event("shutdown")
        async def _on_shutdown() -> None:
            try:
                if self.data_base.engine is not None:
                    await self.data_base.engine.dispose()
            except Exception as ex:
                logger.warning(f"DB dispose failed during shutdown: {ex}")

    
    async def run_server(self) -> None:
        server = uvicorn.Server(self.uvicorn_config)
        await self.data_base.init_alchemy_engine()
        await self._register_routes()

        logger.info(self.data_base.engine)
        
        await server.serve()


    async def stop(self) -> None:
        """
        Gracefully stop uvicorn server from outside.
        """
        if not self.server:
            return

        self.server.should_exit = True

        shutdown = getattr(self.server, "shutdown", None)
        if callable(shutdown):
            try:
                await shutdown() 
            except Exception as ex:
                logger.debug(f"uvicorn shutdown() raised: {ex}")


    async def _register_routes(self) -> None:
        '''
        register all of endpoints.
        '''
        self.app.include_router(get_token_router(self.data_base))
        self.app.include_router(get_user_router(self.data_base))
            

