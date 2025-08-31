from __future__ import annotations

from typing import Any, Mapping, Optional, Dict

import httpx
from loguru import logger

from src.core.utils import EnvTools


class BaseHttpClient:
    """
    The basic async HTTP client.
    Makes JSON requests, collects URLs, mixes Authorization, throws exceptions for non-200.
    """
    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        service_name: Optional[str] = None,
        timeout: float = 10.0,
        read_timeout: float = 30.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
    
        if base_url is None:
            if not service_name:
                raise ValueError("Either base_url or service_name must be provided")
            host = EnvTools.get_service_ip(service_name)
            port = EnvTools.get_service_port(service_name)
            base_url = f"http://{host}:{port}"

        self.base_url: str = base_url.rstrip("/")
        self._client: httpx.AsyncClient = client or httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, read=read_timeout)
        )


    async def aclose(self) -> None:
        await self._client.aclose()


    async def __aenter__(self) -> "BaseHttpClient":
        return self


    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()


    def _join(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"


    def _headers(
        self,
        authorization: Optional[str] = None,
        extra: Optional[Mapping[str, str]] = None,
    ) -> Dict[str, str]:

        h: Dict[str, str] = {}
        if authorization:
            h["Authorization"] = authorization
        if extra:
            h.update(dict(extra))
        return h


    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Any] = None,
        params: Optional[Mapping[str, Any]] = None,
        authorization: Optional[str] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        expected_status: int = 200,
    ) -> Dict[str, Any]:

        url = self._join(path)
        try:
            resp = await self._client.request(
                method=method.upper(),
                url=url,
                json=json,
                params=params,
                headers=self._headers(authorization, extra_headers),
            )
        except Exception as ex:
            logger.error(f"HTTP request failed {method} {url}: {ex}")
            raise

        if resp.status_code != expected_status:
            text = resp.text[:500]
            logger.warning(f"{method} {url} -> {resp.status_code}: {text}")
            resp.raise_for_status()

        try:
            data = resp.json()
        except Exception as ex:
            logger.error(f"Non-JSON response from {url}: {ex}")
            raise

        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object from {url}, got {type(data).__name__}")
            
        return data


