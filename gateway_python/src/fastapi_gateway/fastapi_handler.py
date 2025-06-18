from src.core.config import ConfigLoader
from loguru import logger
from fastapi import APIRouter, FastAPI


class FastApiHandler():
    def __init__(self, app: FastAPI) -> None:
        self.config = ConfigLoader()
        self.app = app
        self.router = APIRouter()


    def register_routes(self) -> None:
        self.router.add_api_route("/", self.root, methods=["GET"])

        self.app.include_router(self.router)


    async def root(self) -> None:
        return "Hello World!"