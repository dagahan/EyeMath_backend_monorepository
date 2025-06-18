from src.core.config import ConfigLoader
from src.fastapi_gateway.fastapi_handler import FastApiHandler
from loguru import logger
from fastapi import FastAPI
import uvicorn


class GatewayServer:
    def __init__(self):
        self.config = ConfigLoader()
        self.app = FastAPI()
        self.fast_api_handler = FastApiHandler(self.app)
        self.fast_api_handler.register_routes()
        

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