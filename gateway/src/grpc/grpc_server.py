import asyncio
from concurrent import futures

import colorama
from loguru import logger

import gen.gateway_pb2 as gateway_pb
import gen.gateway_pb2_grpc as gateway_rpc
import grpc
from src.core.config import ConfigLoader
from src.core.logging import LogAPI
from src.core.utils import EnvTools


class GRPCGateway(gateway_rpc.ExternalApiGateway):
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.env_tools = EnvTools()
        self.log_api = LogAPI()
        self.project_name = self.config.get("project", "name")
        self.project_version = self.config.get("project", "version")


    @logger.catch
    def is_admin(self, request: gateway_pb.is_admin_request, context) -> gateway_pb.is_admin_response:
        '''
        This endpoint just returns metadata of service.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            response = gateway_pb.is_admin_response(
                is_admin = True,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return gateway_pb.is_admin_response()


class GRPCServerRunner:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.grpc_math_recognize = GRPCGateway()
        self.max_workers = self.config.get("grpc_server", "max_workers")
        self.host = EnvTools.load_env_var("GATEWAY_GRPC_HOST")
        self.port = EnvTools.load_env_var("GATEWAY_GRPC_APP_PORT")
        self.addr = f"{self.host}:{self.port}"
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        self._stop_event = asyncio.Event()


    async def run_grpc_server(self) -> None:
        gateway_rpc.add_ExternalApiGatewayServicer_to_server(GRPCGateway(), self.grpc_server)
        self.grpc_server.add_insecure_port(self.addr)
        logger.info(f"{colorama.Fore.GREEN}gRPC server of {self.grpc_math_recognize.project_name} has been started on {colorama.Fore.YELLOW}({self.addr})")
        self.grpc_server.start()

        try:
            await self._stop_event.wait()

        except asyncio.CancelledError:
            await self._graceful_stop()
            logger.info(f"{colorama.Fore.GREEN}gRPC server stopped")


    async def _graceful_stop(self):
        '''
        Graceful async stopp of the gRPC server.
        '''
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.grpc_server.stop, 5)
        await loop.run_in_executor(None, self.grpc_server.wait_for_termination, 5)


    def stop(self):
        self._stop_event.set()

