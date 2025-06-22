from concurrent import futures
from typing import Any

import colorama
from loguru import logger

from stubs import service_math_solve_pb2_grpc as service_math_solve_rpc
from stubs import service_math_solve_pb2 as service_math_solve_pb

import grpc
from grpc_reflection.v1alpha import reflection
from src.core.config import ConfigLoader
from src.core.logging import LogAPI
from src.core.utils import EnvTools
from src.services.math_solver import MathSolver


class GRPCMathSolve(service_math_solve_rpc.GRPCMathSolve):
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.mathsolver = MathSolver()
        self.log_api = LogAPI()
        self.project_name = self.config.get("project", "name")
        self.project_version = self.config.get("project", "version")


    @logger.catch
    def meta_data_solve(self, request: service_math_solve_pb.meta_data_solve_request, context) -> service_math_solve_pb.meta_data_solve_response:
        '''
        Endpoint just returns metadata of service.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            response = service_math_solve_pb.meta_data_solve_response(
                name = self.project_name,
                version = self.project_version,
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return service_math_solve_pb.meta_data_solve_response(
                )
        

    @logger.catch
    def solve(self, request: service_math_solve_pb.solve_request, context) -> service_math_solve_pb.solve_response:
        '''
        Endpoint returns a result of solving latex expression.
        Look at service's protobuf file to get more info.
        '''
        self.log_api._logrequest(request, context)

        try:
            solver_answer = self.mathsolver.solve_math_expression(
                request.latex_expression,
                request.show_solving_steps,
                request.render_latex_expressions,
                )
            
            response = service_math_solve_pb.solve_response(
                results=solver_answer['results'],
                renders=solver_answer['renders'],
                solving_steps=solver_answer['solving_steps'],
            )

            self.log_api._logresponse(response, context)
            return response

        except Exception as error:
            logger.error(f"Solve error: {error}")
            return service_math_solve_pb.solve_response(
                results=None,
                solving_steps=None,
                )


class GRPCServerRunner:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.grpc_math_solve = GRPCMathSolve()
        self.max_workers = self.config.get("grpc_server", "max_workers")
        self.host = EnvTools.load_env_var("SOLVER_HOST")
        self.port = EnvTools.load_env_var("SOLVER_APP_PORT")
        self.addr = f"{self.host}:{self.port}"
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))


    def run_grpc_server(self) -> None:
        service_math_solve_rpc.add_GRPCMathSolveServicer_to_server(GRPCMathSolve(), self.grpc_server)
        self.grpc_server.add_insecure_port(self.addr)
        if EnvTools.load_env_var("SOLVER_GRPC_REFLECTIONS") == "1":
            self.enable_reflections_grpc_server(service_math_solve_pb, self.grpc_server)
        logger.info(f"{colorama.Fore.GREEN}gRPC server of {self.grpc_math_solve.project_name} has been started on {colorama.Fore.YELLOW}({self.addr})")
        self.grpc_server.start()
        self.grpc_server.wait_for_termination()


    def enable_reflections_grpc_server(self, stub: Any, grpc_server: grpc.server) -> None:
        '''
        Enable gRPC reflection for the service
        '''
        try:
            service_name = stub.DESCRIPTOR.services_by_name['GRPCMathSolve'].full_name
            SERVICE_NAMES = (
                service_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, grpc_server)
            logger.warning(f"Enabled reflections for the grpc server: '{service_name}'")
        except Exception as ex:
            logger.critical(f"Unable to enable reflections for the {grpc_server} with stub {stub}: {ex}")

