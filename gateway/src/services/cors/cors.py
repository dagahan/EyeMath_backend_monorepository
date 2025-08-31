from typing import Optional, Iterable, MutableMapping
from fastapi import Request, Response


class CorsTools:
    def __init__(self) -> None:
        pass


    def build_cors_preflight_response(
        self,
        request: Request,
        allowed_origins: Optional[Iterable[str]] = None,
        allow_credentials: bool = True,
        max_age: int = 600,
    ) -> Response:
        origin_hdr = request.headers.get("origin", "")
        req_method = request.headers.get("access-control-request-method", "")
        req_headers = request.headers.get("access-control-request-headers", "")

        allow_origin: str = ""
        if origin_hdr and (allowed_origins is None or origin_hdr in set(allowed_origins)):
            allow_origin = origin_hdr

        if not allow_origin:
            scheme = request.headers.get("x-forwarded-proto") or request.url.scheme or "http"
            if request.headers.get("x-forwarded-host"):
                client_host = request.headers["x-forwarded-host"]
            elif request.client and request.client.host:
                if getattr(request.client, "port", None):
                    client_host = f"{request.client.host}:{request.client.port}"
                else:
                    client_host = request.client.host
            else:
                client_host = ""
            if client_host:
                allow_origin = f"{scheme}://{client_host}"

        headers: dict[str, str] = {
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": req_method or "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": req_headers or "Authorization, Content-Type",
            "Access-Control-Max-Age": str(max_age),
            "Vary": "Origin",
        }
        if allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        return Response(status_code=200, headers=headers)


    def add_cors_headers_on_response(
        self,
        request: Request,
        response_headers: MutableMapping[str, str],
        allowed_origins: Optional[Iterable[str]] = None,
        allow_credentials: bool = True,
    ) -> None:
        origin_hdr = request.headers.get("origin", "")
        allow_origin = ""

        if origin_hdr and (allowed_origins is None or origin_hdr in set(allowed_origins)):
            allow_origin = origin_hdr
        else:
            scheme = request.headers.get("x-forwarded-proto") or request.url.scheme or "http"
            if request.headers.get("x-forwarded-host"):
                client_host = request.headers["x-forwarded-host"]
            elif request.client and request.client.host:
                if getattr(request.client, "port", None):
                    client_host = f"{request.client.host}:{request.client.port}"
                else:
                    client_host = request.client.host
            else:
                client_host = ""

            if client_host:
                allow_origin = f"{scheme}://{client_host}"

        response_headers["Access-Control-Allow-Origin"] = allow_origin
        response_headers["Vary"] = "Origin"
        if allow_credentials:
            response_headers["Access-Control-Allow-Credentials"] = "true"



