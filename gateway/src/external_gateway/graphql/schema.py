from loguru import logger
from typing import List
from strawberry.fastapi import GraphQLRouter

from src.grpc.client.factory_grpc_client import GRPCClientFactory

import strawberry



@strawberry.type
class MathSolution:
    results: List[str]
    solving_steps: List[str] | None = strawberry.field(description="Шаги решения")


class Shema:
    @strawberry.type
    class Query:
        @strawberry.field(description="Решить математическое выражение")
        def solve_math(self, 
        latex_expression: str = "6x^{2} - 17x + 12 = 0",
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
                solving_steps=response.solving_steps
            )
        


    def create_graphql_router(self) -> GraphQLRouter:
        schema = strawberry.Schema(
            query=self.Query
        )
        return GraphQLRouter(schema)