from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING, cast

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from src.core.config import ConfigLoader
from src.services.routers.base_router import BaseRouter
from src.services.solving.math_solver import MathSolver

from eyemath_schemas import (  # type: ignore[import-untyped]
    SolveRequest,
    SolveResponse,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.services.db.database import DataBase

bearer_scheme = HTTPBearer(auto_error=False)


def get_solver_router(db: "DataBase") -> APIRouter:
    router = APIRouter(prefix="/solver", tags=["solver"])

    base_router = BaseRouter(db)
    solver = MathSolver()

    @router.post("/solve", response_model=SolveResponse, status_code=200)
    async def solve_expression(
        data: SolveRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> SolveResponse:

        payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)
        sub_val = payload.get("sub")
        if not isinstance(sub_val, str) or not sub_val:
            raise HTTPException(status_code=400, detail="Invalid user id in token")

        try:
            token = credentials.credentials if credentials else ""
            access_token = f"Bearer {token}" if token else ""

            raw = await solver.solve_math_expression(
                expression=data.latex_expression,
                show_solving_steps=data.show_solving_steps,
                render_latex_expressions=data.render_latex_expressions,
                access_token=access_token
            )

            results = cast("list[str]", raw.get("results", []))
            images_urls = cast("list[str]", raw.get("images_urls", []))
            steps   = cast("list[str]", raw.get("solving_steps", []))

            return SolveResponse(
                results=results,
                renders_urls=images_urls,
                solving_steps=steps
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Solving failed: {ex}")
            raise HTTPException(status_code=500, detail="Solving failed")



    return router


