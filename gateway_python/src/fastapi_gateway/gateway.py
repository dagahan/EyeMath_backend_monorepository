from src.core.config import ConfigLoader
from src.fastapi_gateway.fastapi_handler import FastApiHandler

from loguru import logger
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

import uvicorn
import strawberry



class GatewayServer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.app = FastAPI()
        self.fast_api_handler = FastApiHandler(self.app)
        self.app.include_router(self.create_graphql_router(), prefix="/graphql")
        

    def create_graphql_router(self) -> GraphQLRouter:
        @strawberry.type
        class Query:
            @strawberry.field
            def hello(self) -> str:
                return "Hello from GraphQL!"
        
        schema = strawberry.Schema(Query)
        return GraphQLRouter(schema)
    
    
    def run_gateway(self):
        host = self.config.get("fastapi_server", "host")
        port = self.config.get("fastapi_server", "port")
        
        logger.info(f"Starting gateway on {host}:{port}")
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )