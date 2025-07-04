import asyncio

import colorama
import uvicorn
from fastapi import FastAPI
from loguru import logger

from strawberry.fastapi import GraphQLRouter
from strawberry import Schema

from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.external_gateway.graphql.queries.queries import Query
from src.external_gateway.graphql.mutations.mutations import Mutation


class ExternalGatewayServer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.gateway_app = FastAPI()
        self.host = EnvTools.load_env_var("GATEWAY_HOST")
        self.port = EnvTools.load_env_var("GATEWAY_APP_PORT")
        self.schema = Schema(
            query=Query,
            mutation=Mutation
        )
        graphql_router = GraphQLRouter(self.schema)
        self.gateway_app.include_router(graphql_router, prefix="/graphql")
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


    # def enable_introspection_graphql_server(self, grpc_server: grpc.server) -> None:
    #     '''
    #     Enable gRPC reflection for the service
    #     '''
    #     try:
    #         service_name = stub.DESCRIPTOR.services_by_name['ExternalApiGateway'].full_name
    #         SERVICE_NAMES = (
    #             service_name,
    #             reflection.SERVICE_NAME,
    #         )
    #         reflection.enable_server_reflection(SERVICE_NAMES, grpc_server)
    #         logger.warning(f"Enabled reflections for the grpc server: '{service_name}'")
    #     except Exception as ex:
    #         logger.critical(f"Unable to enable reflections for the {grpc_server} with stub {stub}: {ex}")


    async def stop(self):
        self._stop_requested = True
        if self.server:
            self.server.should_exit = True
            
            if hasattr(self.server, "servers"):
                for server in self.server.servers:
                    server.close()
            
            logger.info(f"{colorama.Fore.GREEN}FastAPI server stopped")
            await self.server.shutdown()
