from typing import List

import strawberry
from strawberry.fastapi import GraphQLRouter

from src.grpc.client.factory_grpc_client import GRPCClientFactory
from src.grpc.grpc_requests import GrpcRequests


@strawberry.type
class MathSolveGraphQLResponse:
    results: List[str]
    renders: List[str]
    solving_steps: List[str] | None = strawberry.field(description="Solving steps")


@strawberry.type
class MathRecognizeGraphQLResponse:
    result: str


class Shema:
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
        

    def create_graphql_router(self) -> GraphQLRouter:
        schema = strawberry.Schema(
            query=self.Query,
        )
        return GraphQLRouter(schema)
