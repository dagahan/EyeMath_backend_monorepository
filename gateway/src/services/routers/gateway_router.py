from __future__ import annotations
from typing import Optional, Dict, TYPE_CHECKING

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from urllib.parse import urlparse

from src.services.routers.base_router import BaseRouter
from src.services.jwt.jwt_parser import JwtParser
from src.services.auth.auth_service import AuthService
from src.services.auth.sessions_manager import SessionsManager
from src.services.cors.cors import CorsTools

if TYPE_CHECKING:
    from src.services.db.database import DataBase


def get_gateway_router(db: "DataBase") -> APIRouter:
    router = APIRouter()
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    auth_service = AuthService(db)  # noqa: F841
    cors_tools = CorsTools()


    @router.api_route(
        "/{endpoint_path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    )
    async def proxy(
        endpoint_path: str,
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    ) -> Response:
        if request.method == "OPTIONS":
            return cors_tools.build_cors_preflight_response(
                request,
                allowed_origins=base_router.ALLOWED_ORIGINS,
            )

        if not base_router.is_public_endpoint(request.method, endpoint_path):
            if credentials is None or not credentials.credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing Authorization",
                )

            access_token = credentials.credentials

            try:
                payload: Dict[str, object] = jwt_parser.decode_token(access_token)
            except HTTPException:
                raise
            except Exception as ex:
                logger.debug(f"Invalid access token in proxy: {ex}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired access token",
                )

            sid = payload.get("sid")
            if not isinstance(sid, str) or not sid:
                logger.debug(f"Access token missing session id (sid) claim: {payload}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Access token missing session id (sid)",
                )

            if not sessions_manager.is_session_exists(sid):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session expired")

            sessions_manager.touch_session(session_id=sid)

        service_address = base_router.map_path_to_service_address(endpoint_path)
        if not service_address:
            raise HTTPException(status_code=404, detail="No upstream service mapped for this path")

        final_forward_url = f"{service_address}/{endpoint_path}"

        parsed = urlparse(final_forward_url)
        upstream_host = parsed.netloc
        client_host = request.client.host if request.client else None
        incoming_headers = dict(request.headers)
        headers = base_router.filter_request_headers(
            incoming_headers,
            upstream_host=upstream_host,
            client_ip=client_host,
        )

        if "authorization" in incoming_headers:
            headers["Authorization"] = incoming_headers["authorization"]

        body = await request.body()
        params = dict(request.query_params)

        try:
            response = await base_router.client.request(
                method=request.method,
                url=final_forward_url,
                headers=headers,
                content=body if body else None,
                params=params,
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc

        response_headers = base_router.filter_response_headers(response.headers)
        cors_tools.add_cors_headers_on_response(
            request,
            response_headers,
            allowed_origins=base_router.ALLOWED_ORIGINS,
        )
        return Response(content=response.content, status_code=response.status_code, headers=response_headers)



    return router


    