from __future__ import annotations

from typing import Any, Dict, Optional

from loguru import logger

from .base_client import BaseHttpClient


class RendererHttpClient(BaseHttpClient):
    """
    Client to the renderer service.
    POST /renderer/render {latex_expression} -> { id, url, mime, width, height, size }
    We return a convenient URL to the image.
    """

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        client=None,
        endpoint: str = "/renderer/render",
    ) -> None:

        super().__init__(base_url=base_url, service_name=None if base_url else "renderer", client=client)
        self.endpoint = endpoint


    async def render_latex_url(self, expression: str, access_token: str) -> str:
        data = await self._request_json(
            "POST",
            self.endpoint,
            json={"latex_expression": expression},
            authorization=access_token,
        )

        url = data.get("image_url") or data.get("images_urls")
        return url


