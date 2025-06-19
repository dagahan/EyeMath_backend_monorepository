from loguru import logger
from src.grpc.client.factory_grpc_client import GRPCClientFactory


class GrpcRequests:
    pass
    # @staticmethod
    # def solve(latex_expression: str, show_solving_steps: bool, render_latex_expressions: bool) -> str:
    #     try:
    #         response = GRPCClientFactory.rpc_call(
    #             service_name="math_solve",
    #             method_name="solve",
    #             latex_expression=latex_expression,
    #             show_solving_steps=show_solving_steps,
    #             render_latex_expressions=render_latex_expressions,
    #         )
    #         return response
    #     except Exception as ex:
    #         logger.critical(f"Cannot solve latex: {ex}")
