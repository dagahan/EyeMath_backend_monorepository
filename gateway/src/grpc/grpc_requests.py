from loguru import logger
from src.grpc.client.factory_grpc_client import GRPCClientFactory


class GrpcRequests:
    @staticmethod
    def solve(latex_expression: str, show_solving_steps: bool, render_latex_expressions: bool) -> str:
        try:
            response = GRPCClientFactory.rpc_call(
                service_name="solver",
                method_name="solve",
                latex_expression=latex_expression,
                show_solving_steps=show_solving_steps,
                render_latex_expressions=render_latex_expressions,
            )
            return response
        except Exception as ex:
            logger.critical(f"Cannot solve latex: {ex}")
        

    @staticmethod
    def recognize(image2recognize: str, normalize_for_sympy: bool) -> str:
        try:
            response = GRPCClientFactory.rpc_call(
                service_name="recognizer",
                method_name="recognize",
                normalize_for_sympy=normalize_for_sympy,
                image=image2recognize
            )
            return response.result
        except Exception as ex:
            logger.critical(f"Cannot recognize latex for math solving process {ex}")