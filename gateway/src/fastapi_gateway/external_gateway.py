from src.core.config import ConfigLoader

from loguru import logger
from typing import List
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

import uvicorn
import strawberry
import colorama
import asyncio



# Выносим типы GraphQL из класса
@strawberry.type
class Book:
    id: int
    title: str
    author: str

@strawberry.type
class Car:
    id: int
    brand: str
    model: str
    year: int = strawberry.field(description="Год выпуска")



class GatewayServer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.gateway_app = FastAPI()
        self.gateway_app.include_router(self.create_graphql_router(), prefix="/graphql")
        self.server = None
        self._stop_requested = False


    # Основной класс запросов
    @strawberry.type
    class Query:
        @strawberry.field(description="Получить список книг")
        def books(self) -> List[Book]:
            return [
                Book(id=1, title="Гарри Поттер", author="Дж. К. Роулинг"),
                Book(id=2, title="Властелин Колец", author="Дж. Р. Р. Толкин"),
                Book(id=3, title="Test Test", author="Usov Nikita"),
            ]
        
        @strawberry.field(description="Получить автомобиль по ID")
        def car(self, id: int) -> Car:
            return Car(
                id=id,
                brand="Tesla",
                model="Model S",
                year=2023
            )


    # Класс мутаций
    @strawberry.type
    class Mutation:
        @strawberry.mutation(description="Добавить новую книгу")
        async def add_book(self, title: str, author: str) -> Book:
            return await Book(id=3, title=title, author=author)
        
        @strawberry.mutation(description="Добавить автомобиль")
        async def add_car(self, brand: str, model: str, year: int) -> Car:
            return await Car(id=4, brand=brand, model=model, year=year)


    def create_graphql_router(self) -> GraphQLRouter:
        # Объединяем Query и Mutation в одну схему
        schema = strawberry.Schema(
            query=self.Query, 
            mutation=self.Mutation
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