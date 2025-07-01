from typing import List
import strawberry


@strawberry.type
class RegisterUserGraphQLResponse:
    result: bool
    description: str


@strawberry.type
class AuthorizeUserGraphQLResponse:
    result: bool
    token: str


@strawberry.type
class UnAuthorizeUserGraphQLResponse:
    result: bool