import sys

import colorama
from loguru import logger

sys.path.insert(0, './gen') #Fix of relative import in generated stubs
from src.core.config import ConfigLoader
from src.services.grpc_server import GRPCServerRunner
from src.core.logging import InterceptHandler, LogSetup


class Service:
    def __init__(self):
        self.config = ConfigLoader()
        self.intercept_handler = InterceptHandler()
        self.logger_setup = LogSetup()
        self.grpc_server_runner = GRPCServerRunner()
        self.service_name = self.config.get("project", "name")
        self.show_params_on_start = self.config.get("project", "show_params_on_run")


    def service_start_message(self) -> None:
        match self.show_params_on_start:
            case True:
                from tabulate import tabulate
                table = self.config["MaL"]
                table.update(self.config["grpc_server"])

                logger.info(f"""{colorama.Fore.CYAN}{self.service_name} started with configuration parameters:\n
                {colorama.Fore.GREEN}{tabulate([table], headers="keys", tablefmt="grid")}""")

            case False:
                (logger.info(f"{colorama.Fore.CYAN}{self.service_name} starting..."))


    def run_service(self) -> None:
        self.logger_setup.configure()
        self.service_start_message()
        self.grpc_server_runner.run_grpc_server()



if __name__ == "__main__":
    try:
        mathsolve = Service()
        mathsolve.run_service()
    except KeyboardInterrupt:
        logger.info(f"{colorama.Fore.CYAN}Service stopped by user")
    except Exception as error:
        logger.critical(f"{colorama.Fore.RED}Service crashed: {error}")
        sys.exit(1)
