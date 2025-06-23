from loguru import logger
from src.grpc.grpc_requests import GrpcRequests


# TODO: it must work as decorator for the each of endpoint's methods.
class TokenValidator:
    @staticmethod
    def validate_token_grpc(token) -> bool:
        try:
            response = GrpcRequests.validate_jwt(token)
            return response.result
        except Exception as ex:
            logger.critical(f"Token cannot be validate: {ex}")
            return False