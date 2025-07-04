from concurrent import futures
from typing import Any

import colorama
from loguru import logger

from stubs import service_math_render_pb2 as service_math_render_pb
from stubs import service_math_render_pb2_grpc as service_math_render_rpc

import grpc
from grpc_reflection.v1alpha import reflection
from src.core.config import ConfigLoader
from src.core.logging import LogAPI
from src.core.utils import EnvTools
from src.services.math_latex_render import LatexRenderTool


class GRPCMathRender(service_math_render_rpc.GRPCMathRender):
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.env_tools = EnvTools()
        self.log_api = LogAPI()
        self.latex_render_tool = LatexRenderTool()
        self.project_name = self.config.get("project", "name")
        self.project_version = self.config.get("project", "version")
        self.render_dpi = self.config.get("latex_render", "render_dpi")


    @logger.catch
    def meta_data_render(self, request: service_math_render_pb.meta_data_render_request, context) -> service_math_render_pb.meta_data_render_response:
        '''
        This endpoint just returns metadata of service.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            response = service_math_render_pb.meta_data_render_response(
                name = self.project_name,
                version = self.project_version,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return service_math_render_pb.meta_data_render_response()
        

    @logger.catch
    def render_latex(self, request: service_math_render_pb.render_latex_request, context) -> service_math_render_pb.render_latex_response:
        '''
        Endpoint returns a rendered jpg picture of latex-expression
        in base64 format.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            renderer_answer = self.latex_render_tool.render_latex_jpg_base64(request.latex_expression, self.render_dpi)

            response = service_math_render_pb.render_latex_response(
                render_image=renderer_answer,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Render error: {error}")
            return service_math_render_pb.render_latex_response(
                render_image="None",
                )


class GRPCServerRunner:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.grpc_math_recognize = GRPCMathRender()
        self.max_workers = self.config.get("grpc_server", "max_workers")
        self.host = EnvTools.load_env_var("RENDERER_HOST")
        self.port = EnvTools.load_env_var("RENDERER_APP_PORT")
        self.addr = f"{self.host}:{self.port}"
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))


    def run_grpc_server(self) -> None:
        service_math_render_rpc.add_GRPCMathRenderServicer_to_server(GRPCMathRender(), self.grpc_server)
        self.grpc_server.add_insecure_port(self.addr)
        if EnvTools.load_env_var("RENDERER_GRPC_REFLECTIONS") == "1":
            self.enable_reflections_grpc_server(service_math_render_pb, self.grpc_server)
        logger.info(f"{colorama.Fore.GREEN}gRPC server of {self.grpc_math_recognize.project_name} has been started on {colorama.Fore.YELLOW}({self.addr})")
        self.grpc_server.start()
        self.grpc_server.wait_for_termination()


    def enable_reflections_grpc_server(self, stub: Any, grpc_server: grpc.server) -> None:
        '''
        Enable gRPC reflection for the service
        '''
        try:
            service_name = stub.DESCRIPTOR.services_by_name['GRPCMathRender'].full_name
            SERVICE_NAMES = (
                service_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, grpc_server)
            logger.warning(f"Enabled reflections for the grpc server: '{service_name}'")
        except Exception as ex:
            logger.critical(f"Unable to enable reflections for the {grpc_server} with stub {stub}: {ex}")