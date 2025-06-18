from src.grpc.client.factory_grpc_client import GRPCClientFactory
from loguru import logger
from src.core.utils import EnvTools

import gen.gateway_pb2 as gateway_pb
import gen.gateway_pb2_grpc as gateway_rpc



class RegistryGrpcMethods:
    @classmethod
    def pull_actual_grpc_methods(cls):
        pass


    @classmethod
    def register_service_with_methods(cls):

        service_name="gateway"
        host=EnvTools.load_env_var("GATEWAY_GRPC_HOST")
        port=EnvTools.load_env_var("GATEWAY_GRPC_APP_PORT")
        stub_class=gateway_rpc.ExternalApiGatewayStub
        method_map={
                "is_admin": gateway_pb.is_admin_request,
                "login": gateway_pb.login_request,
                "register": gateway_pb.register_request
            }


        GRPCClientFactory.register_service(
            service_name=service_name,
            host=host,
            port=port,
            stub_class=stub_class,
            method_map=method_map
        )