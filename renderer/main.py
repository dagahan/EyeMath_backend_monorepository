import asyncio
import sys

import colorama
from loguru import logger

from src.core.config import ConfigLoader
from src.core.logging import InterceptHandler, LogSetup
from src.services.fastapi_server import Server


class Service:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.intercept_handler = InterceptHandler()
        self.logger_setup = LogSetup()
        self.fastapi_server = Server()
        self.service_name = self.config.get("project", "name")


    async def run_service(self) -> None:
        self.logger_setup.configure()
        
        pending = set()
        
        try:
            renderer_task = asyncio.create_task(self.fastapi_server.run_server(), name="FastAPI")
            pending = {renderer_task}
            
            done, pending = await asyncio.wait(
                pending,
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in done:
                if task.exception():
                    logger.error(f"{colorama.Fore.RED}{task.get_name()} server crashed: {task.exception()}")
        except asyncio.CancelledError:
            logger.info(f"{colorama.Fore.YELLOW}Service stop requested")
        
        finally:
            if hasattr(self.fastapi_server, 'server'):
                logger.info(f"{colorama.Fore.YELLOW}Stopping FastAPI server gracefully...")
                await self.fastapi_server.stop()
                
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error stopping task: {e}")
            
            logger.info(f"{colorama.Fore.GREEN}All servers stopped gracefully")


if __name__ == "__main__":
    try:
        service = Service()
        asyncio.run(service.run_service())
    except KeyboardInterrupt:
        logger.info(f"{colorama.Fore.CYAN}Service stopped by user")
    except Exception as error:
        logger.critical(f"{colorama.Fore.RED}Service crashed: {error}")
        sys.exit(1)
