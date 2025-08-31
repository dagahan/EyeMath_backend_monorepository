from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING, cast
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from src.core.config import ConfigLoader
from src.services.routers.base_router import BaseRouter
from src.services.media_process.math_latex_render import LatexRenderTool
from eyemath_schemas import (
    RenderLatexRequest, RenderLatexResponse,
    RenderLatexBatchRequest, RenderLatexBatchResponse,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.services.db.database import DataBase

bearer_scheme = HTTPBearer(auto_error=False)


def get_renderer_router(db: "DataBase") -> APIRouter:
    router = APIRouter(prefix="/renderer", tags=["renderer"])
    base_router = BaseRouter(db)
    renderer = LatexRenderTool()
    config = ConfigLoader()
    default_dpi: int = int(config.get("latex_render", "render_dpi"))


    @router.post("/render", response_model=RenderLatexResponse, status_code=200)
    async def render_latex(
        data: RenderLatexRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> RenderLatexResponse:

        payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)
        sub_val = payload.get("sub")
        if not isinstance(sub_val, str) or not sub_val:
            raise HTTPException(status_code=400, detail="Invalid user id in token")
        user_id: str = cast(str, sub_val)

        try:
            dpi = data.dpi if data.dpi is not None else default_dpi
            url = await renderer.render_and_upload(data.latex_expression, dpi, user_id)
            return RenderLatexResponse(image_url=url)

        except Exception as ex:
            logger.error(f"LaTeX render failed: {ex}")
            raise HTTPException(status_code=500, detail="Render failed")


    @router.post("/render/batch", response_model=RenderLatexBatchResponse, status_code=200)
    async def render_latex_batch(
        data: RenderLatexBatchRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> RenderLatexBatchResponse:

        payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)
        sub_val = payload.get("sub")
        if not isinstance(sub_val, str) or not sub_val:
            raise HTTPException(status_code=400, detail="Invalid user id in token")
        user_id: str = cast(str, sub_val)

        try:
            dpi = data.dpi if data.dpi is not None else default_dpi
            urls = await renderer.render_and_upload_batch(data.latex_expressions, dpi, user_id)
            return RenderLatexBatchResponse(images_urls=urls)

        except Exception as ex:
            logger.error(f"LaTeX batch render failed: {ex}")
            raise HTTPException(status_code=500, detail="Batch render failed")



    return router


