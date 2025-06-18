from typing import Dict, Type, Any, Callable
from loguru import logger

from src.grpc.client.base_grpc_client import GRPCClient


class GRPCClientFactory:
    '''
    Factory for creating and caching gRPC clients.
    If you have created a client for the specified gRPC server
    it will contain an open gprs connection to the server until
    the program shuts down.
    One client created for one gRPC server.
    '''
    _clients = {}
    _configs = {}


    @classmethod
    def _is_client_already_registered(cls, service_name: str) -> bool:
        return service_name in cls._clients
    
    
    @classmethod
    def register_service(
        cls, 
        service_name: str,
        host: str,
        port: int,
        stub_class: Type,
        method_map: Dict[str, Type]
    ):
        '''
        register new grpc service with specific client and list of methods to invoke.
        '''
        if cls._is_client_already_registered(service_name):
            return
            
        cls._configs[service_name] = {
            'host': host,
            'port': port,
            'stub_class': stub_class,
            'method_map': method_map
        }

        logger.debug(f"Registered new grpc client '{service_name}' with method_map {method_map} at {host}:{port}")
    

    @classmethod
    def get_client(cls, service_name: str) -> GRPCClient:
        if service_name not in cls._clients:
            raise ValueError(f"Service {service_name} not registered")
        
        return cls._clients[service_name]
    

    @classmethod
    def rpc_call(
        cls,
        service_name: str,
        method_name: str,
        **kwargs
    ) -> Any:
        '''
        Universally calling the rpc method on the gRPC server.
        '''
        client = cls.get_client(service_name)
        return client.call_method(method_name, **kwargs)