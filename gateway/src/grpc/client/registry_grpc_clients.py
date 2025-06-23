
from stubs import gateway_pb2 as gateway_pb
from stubs import gateway_pb2_grpc as gateway_rpc
from stubs import service_math_recognize_pb2 as math_recognize_pb
from stubs import service_math_recognize_pb2_grpc as math_recognize_rpc
from stubs import service_math_render_pb2 as math_render_pb
from stubs import service_math_render_pb2_grpc as math_render_rpc
from stubs import service_math_solve_pb2 as math_solve_pb
from stubs import service_math_solve_pb2_grpc as math_solve_rpc
from stubs import authorizer_pb2 as authorizer_pb
from stubs import authorizer_pb2_grpc as authorizer_rpc
from src.core.utils import EnvTools
from src.grpc.client.factory_grpc_client import GRPCClientFactory


class RegistryGrpcMethods:
    @classmethod
    def _is_server_local(cls, server_adress: str) -> bool:
        return server_adress == "0.0.0.0"


    @classmethod
    def register_service_with_methods(cls):
        service_name="gateway"
        host=EnvTools.load_env_var("GATEWAY_GRPC_HOST")
        port=EnvTools.load_env_var("GATEWAY_GRPC_APP_PORT")
        if EnvTools.is_running_inside_docker() and cls._is_server_local(host):
            host=service_name
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


        service_name="authorizer"
        host=EnvTools.load_env_var("AUTHORIZER_HOST")
        port=EnvTools.load_env_var("AUTHORIZER_APP_PORT")
        if EnvTools.is_running_inside_docker() and cls._is_server_local(host):
            host=service_name
        stub_class=authorizer_rpc.GRPCAuthorizerStub
        method_map={
                "meta_data_authorizer": authorizer_pb.meta_data_authorizer_request,
                "register": authorizer_pb.register_request,
                "authorize": authorizer_pb.authorize_request,
                "validate_jwt": authorizer_pb.validate_jwt_request,
            }
        
        GRPCClientFactory.register_service(
            service_name=service_name,
            host=host,
            port=port,
            stub_class=stub_class,
            method_map=method_map
        )


        service_name="solver"
        host=EnvTools.load_env_var("SOLVER_HOST")
        port=EnvTools.load_env_var("SOLVER_APP_PORT")
        if EnvTools.is_running_inside_docker() and cls._is_server_local(host):
            host=service_name
        stub_class=math_solve_rpc.GRPCMathSolveStub
        method_map={
                "meta_data_solve": math_solve_pb.meta_data_solve_request,
                "solve": math_solve_pb.solve_request,
            }
        
        GRPCClientFactory.register_service(
            service_name=service_name,
            host=host,
            port=port,
            stub_class=stub_class,
            method_map=method_map
        )


        service_name="recognizer"
        host=EnvTools.load_env_var("RECOGNIZER_HOST")
        port=EnvTools.load_env_var("RECOGNIZER_APP_PORT")
        if EnvTools.is_running_inside_docker() and cls._is_server_local(host):
            host=service_name
        stub_class=math_recognize_rpc.GRPCMathRecognizeStub
        method_map={
                "meta_data_recognize": math_recognize_pb.meta_data_recognize_request,
                "recognize": math_recognize_pb.recognize_request,
                "normalize_for_sympy": math_recognize_pb.normalize_for_sympy_request,
            }
        
        GRPCClientFactory.register_service(
            service_name=service_name,
            host=host,
            port=port,
            stub_class=stub_class,
            method_map=method_map
        )


        service_name="renderer"
        host=EnvTools.load_env_var("RENDERER_HOST")
        port=EnvTools.load_env_var("RENDERER_APP_PORT")
        if EnvTools.is_running_inside_docker() and cls._is_server_local(host):
            host=service_name
        stub_class=math_render_rpc.GRPCMathRenderStub
        method_map={
                "meta_data_render": math_render_pb.meta_data_render_request,
                "render_latex": math_render_pb.render_latex_request,
            }
        
        GRPCClientFactory.register_service(
            service_name=service_name,
            host=host,
            port=port,
            stub_class=stub_class,
            method_map=method_map
        )
