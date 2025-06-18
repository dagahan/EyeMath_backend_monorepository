import sys

import colorama
from loguru import logger

sys.path.insert(0, "./gen")  # Fix of relative import in generated stubs
from src.core.config import ConfigLoader
from src.core.logging import InterceptHandler, LogSetup
from src.fastapi_gateway.gateway import GatewayServer


class Service:
    def __init__(self):
        self.config = ConfigLoader()
        self.intercept_handler = InterceptHandler()
        self.logger_setup = LogSetup()
        self.gateway = GatewayServer()
        self.service_name = self.config.get("project", "name")
        self.show_params_on_start = self.config.get("project", "show_params_on_run")


    def service_start_message(self):
        match self.show_params_on_start:
            case True:
                from tabulate import tabulate

                table = self.config["fastapi_server"]
                table.update(self.config["grpc_client"])

                logger.info(f"""{colorama.Fore.CYAN}{self.service_name} started with configuration parameters:\n
                {colorama.Fore.GREEN}{tabulate([table], headers="keys", tablefmt="grid")}""")

            case False:
                (logger.info(f"{colorama.Fore.CYAN}{self.service_name} starting..."))


    def run_service(self):
        self.logger_setup.configure()
        self.service_start_message()
        self.gateway.run_gateway()


if __name__ == "__main__":
    try:
        mathsolve = Service()
        mathsolve.run_service()
    except KeyboardInterrupt:
        logger.info(f"{colorama.Fore.CYAN}Service stopped by user")
    except Exception as error:
        logger.critical(f"{colorama.Fore.RED}Service crashed: {error}")
        sys.exit(1)
