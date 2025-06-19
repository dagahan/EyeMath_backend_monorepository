from src.core.config import ConfigLoader

from loguru import logger
from typing import List, Any
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.grpc.client.factory_grpc_client import GRPCClientFactory

import uvicorn
import strawberry
import colorama
import asyncio


# TODO: gRPC responce type auto-convertor to graphql type.


@strawberry.type
class MathSolution:
    results: List[str]
    solving_steps: List[str] | None = strawberry.field(description="Шаги решения")


class GatewayServer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.gateway_app = FastAPI()
        self.gateway_app.include_router(self.create_graphql_router(), prefix="/graphql")
        self.server = None
        self._stop_requested = False


    @strawberry.type
    class Query:
        @strawberry.field(description="Решить математическое выражение")
        def solve_math(self, 
        latex_expression: str = "6x^{2} - 17x + 12 = 0",
        show_solving_steps: bool = True,
        render_latex_expressions: bool = False,
        ) -> MathSolution:
            
            response = GRPCClientFactory.rpc_call(
                service_name="math_solve",
                method_name="solve",
                latex_expression=latex_expression,
                show_solving_steps=show_solving_steps,
                render_latex_expressions=render_latex_expressions
            )
            
            # Преобразование gRPC ответа в GraphQL тип
            return MathSolution(
                results=response.results,
                solving_steps=response.solving_steps
            )


    def create_graphql_router(self) -> GraphQLRouter:
        schema = strawberry.Schema(
            query=self.Query
        )
        return GraphQLRouter(schema)
    
    
    async def run_external_gateway(self):
        host = self.config.get("fastapi_server", "fastapi_host")
        port = int(self.config.get("fastapi_server", "fastapi_port"))
        
        config = uvicorn.Config(
            app=self.gateway_app,
            host=host,
            port=port,
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
            logger.info(f"{colorama.Fore.GREEN}Starting FastAPI on {colorama.Fore.YELLOW}http://{host}:{port}/graphql")
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