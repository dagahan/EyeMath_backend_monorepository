from typing import List
import strawberry

@strawberry.type
class MathSolveGraphQLResponse:
    results: List[str]
    renders: List[str]
    solving_steps: List[str] | None = strawberry.field(description="Solving steps")


@strawberry.type
class MathRecognizeGraphQLResponse:
    result: str