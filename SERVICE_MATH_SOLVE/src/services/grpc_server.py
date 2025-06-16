from concurrent import futures

import colorama
import grpc
from loguru import logger

import gen.service_math_solve_pb2 as sevice_math_solve_pb
import gen.service_math_solve_pb2_grpc as sevice_math_solve_rpc
from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.core.logging import LogAPI
from src.services.math_solver import MathSolver


class GRPCMathSolve(sevice_math_solve_rpc.GRPCMathSolve):
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.mathsolver = MathSolver()
        self.env_tools = EnvTools()
        self.log_api = LogAPI()
        self.project_name = self.config.get("project", "name")
        self.project_version = self.config.get("project", "version")


    @logger.catch
    def meta_data_solve(self, request: sevice_math_solve_pb.meta_data_solve_request, context) -> sevice_math_solve_pb.meta_data_solve_response:
        '''
        Endpoint just returns metadata of service.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            response = sevice_math_solve_pb.meta_data_solve_response(
                name = self.project_name,
                version = self.project_version,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return sevice_math_solve_pb.meta_data_solve_response(
                )
        

    @logger.catch
    def solve(self, request: sevice_math_solve_pb.solve_request, context) -> sevice_math_solve_pb.solve_response:
        '''
        Endpoint returns a result of recognizing latex on sended picture by client.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            if self.env_tools.is_debug_mode() == "1":
                solver_answer = self.mathsolver.solve_math_expression_debug(request)
            else:
                solver_answer = self.mathsolver.solve_math_expression(request)
            response = sevice_math_solve_pb.solve_response(
                result=str(solver_answer),
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Solve error: {error}")
            return sevice_math_solve_pb.solve_response(
                result="None",
                )


class GRPCServerRunner:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.grpc_math_solve = GRPCMathSolve()
        self.max_workers = self.config.get("grpc_server", "max_workers")
        self.host = self.config.get("grpc_server", "host")
        self.port = int(self.config.get("grpc_server", "port"))
        self.addr = f"{self.host}:{self.port}"
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))


    def run_grpc_server(self) -> None:
        sevice_math_solve_rpc.add_GRPCMathSolveServicer_to_server(GRPCMathSolve(), self.grpc_server)
        self.grpc_server.add_insecure_port(self.addr)
        logger.info(f"{colorama.Fore.GREEN}gRPC server of {self.grpc_math_solve.project_name} has been started on {colorama.Fore.YELLOW}({self.addr})")
        self.grpc_server.start()
        self.grpc_server.wait_for_termination()

