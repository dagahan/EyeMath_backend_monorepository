from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, TYPE_CHECKING, cast

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from PIL import Image, UnidentifiedImageError

from src.core.config import ConfigLoader
from src.services.routers.base_router import BaseRouter
from src.services.media_process.math_recognizer import MathRecognizer
from src.services.media_process.math_recognizer_normalizer import LatexNormalizer

from eyemath_schemas import (  # type: ignore[import-untyped]
    RecognizeImageResponse,
    NormalizeLatexRequest,
    NormalizeLatexResponse,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.services.db.database import DataBase

bearer_scheme = HTTPBearer(auto_error=False)


def get_recognizer_router(db: "DataBase") -> APIRouter:
    router = APIRouter(prefix="/recognizer", tags=["recognizer"])

    base_router = BaseRouter(db)
    recognizer = MathRecognizer()
    normalizer = LatexNormalizer()
    config = ConfigLoader()


    @router.post("/image", response_model=RecognizeImageResponse, status_code=200)
    async def recognize_from_image(
        file: UploadFile = File(...),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> RecognizeImageResponse:

        payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)
        sub_val = payload.get("sub")
        if not isinstance(sub_val, str) or not sub_val:
            raise HTTPException(status_code=400, detail="Invalid user id in token")

        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image/* allowed")

        try:
            raw = await file.read()
            opened = Image.open(BytesIO(raw))
            img = cast("Image.Image", opened)
        except (UnidentifiedImageError, OSError) as e:
            logger.debug(f"Bad image upload: {e}")
            raise HTTPException(status_code=400, detail="Invalid image data")

        try:
            img = recognizer.img_processing.preprocess_image(img)
            await recognizer.save_image_localy(img)

            latex = recognizer.image_to_latex(img)

            latex = normalizer.parse_latex_to_sympylatex(latex)

            return RecognizeImageResponse(latex=latex)
        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Recognition failed: {ex}")
            raise HTTPException(status_code=500, detail="Recognition failed")


    @router.post("/normalize", response_model=NormalizeLatexResponse, status_code=200)
    async def normalize_latex(
        data: NormalizeLatexRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> NormalizeLatexResponse:

        payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)
        sub_val = payload.get("sub")
        if not isinstance(sub_val, str) or not sub_val:
            raise HTTPException(status_code=400, detail="Invalid user id in token")

        try:
            normalized = normalizer.parse_latex_to_sympylatex(data.expression)
            return NormalizeLatexResponse(normalized=normalized)
        except Exception as ex:
            logger.error(f"Normalization failed: {ex}")
            raise HTTPException(status_code=500, detail="Normalization failed")

    return router



