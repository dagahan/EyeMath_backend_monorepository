from loguru import logger
from src.grpc.client.factory_grpc_client import GRPCClientFactory


class GrpcRequests:
    @staticmethod
    def _render_latex(expression: str) -> str:
        try:
            response = GRPCClientFactory.rpc_call(
                service_name="math_render",
                method_name="render_latex",
                latex_expression=expression,
            )
            return response.render_image
        except Exception as ex:
            logger.critical(f"Cannot rendering latex for math solving process {ex}")
        

    @staticmethod
    def _recognize(image2recognize: str) -> str:
        try:
            response = GRPCClientFactory.rpc_call(
                service_name="math_recognize",
                method_name="recognize",
                normalize_for_sympy=True,
                image=image2recognize
            )
            return response.result
        except Exception as ex:
            logger.critical(f"Cannot recognize latex for math solving process {ex}")