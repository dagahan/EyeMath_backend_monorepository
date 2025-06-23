from loguru import logger
from src.grpc.client.factory_grpc_client import GRPCClientFactory
from typing import List


class GrpcRequests:
    @staticmethod
    def solve(latex_expression: str,
              show_solving_steps: bool,
              render_latex_expressions: bool) -> List:
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
    def recognize(image2recognize: str,
                  normalize_for_sympy: bool) -> str:
        try:
            response = GRPCClientFactory.rpc_call(
                service_name="recognizer",
                method_name="recognize",
                normalize_for_sympy=normalize_for_sympy,
                image=image2recognize,
            )
            return response.result
        except Exception as ex:
            logger.critical(f"Cannot recognize latex for math solving process: {ex}")


    @staticmethod
    def register(user_name: str,
                password: str,
                email: str,) -> List:
        try:
            response = GRPCClientFactory.rpc_call(
                service_name="authorizer",
                method_name="register",
                user_name=user_name,
                password=password,
                email=email,
            )
            return response
        except Exception as ex:
            logger.critical(f"Cannot register user: {ex}")

    
    @staticmethod
    def authorize(user_name: str,
                password: str) -> List:
        try:
            response = GRPCClientFactory.rpc_call(
                service_name="authorizer",
                method_name="authorize",
                user_name=user_name,
                password=password,
            )
            return response
        except Exception as ex:
            logger.critical(f"Cannot authorize user: {ex}")


    @staticmethod
    def validate_jwt(token: str,
                     ) -> List:
        try:
            response = GRPCClientFactory.rpc_call(
                service_name="authorizer",
                method_name="validate_jwt",
                token=token,
            )
            return response
        except Exception as ex:
            logger.critical(f"Cannot validate jwt: {ex}")

