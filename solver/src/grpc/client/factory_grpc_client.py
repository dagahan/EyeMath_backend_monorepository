from typing import Any, Dict, Type

from loguru import logger

import grpc
from grpc import StatusCode
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
    _registered_services = set()
    _error_threshold = 1  # Max errors before client removal
    _error_counts = {}


    @classmethod
    def _is_service_registered(cls, service_name: str) -> bool:
        return service_name in cls._registered_services
    
    
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
        if cls._is_service_registered(service_name):
            return
            
        cls._configs[service_name] = {
            'host': host,
            'port': port,
            'stub_class': stub_class,
            'method_map': method_map
        }

        cls._registered_services.add(service_name)
        logger.debug(f"Registered new grpc client '{service_name}' with method_map {method_map} at {host}:{port}")


    @classmethod
    def _create_client(cls, service_name: str) -> GRPCClient:
        '''
        Create a client instance from configuration
        '''
        if not cls._is_service_registered(service_name):
            raise ValueError(f"Service {service_name} not registered")
        
        config = cls._configs[service_name]
        client = GRPCClient(
            host=config['host'],
            port=config['port'],
            stub_class=config['stub_class'],
            method_map=config['method_map']
        )

        cls._clients[service_name] = client
        logger.debug(f"Created gRPC client for service '{service_name}'")
        return client
    

    @classmethod
    def _handle_client_error(cls, service_name: str, error: Exception):
        '''
        Handle connection errors and reset clients if needed
        '''
        if service_name not in cls._error_counts:
            cls._error_counts[service_name] = 0
            
        cls._error_counts[service_name] += 1
        logger.warning(f"Client error for '{service_name}' (count: {cls._error_counts[service_name]}/{cls._error_threshold})")
        
        if cls._error_counts[service_name] >= cls._error_threshold:
            if service_name in cls._clients:
                del cls._clients[service_name]
                logger.warning(f"Removed client for '{service_name}' due to repeated errors")
            cls._error_counts[service_name] = 0
    

    @classmethod
    def get_client(cls, service_name: str) -> GRPCClient:
        if service_name not in cls._clients:
            return cls._create_client(service_name)
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
        try:
            client = cls.get_client(service_name)
            return client.call_method(method_name, **kwargs)
        
        except grpc.RpcError as e:
            # Handle specific connection errors
            if e.code() in [StatusCode.UNAVAILABLE, StatusCode.DEADLINE_EXCEEDED]:
                cls._handle_client_error(service_name, e)
            
            logger.error(f"gRPC call failed: {e.details()}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in RPC call: {e}")
            raise
