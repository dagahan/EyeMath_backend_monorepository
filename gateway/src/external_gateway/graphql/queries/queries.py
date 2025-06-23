import strawberry
from loguru import logger

from src.external_gateway.graphql.queries.queries_shemas import *
from src.external_gateway.graphql.token_validation import TokenValidator
from src.grpc.grpc_requests import GrpcRequests


# TODO: There is unrestful api and there is no errors handling :(
# TODO: Also, the graphql shemas need to be rewriten in specific .graphql files!


@strawberry.type
class Query:
    @strawberry.field(description="Solve math expression in latex format.")
    def solve(
    self,
    token: str,
    latex_expression: str = "2x = 10",
    show_solving_steps: bool = True,
    render_latex_expressions: bool = False,
    ) -> MathSolveGraphQLResponse:
        
        if not TokenValidator.validate_token_grpc(token):
            raise "Invalid or expired token"
        
        else:
            response = GrpcRequests.solve(latex_expression, show_solving_steps, render_latex_expressions)
            return MathSolveGraphQLResponse(
                results=response.results,
                renders=response.renders,
                solving_steps=response.solving_steps,
            )


    @strawberry.field(description="Recognize math expression in latex format from image.")
    def recognize(
    self,
    token: str,
    image: str,
    normalize_for_sympy: bool = True,
    ) -> MathSolveGraphQLResponse:
        
        if not TokenValidator.validate_token_grpc(token):
            raise "Invalid or expired token"
        
        else:
            response = GrpcRequests.recognize(image, normalize_for_sympy)
            return MathRecognizeGraphQLResponse(
                result=response,
            )