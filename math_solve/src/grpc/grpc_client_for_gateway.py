import colorama
import grpc
from loguru import logger

from abc import ABC
from typing import Any

import gen.gateway_pb2 as gateway_pb
import gen.gateway_pb2_grpc as gateway_rpc
from src.core.config import ConfigLoader
from src.core.utils import EnvTools


class GatewayClientGRPC(ABC):
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.gateway_host = EnvTools.load_env_var("GATEWAY_HOST")
        self.gateway_port = EnvTools.load_env_var("GATEWAY_APP_PORT")
        # self.request_types = {
        #     "register": gateway_pb.register_request,
        #     "login": gateway_pb.login_request,
        #     "is_admin": gateway_pb.is_admin_request
        # }

        self.addrs = {
            "gateway": f'{self.gateway_host}:{self.gateway_port}'
        }

        self.endpoints = {
            "is_admin":
                {
                    "method": gateway_pb.is_admin_request,
                    "connection": self._create_grpc_connection(self.addrs["gateway"])
                },

            "is_admin":
                {
                    "method": gateway_pb.is_admin_request,
                    "connection": self._create_grpc_connection(self.addrs["gateway"])
                },
        }


    def _create_grpc_connection(self, addr: str) -> grpc.Channel:
        return grpc.insecure_channel(addr)
    

    def _is_stub_has_method(self, stub: Any, method_name: str) -> bool:
        return hasattr(stub, method_name)
    

    def call_grpc_endpoint(
        self, 
        method_name: str, 
        **arguments
    ) -> Any:
        '''
        universal method to call gRPC endpoints.
        :param method_name: name of an RPC method.
        :param kwargs: arguments for an RPC method.
        returns a server's response.
        '''
        if method_name not in self.endpoints:
            logger.critical(f"Method {method_name} not supported!")
            return None

        endpoint_config = self.endpoints[method_name]
        request_method = endpoint_config["method"]
        stub_connection = endpoint_config["connection"]
        arguments = request_method(**arguments)

        stub = gateway_rpc.ExternalApiGatewayStub(stub_connection)
        
        if not self._is_stub_has_method(stub, method_name):
            logger.error(f"Method {method_name} not found in gRPC service")
            return None
        
        try:
            logger.debug(f"Calling method {method_name} in gRPC service.")
            method = getattr(stub, method_name)
            return method(arguments)
        
        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.details()}")
            return None