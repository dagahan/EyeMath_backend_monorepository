import asyncio
from concurrent import futures
from typing import Any

import colorama
from loguru import logger

from stubs import authorizer_pb2 as authorizer_pb
from stubs import authorizer_pb2_grpc as authorizer_rpc
import grpc
from grpc_reflection.v1alpha import reflection

from src.services.authorizer import Authorizer
from src.core.config import ConfigLoader
from src.core.logging import LogAPI
from src.core.utils import EnvTools


class GRPCAuthorizer(authorizer_rpc.GRPCAuthorizer):
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.env_tools = EnvTools()
        self.log_api = LogAPI()
        self.authorizer = Authorizer()
        self.project_name = self.config.get("project", "name")
        self.project_version = self.config.get("project", "version")


    @logger.catch
    def meta_data(self, request: authorizer_pb.meta_data_authorizer_request, context) -> authorizer_pb.meta_data_authorizer_response:
        '''
        This endpoint just returns metadata of service.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            response = authorizer_pb.meta_data_authorizer_response(
                name = self.project_name,
                version = self.project_version,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return authorizer_pb.meta_data_authorizer_response()
        

    @logger.catch
    def register(self, request: authorizer_pb.register_request, context) -> authorizer_pb.register_response:
        '''
        This endpoint register a new user.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            authorizer_response = self.authorizer.register_user(
                request.user_name,
                request.password,
                request.email,
                )
            
            response = authorizer_pb.register_response(
                result=authorizer_response['result'],
                description=authorizer_response['description'],
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Register user error: {error}")
            return authorizer_pb.register_response()
        

    @logger.catch
    def authorize(self, request: authorizer_pb.authorize_request, context) -> authorizer_pb.authorize_response:
        '''
        This endpoint authorize through with credits.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            authorizer_response = self.authorizer.authorize_user(
                request.user_name,
                request.password,
                )
            
            response = authorizer_pb.authorize_response(
                result=authorizer_response['result'],
                token=authorizer_response['token'],
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Authorize user error: {error}")
            return authorizer_pb.authorize_response()
        
    
    @logger.catch
    def unauthorize(self, request: authorizer_pb.unauthorize_request, context) -> authorizer_pb.unauthorize_response:
        '''
        This endpoint unauthorize through with credits.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            authorizer_response = self.authorizer.unauthorize_user(
                request.token,
                )
            
            response = authorizer_pb.unauthorize_response(
                result=authorizer_response['result'],
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Authorize user error: {error}")
            return authorizer_pb.unauthorize_response()
        

    @logger.catch
    def validate_jwt(self, request: authorizer_pb.validate_jwt_request, context) -> authorizer_pb.validate_jwt_response:
        '''
        This endpoint validates jwt token.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            authorizer_response = self.authorizer.token_validation(
                request.token,
                )
            
            response = authorizer_pb.validate_jwt_response(
                result=authorizer_response['result'],
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Token validation error: {error}")
            return authorizer_pb.validate_jwt_response()


class GRPCServerRunner:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.grpc_authorizer = GRPCAuthorizer()
        self.max_workers = self.config.get("grpc_server", "max_workers")
        self.host = EnvTools.load_env_var("AUTHORIZER_HOST")
        self.port = EnvTools.load_env_var("AUTHORIZER_APP_PORT")
        self.addr = f"{self.host}:{self.port}"
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        self._stop_event = asyncio.Event()


    async def run_grpc_server(self) -> None:
        authorizer_rpc.add_GRPCAuthorizerServicer_to_server(GRPCAuthorizer(), self.grpc_server)
        self.grpc_server.add_insecure_port(self.addr)
        logger.info(f"{colorama.Fore.GREEN}gRPC server of {self.grpc_authorizer.project_name} has been started on {colorama.Fore.YELLOW}({self.addr})")
        if EnvTools.load_env_var("AUTHORIZER_REFLECTIONS") == "1":
            self.enable_reflections_grpc_server(authorizer_pb, self.grpc_server)
        self.grpc_server.start()

        try:
            await self._stop_event.wait()

        except asyncio.CancelledError:
            await self._graceful_stop()
            logger.info(f"{colorama.Fore.GREEN}gRPC server stopped")

        
    def enable_reflections_grpc_server(self, stub: Any, grpc_server: grpc.server) -> None:
        '''
        Enable gRPC reflection for the service
        '''
        try:
            service_name = stub.DESCRIPTOR.services_by_name['GRPCAuthorizer'].full_name
            SERVICE_NAMES = (
                service_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, grpc_server)
            logger.warning(f"Enabled reflections for the grpc server: '{service_name}'")
        except Exception as ex:
            logger.critical(f"Unable to enable reflections for the {grpc_server} with stub {stub}: {ex}")
        

    async def _graceful_stop(self):
        '''
        Graceful async stopp of the gRPC server.
        '''
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.grpc_server.stop, 5)
        await loop.run_in_executor(None, self.grpc_server.wait_for_termination, 5)


    def stop(self):
        self._stop_event.set()

