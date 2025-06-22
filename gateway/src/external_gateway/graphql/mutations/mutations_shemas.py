from typing import List
import strawberry


@strawberry.type
class RegisterUserGraphQLResponse:
    result: bool
    description: str