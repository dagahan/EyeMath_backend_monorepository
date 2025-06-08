import inspect, grpc, json, sys, colorama

from loguru import logger
from concurrent import futures
from google.protobuf.json_format import MessageToDict
from grpc_reflection.v1alpha import reflection #reflections to gRPC server

from src.core.config import ConfigLoader
from src.services.math_solver import MathSolver
from src.core.utils import EnvTools, MethodTools

import gen.service_math_solve_pb2 as sevice_math_solve_pb
import gen.service_math_solve_pb2_grpc as sevice_math_solve_rpc




class GRPC_math_solve(sevice_math_solve_rpc.GRPC_math_solve):
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
    def Metadata(self, request: sevice_math_solve_pb.MetadataRequest, context) -> sevice_math_solve_pb.MetadataResponse:
        self._logrequest(request, context)

        try:
            responce = sevice_math_solve_pb.MetadataResponse(
                name = self.project_name,
                version = self.project_version,
            )

            self._logresponce(responce, context)
            return responce

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return sevice_math_solve_pb.MetadataResponse(
                )
        
    @logger.catch
    def Solve(self, request: sevice_math_solve_pb.SolveRequest, context) -> sevice_math_solve_pb.SolveResponse: #that function we call "endpoint of the gRPC api"
        self._logrequest(request, context)

        try:
            if self.env_tools.is_debug_mode() == "1":
                MathAnswer = self.mathsolver.SolveExpressionDebugMode(request)
            else:
                MathAnswer = self.mathsolver.SolveExpression(request)
            responce = sevice_math_solve_pb.SolveResponse(
                status=sevice_math_solve_pb.SolveResponse.OK,
                result=str(MathAnswer),
            )

            self._logresponce(responce, context)
            return responce

        except Exception as error:
            logger.error(f"Solve error: {error}")
            return sevice_math_solve_pb.SolveResponse(
                status=sevice_math_solve_pb.SolveResponse.ERROR,
                )
        

class gRPC_Server_Runner:
    def __init__(self):
        self.config = ConfigLoader()
        self.grpc_math_solve = GRPC_math_solve()
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.host = self.config.get("grpc_server", "host")
        self.port = int(self.config.get("grpc_server", "port"))
        self.addr = f"{self.host}:{self.port}"

        

    
    def run_grpc_server(self):
        sevice_math_solve_rpc.add_GRPC_math_solveServicer_to_server(GRPC_math_solve(), self.grpc_server)

        self.grpc_server.add_insecure_port(self.addr)

        # Enable gRPC reflection for the service
        # SERVICE_NAMES = (
        #     sevice_math_solve_pb.DESCRIPTOR.services_by_name['GRPC_math_solve'].full_name,
        #     reflection.SERVICE_NAME,
        # )
        # reflection.enable_server_reflection(SERVICE_NAMES, server)

        logger.info(f"{colorama.Fore.GREEN}gRPC server of {self.grpc_math_solve.project_name} has been started on {colorama.Fore.YELLOW}({self.addr})")
        self.grpc_server.start()
        self.grpc_server.wait_for_termination()

        