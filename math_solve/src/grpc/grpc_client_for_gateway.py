import colorama
import grpc
from loguru import logger

from typing import Any, Type

import gen.gateway_pb2 as gateway_pb
import gen.gateway_pb2_grpc as gateway_rpc
from src.core.config import ConfigLoader
from src.core.utils import EnvTools


class GatewayClientGRPC:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.gateway_host = EnvTools.load_env_var("GATEWAY_HOST")
        self.gateway_port = EnvTools.load_env_var("GATEWAY_APP_PORT")
        self.request_types = {
            "register": gateway_pb.register_request,
            "login": gateway_pb.login_request,
            "is_admin": gateway_pb.is_admin_request
        }


    def _create_grpc_connection(self, host: int, port: int) -> grpc.Channel:
        return grpc.insecure_channel(f'{host}:{port}')
    

    def get_rpc_stub(self, rpc_class: Type[Any], connection_channel: grpc.Channel) -> Any:
        return rpc_class.ExternalApiGatewayStub(connection_channel)
    

    def _is_stub_has_method(self, stub: Any, method_name: str) -> bool:
        return hasattr(stub, method_name)
    

    def call_rpc_method(
        self, 
        method_name: str, 
        **kwargs
    ) -> Any:
        '''
        Универсальный метод для вызова gRPC методов
        
        :param method_name: Имя RPC метода (например 'is_admin')
        :param response_class: Класс ответа (для type hinting)
        :param kwargs: Аргументы для создания запроса
        :return: Ответ сервера
        '''
        if method_name not in self.request_types:
            logger.error(f"Method {method_name} not supported")
            return None
        
        
        
        with self._create_grpc_connection(self.gateway_host, self.gateway_port) as channel:
            request_class = self.request_types[method_name]
            request = request_class(**kwargs)

            stub = gateway_rpc.ExternalApiGatewayStub(channel)
            
            if not self._is_stub_has_method(stub, method_name):
                logger.error(f"Method {method_name} not found in gRPC service")
                return None
            
            try:
                logger.debug(f"Calling method {method_name} in gRPC service...")
                method = getattr(stub, method_name)
                return method(request)
            except grpc.RpcError as e:
                logger.error(f"gRPC call failed: {e.details()}")
                return None