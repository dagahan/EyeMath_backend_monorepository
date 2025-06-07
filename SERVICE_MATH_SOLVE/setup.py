import sys, colorama
from loguru import logger

from src.core.config import ConfigLoader
from src.services.logging import InterceptHandler, LogSetup
from src.services.grpc_server import gRPC_Server_Runner




class service:
    def __init__(self):
        self.config = ConfigLoader()
        self.intercept_handler = InterceptHandler()
        self.logger_setup = LogSetup()
        self.grpc_server_runner = gRPC_Server_Runner()
        self.service_name = self.config.get("project", "name")
        self.show_params_on_start = self.config.get("project", "show_params_on_run")

    
    def service_start_message(self):
        match self.show_params_on_start:
            case True:
                from tabulate import tabulate
                table = self.config["MaL"]
                table.update(self.config["grpc_server"])
            
                logger.info(f"""{colorama.Fore.CYAN}{self.service_name} started with parameters:\n
                {colorama.Fore.GREEN}{tabulate([table], headers="keys", tablefmt="grid")}""")

            case default:
                (logger.info(f"{colorama.Fore.CYAN}{self.service_name} starting..."))


    def run_service(self):
        self.logger_setup.configure()
        self.service_start_message()
        self.grpc_server_runner.run_grpc_server()



if __name__ == "__main__":
    try:
        mathsolve = service()
        mathsolve.run_service()
    except KeyboardInterrupt:
        logger.info(f"{colorama.Fore.CYAN}Service stopped by user")
    except Exception as error:
        logger.critical(f"{colorama.Fore.RED}Service crashed: {error}")
        sys.exit(1)