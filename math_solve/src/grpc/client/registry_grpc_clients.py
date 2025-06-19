
import gen.gateway_pb2 as gateway_pb
import gen.gateway_pb2_grpc as gateway_rpc
import gen.service_math_recognize_pb2 as math_recognize_pb
import gen.service_math_recognize_pb2_grpc as math_recognize_rpc
import gen.service_math_render_pb2 as math_render_pb
import gen.service_math_render_pb2_grpc as math_render_rpc
import gen.service_math_solve_pb2 as math_solve_pb
import gen.service_math_solve_pb2_grpc as math_solve_rpc
from src.core.utils import EnvTools
from src.grpc.client.factory_grpc_client import GRPCClientFactory


class RegistryGrpcMethods:
    @classmethod
    def pull_actual_grpc_methods(cls):
        pass


    @classmethod
    def register_service_with_methods(cls):
        # GATEWAY
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


        # MATH_SOLVE
        service_name="math_solve"
        host=EnvTools.load_env_var("MATH_SOLVE_HOST")
        port=EnvTools.load_env_var("MATH_SOLVE_APP_PORT")
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


        # MATH_RECOGNIZE
        service_name="math_recognize"
        host=EnvTools.load_env_var("RECOGNIZE_LATEX_HOST")
        port=EnvTools.load_env_var("RECOGNIZE_LATEX_APP_PORT")
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


        # MATH_RENDER
        service_name="math_render"
        host=EnvTools.load_env_var("RENDER_LATEX_HOST")
        port=EnvTools.load_env_var("RENDER_LATEX_APP_PORT")
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
