from typing import List

import strawberry
from strawberry.fastapi import GraphQLRouter

from src.grpc.client.factory_grpc_client import GRPCClientFactory


@strawberry.type
class MathSolution:
    results: List[str]
    renders: List[str]
    solving_steps: List[str] | None = strawberry.field(description="Solving steps")


class Shema:
    @strawberry.type
    class Query:
        @strawberry.field(description="Solve math expression in latex format.")
        def solve_math(self,
        latex_expression: str = "2x = 10",
        show_solving_steps: bool = True,
        render_latex_expressions: bool = False,
        ) -> MathSolution:
            
            response = GRPCClientFactory.rpc_call(
                service_name="math_solve",
                method_name="solve",
                latex_expression=latex_expression,
                show_solving_steps=show_solving_steps,
                render_latex_expressions=render_latex_expressions
            )
            
            # Преобразование gRPC ответа в GraphQL тип
            return MathSolution(
                results=response.results,
                renders=response.renders,
                solving_steps=response.solving_steps
            )
        

    def create_graphql_router(self) -> GraphQLRouter:
        schema = strawberry.Schema(
            query=self.Query
        )
        return GraphQLRouter(schema)
