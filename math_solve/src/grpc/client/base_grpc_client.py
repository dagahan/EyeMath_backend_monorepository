from typing import Any, Dict, Type

from loguru import logger

import grpc


class GRPCClient:
    '''
    universal client to call gRPC endpoints.
    '''
    _instances = {}
    
    def __init__(
        self,
        host: str,
        port: int,
        stub_class: Type,
        method_map: Dict[str, Type]
    ):
        '''
        :param host: host of the service.
        :param port: port of the service.
        :param stub_class: class of stub from the gRPC server.
        :param method_map: availiable methods on gRPC server.
        returns a server's response.
        '''
        self.addr = f"{host}:{port}"
        self.stub_class = stub_class
        self.method_map = method_map
        self._channel = None
        self._stub = None
        

    @property
    def init_channel(self) -> grpc.Channel:
        if self._channel is None or self._channel._channel.is_closed():
            self._channel = grpc.insecure_channel(self.addr)
        return self._channel
    

    @property
    def stub(self):
        if self._stub is None:
            self._stub = self.stub_class(self.init_channel)
        return self._stub
    
    
    def call_method(self, method_name: str, **kwargs) -> Any:
        '''
        calling the rpc method with arguments on specified gRPC server.
        '''
        request_class = self.method_map.get(method_name)

        if not request_class:
            raise ValueError(f"Unsupported method: {method_name}")
        if not hasattr(self.stub, method_name):
            raise AttributeError(f"Method {method_name} not found in service")
        
        request_with_arguments = request_class(**kwargs)
        
        try:
            method = getattr(self.stub, method_name)
            return method(request_with_arguments)
        
        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.details()}")
            raise
