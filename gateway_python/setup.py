import sys
import asyncio
import colorama

from loguru import logger

sys.path.insert(0, "./gen")  # Fix of relative import in generated stubs
from src.core.config import ConfigLoader
from src.core.logging import InterceptHandler, LogSetup
from src.fastapi_gateway.external_gateway import GatewayServer
from src.grpc.grpc_server import GRPCServerRunner


class Service:
    def __init__(self):
        self.config = ConfigLoader()
        self.intercept_handler = InterceptHandler()
        self.logger_setup = LogSetup()
        self.gateway = GatewayServer()
        self.grpc_server_runner = GRPCServerRunner()
        self.service_name = self.config.get("project", "name")
        self.show_params_on_start = self.config.get("project", "show_params_on_run")


    def service_start_message(self):
        match self.show_params_on_start:
            case True:
                from tabulate import tabulate

                table = self.config["fastapi_server"]
                table = self.config["grpc_server"]

                logger.info(f"""{colorama.Fore.CYAN}{self.service_name} started with configuration parameters:\n
                {colorama.Fore.GREEN}{tabulate([table], headers="keys", tablefmt="grid")}""")

            case False:
                (logger.info(f"{colorama.Fore.CYAN}{self.service_name} starting..."))


    async def run_service(self):
        self.logger_setup.configure()
        self.service_start_message()
        
        pending = set()
        
        try:
            # Создаем задачи для серверов
            gateway_task = asyncio.create_task(self.gateway.run_external_gateway(), name="FastAPI")
            grpc_task = asyncio.create_task(self.grpc_server_runner.run_grpc_server(), name="gRPC")
            pending = {gateway_task, grpc_task}
            
            # Ожидаем завершения любой из задач
            done, pending = await asyncio.wait(
                pending,
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Логируем причину остановки
            for task in done:
                if task.exception():
                    logger.error(f"{colorama.Fore.RED}{task.get_name()} server crashed: {task.exception()}")
        except asyncio.CancelledError:
            logger.info(f"{colorama.Fore.YELLOW}Service stop requested")
        
        finally:
            if hasattr(self.gateway, 'server') and self.gateway.server:
                logger.info(f"{colorama.Fore.YELLOW}Stopping FastAPI server gracefully...")
                await self.gateway.stop()
                
            if hasattr(self.grpc_server_runner, '_stop_event'):
                logger.info(f"{colorama.Fore.YELLOW}Stopping gRPC server gracefully...")
                self.grpc_server_runner.stop()
            
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