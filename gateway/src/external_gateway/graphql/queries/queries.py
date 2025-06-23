import strawberry
from loguru import logger

from src.external_gateway.graphql.queries.queries_shemas import *
from src.grpc.grpc_requests import GrpcRequests


@strawberry.type
class Query:
    @strawberry.field(description="Solve math expression in latex format.")
    def solve(
    self,
    latex_expression: str = "2x = 10",
    show_solving_steps: bool = True,
    render_latex_expressions: bool = False,
    ) -> MathSolveGraphQLResponse:
        
        response = GrpcRequests.solve(latex_expression, show_solving_steps, render_latex_expressions)
        return MathSolveGraphQLResponse(
            results=response.results,
            renders=response.renders,
            solving_steps=response.solving_steps,
        )


    @strawberry.field(description="Recognize math expression in latex format from image.")
    def recognize(
    self,
    image: str,
    normalize_for_sympy: bool = True,
    ) -> MathRecognizeGraphQLResponse:
        
        response = GrpcRequests.recognize(image, normalize_for_sympy)
        return MathRecognizeGraphQLResponse(
            result=response,
        )
    
    
    @strawberry.field(description="Validate jwt token.")
    def validate_jwt(
    self,
    token: str,
    ) -> ValidateJwtGraphQLResponse:
        
        response = GrpcRequests.validate_jwt(token)
        return ValidateJwtGraphQLResponse(
            result=response.result,
        )
