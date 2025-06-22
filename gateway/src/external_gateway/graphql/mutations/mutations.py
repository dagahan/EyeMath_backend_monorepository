import strawberry
from loguru import logger

from src.external_gateway.graphql.mutations.mutations_shemas import *
from src.grpc.grpc_requests import GrpcRequests


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Register new eye.math account for user.")
    def register(
    self,
    user_name: str,
    password: str,
    email: str,
    ) -> RegisterUserGraphQLResponse:
        
        logger.debug(f"{user_name}, {password}, {email}")
        
        response = GrpcRequests.register(user_name, password, email)
        return RegisterUserGraphQLResponse(
            result=response.result,
            description=response.description,
        )