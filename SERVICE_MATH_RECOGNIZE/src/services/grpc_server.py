from concurrent import futures

import colorama
import grpc
from loguru import logger

import gen.service_math_recognize_pb2 as sevice_math_recognize_pb
import gen.service_math_recognize_pb2_grpc as sevice_math_recognize_rpc
from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.services.logging import LogAPI
from src.services.math_recognizer import MathRecognizer


class GRPCMathRecognize(sevice_math_recognize_rpc.GRPCMathRecognize):
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.mathrecognizer = MathRecognizer()
        self.env_tools = EnvTools()
        self.log_api = LogAPI()
        self.project_name = self.config.get("project", "name")
        self.project_version = self.config.get("project", "version")


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
            if self.env_tools.is_debug_mode() == "1":
                recognizer_answer = self.mathrecognizer.recognize_expression(request)
            else:
                recognizer_answer = self.mathrecognizer.recognize_expression(request)

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

