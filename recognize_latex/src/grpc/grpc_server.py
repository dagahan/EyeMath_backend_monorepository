from concurrent import futures

import colorama
from loguru import logger

import gen.service_math_recognize_pb2 as sevice_math_recognize_pb
import gen.service_math_recognize_pb2_grpc as sevice_math_recognize_rpc
import grpc
from src.core.config import ConfigLoader
from src.core.logging import LogAPI
from src.core.utils import EnvTools
from src.services.math_latex_render import LatexRenderTool
from src.services.math_recognizer import MathRecognizer
from src.services.math_recognizer_normalizer import LatexNormalizer


class GRPCMathRecognize(sevice_math_recognize_rpc.GRPCMathRecognize):
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.mathrecognizer = MathRecognizer()
        self.env_tools = EnvTools()
        self.log_api = LogAPI()
        self.latex_parser = LatexNormalizer()
        self.latex_render_tool = LatexRenderTool()
        self.project_name = self.config.get("project", "name")
        self.project_version = self.config.get("project", "version")
        self.render_dpi = self.config.get("latex_render", "render_dpi")


    @logger.catch
    def meta_data_recognize(self, request: sevice_math_recognize_pb.meta_data_recognize_request, context) -> sevice_math_recognize_pb.meta_data_recognize_response:
        '''
        This endpoint just returns metadata of service.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            response = sevice_math_recognize_pb.meta_data_recognize_response(
                name = self.project_name,
                version = self.project_version,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return sevice_math_recognize_pb.meta_data_recognize_response()


    @logger.catch
    def recognize(self, request: sevice_math_recognize_pb.recognize_request, context) -> sevice_math_recognize_pb.recognize_response:
        '''
        Endpoint returns a result of recognizing latex on sended picture by client.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            recognizer_answer = self.mathrecognizer.recognize_expression(request.image)

            if request.normalize_for_sympy:
                recognizer_answer = self.latex_parser.parse_latex_to_sympylatex(recognizer_answer)

            response = sevice_math_recognize_pb.recognize_response(
                result=recognizer_answer,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Recognize error: {error}")
            return sevice_math_recognize_pb.recognize_response(
                result="None",
                )
        

    @logger.catch
    def normalize_for_sympy(self, request: sevice_math_recognize_pb.normalize_for_sympy_request, context) -> sevice_math_recognize_pb.normalize_for_sympy_response:
        '''
        Endpoint returns a normalized latex-string for using by latex2sympy library.
        Example: 6x^{2}\\,-\\,17x\\ +\\ 12\\,=\\,0 ----------> 6x^{2} - 17x + 12 = 0.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            normalizer_answer = self.latex_parser.parse_latex_to_sympylatex(request.latex_expression)

            response = sevice_math_recognize_pb.normalize_for_sympy_response(
                result=normalizer_answer,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Recognize error: {error}")
            return sevice_math_recognize_pb.normalize_for_sympy_response(
                result="None",
                )
        

    @logger.catch
    def render_latex(self, request: sevice_math_recognize_pb.render_latex_request, context) -> sevice_math_recognize_pb.render_latex_response:
        '''
        Endpoint returns a rendered jpg picture of latex-expression
        in base64 format.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            renderer_answer = self.latex_render_tool.render_latex_jpg_base64(request.latex_expression, self.render_dpi)

            response = sevice_math_recognize_pb.render_latex_response(
                render_image=renderer_answer,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Render error: {error}")
            return sevice_math_recognize_pb.render_latex_response(
                render_image="None",
                )


class GRPCServerRunner:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.grpc_math_recognize = GRPCMathRecognize()
        self.max_workers = self.config.get("grpc_server", "max_workers")
        self.host = self.config.get("grpc_server", "host")
        self.port = int(self.config.get("grpc_server", "port"))
        self.addr = f"{self.host}:{self.port}"
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))


    def run_grpc_server(self) -> None:
        sevice_math_recognize_rpc.add_GRPCMathRecognizeServicer_to_server(GRPCMathRecognize(), self.grpc_server)
        self.grpc_server.add_insecure_port(self.addr)
        logger.info(f"{colorama.Fore.GREEN}gRPC server of {self.grpc_math_recognize.project_name} has been started on {colorama.Fore.YELLOW}({self.addr})")
        self.grpc_server.start()
        self.grpc_server.wait_for_termination()

