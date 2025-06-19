import asyncio

import colorama
import uvicorn
from fastapi import FastAPI
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.external_gateway.graphql.schema import Shema


class ExternalGatewayServer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.gateway_app = FastAPI()
        self.host = EnvTools.load_env_var("GATEWAY_HOST")
        self.port = EnvTools.load_env_var("GATEWAY_APP_PORT")
        self.shema = Shema()
        self.gateway_app.include_router(self.shema.create_graphql_router(), prefix="/graphql")
        self.server = None
        self._stop_requested = False


    async def run_external_gateway(self):
        config = uvicorn.Config(
            app=self.gateway_app,
            host=self.host,
            port=self.port,
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "loggers": {
                    "uvicorn": {"level": "WARNING"},
                    "uvicorn.error": {"level": "WARNING"},
                    "uvicorn.access": {
                        "handlers": ["access"],
                        "level": "INFO",
                        "propagate": False
                    },
                },
                "handlers": {
                    "access": {
                        "class": "logging.StreamHandler",
                        "formatter": "access",
                        "stream": "ext://sys.stdout",
                    },
                },
                "formatters": {
                    "access": {
                        "()": "uvicorn.logging.AccessFormatter",
                        "fmt": '%(asctime)s - %(levelname)s - %(message)s',
                    },
                },
            }
        )
        self.server = uvicorn.Server(config)
        
        try:
            logger.info(f"{colorama.Fore.GREEN}Starting FastAPI on {colorama.Fore.YELLOW}http://{self.host}:{self.port}/graphql")
            await self.server.serve()

        except asyncio.CancelledError:
            if not self._stop_requested:
                logger.info(f"{colorama.Fore.YELLOW}Stopping FastAPI server gracefully...")
                await self.stop()
                

    async def stop(self):
        self._stop_requested = True
        if self.server:
            self.server.should_exit = True
            
            if hasattr(self.server, "servers"):
                for server in self.server.servers:
                    server.close()
            
            logger.info(f"{colorama.Fore.GREEN}FastAPI server stopped")
            await self.server.shutdown()
