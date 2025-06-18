from src.core.config import ConfigLoader
from loguru import logger
from fastapi import FastAPI



class GatewayServer:
    def __init__(self):
        self.config = ConfigLoader()
        

    def run_gateway(self):
        logger.debug("helloo!!!")