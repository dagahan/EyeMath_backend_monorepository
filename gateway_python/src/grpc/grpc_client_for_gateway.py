import colorama
import grpc
from loguru import logger

from typing import Any, Type

import gen.external_api_gateway_pb2 as external_api_gateway_pb
import gen.external_api_gateway_pb2_grpc as external_api_gateway_rpc
from src.core.config import ConfigLoader
from src.core.utils import EnvTools


class GatewayClientGRPC:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.gateway_host = EnvTools.load_env_var("GATEWAY_APP_HOST")
        self.gateway_port = EnvTools.load_env_var("GATEWAY_APP_PORT")


    def _create_grpc_connection(self) -> grpc.Channel:
        return grpc.insecure_channel(f'{self.gateway_host}:{self.gateway_port}')
    

    def get_rpc_stub(self, rpc_class: Type[Any], connection_channel) -> Any:
        return rpc_class.ExternalApiGatewayStub(connection_channel)
    

    def _is_stub_has_method(self, stub: Any, method_name: str) -> bool:
        if not hasattr(stub, method_name):
            return False
        return True
    

    def call_rpc_method(
        self, 
        method_name: str, 
        # request_class: Type[Any],
        **kwargs
    ) -> Any:
        '''
        Универсальный метод для вызова gRPC методов
        
        :param method_name: Имя RPC метода (например 'is_admin')
        :param request_class: Класс запроса (например external_api_gateway_pb.is_admin_request)
        :param response_class: Класс ответа (для type hinting)
        :param kwargs: Аргументы для создания запроса
        :return: Ответ сервера
        '''
        with self._create_grpc_connection() as channel:
            print(type(channel).__name__)
            logger.debug(f"Calling method {method_name} in gRPC service...")
            stub = self.get_rpc_stub(external_api_gateway_rpc, channel)
            print(type(stub).__name__)
            
            if not self._is_stub_has_method(stub, method_name):
                logger.error(f"Method {method_name} not found in gRPC service")
                return None
            
            request = external_api_gateway_pb(**kwargs)
            method = getattr(stub, method_name)
            return method(request)