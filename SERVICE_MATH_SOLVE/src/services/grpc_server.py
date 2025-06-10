import json
from concurrent import futures

import colorama
import grpc
from google.protobuf.json_format import MessageToDict
from loguru import logger

import gen.service_math_solve_pb2 as sevice_math_solve_pb
import gen.service_math_solve_pb2_grpc as sevice_math_solve_rpc

# from grpc_reflection.v1alpha import reflection #reflections to gRPC server
from src.core.config import ConfigLoader
from src.core.utils import EnvTools, MethodTools
from src.services.math_solver import MathSolver


class GRPCMathSolve(sevice_math_solve_rpc.GRPCMathSolve):
    def __init__(self):
        self.config = ConfigLoader()
        self.mathsolver = MathSolver()
        self.env_tools = EnvTools()
        self.method_tools = MethodTools()
        self.log_requests = self.config.get("grpc_server", "log_requests")
        self.log_responses = self.config.get("grpc_server", "log_responses")
        self.project_name = self.config.get("project", "name")
        self.project_version = self.config.get("project", "version")


    @logger.catch
    def _logrequest(self, request, context):
        if self.log_requests:
            payload = MessageToDict(request)
            logger.info(
                f"Method \"{self.method_tools.name_of_method(3, 3)}\" has called from  |  {context.peer()}\n" #format: 'ipv4:127.0.0.1:54321'
                f"{json.dumps(payload, indent=4, ensure_ascii=False)}"
            )

    @logger.catch
    def _logresponce(self, responce, context):
        if self.log_responses:
            payload = MessageToDict(responce)
            logger.info(
                f"Method \"{self.method_tools.name_of_method(3, 3)}\" responsing to  |  {context.peer()}\n"
                f"{json.dumps(payload, indent=4, ensure_ascii=False)}"
            )


    @logger.catch
    def meta_data(self, request: sevice_math_solve_pb.meta_data_request, context) -> sevice_math_solve_pb.meta_data_response:
        self._logrequest(request, context)

        try:
            responce = sevice_math_solve_pb.meta_data_response(
                name = self.project_name,
                version = self.project_version,
            )

            self._logresponce(responce, context)
            return responce

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return sevice_math_solve_pb.meta_data_response(
                )

    @logger.catch
    def solve(self, request: sevice_math_solve_pb.solve_request, context) -> sevice_math_solve_pb.solve_response: #that function we call "endpoint of the gRPC api"
        self._logrequest(request, context)

        try:
            if self.env_tools.is_debug_mode() == "1":
                math_answer = self.mathsolver.solve_expression_debug(request)
            else:
                math_answer = self.mathsolver.solve_expression(request)
            responce = sevice_math_solve_pb.solve_response(
                result=str(math_answer),
            )

            self._logresponce(responce, context)
            return responce

        except Exception as error:
            logger.error(f"Solve error: {error}")
            return sevice_math_solve_pb.solve_response(
                result="None",
                )


class GRPCServerRunner:
    def __init__(self):
        self.config = ConfigLoader()
        self.grpc_math_solve = GRPCMathSolve()
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.host = self.config.get("grpc_server", "host")
        self.port = int(self.config.get("grpc_server", "port"))
        self.addr = f"{self.host}:{self.port}"


    def run_grpc_server(self):
        sevice_math_solve_rpc.add_GRPCMathSolveServicer_to_server(GRPCMathSolve(), self.grpc_server)

        self.grpc_server.add_insecure_port(self.addr)

        # Enable gRPC reflection for the service
        # SERVICE_NAMES = (
        #     sevice_math_solve_pb.DESCRIPTOR.services_by_name['GRPCMathSolve'].full_name,
        #     reflection.SERVICE_NAME,
        # )
        # reflection.enable_server_reflection(SERVICE_NAMES, server)

        logger.info(f"{colorama.Fore.GREEN}gRPC server of {self.grpc_math_solve.project_name} has been started on {colorama.Fore.YELLOW}({self.addr})")
        self.grpc_server.start()
        self.grpc_server.wait_for_termination()

