from __future__ import annotations

from typing import Optional, List, Mapping
import httpx
from src.core.utils import EnvTools


class BaseRouter:
    def __init__(self, db: object) -> None:
        self.db = db
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=30.0))

        self.HOP_BY_HOP: set[str] = {
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        }

        # must be replaced by configmap from k8s
        self.SERVICE_MAP: dict[str, str] = {
            "users": f"http://{EnvTools.get_service_ip('authorizer')}:{EnvTools.get_service_port('authorizer')}",
            "tokens": f"http://{EnvTools.get_service_ip('authorizer')}:{EnvTools.get_service_port('authorizer')}",
            "recognizer": f"http://{EnvTools.get_service_ip('recognizer')}:{EnvTools.get_service_port('recognizer')}",
            "solver": f"http://{EnvTools.get_service_ip('solver')}:{EnvTools.get_service_port('solver')}",
            "renderer": f"http://{EnvTools.get_service_ip('renderer')}:{EnvTools.get_service_port('renderer')}",
        }

        self.PUBLIC_ENDPOINTS: set[tuple[str, tuple[str, ...]]] = {
            ("POST", ("users", "register")),
            ("POST", ("users", "login")),
            ("GET", ("tokens", "access")),
            ("POST", ("tokens", "refresh")),
        }

        self.ALLOWED_ORIGINS: set[str] = {
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "http://127.0.0.1:5501",
            "http://localhost:5501",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://127.0.0.1:4173",
            "http://localhost:4173",
            f"http://{EnvTools.required_load_env_var("FRONTEND_NGINX_DEV_HOST")}:{EnvTools.required_load_env_var("FRONTEND_NGINX_DEV_PORT")}",
            f"http://{EnvTools.required_load_env_var("FRONTEND_NGINX_HOST")}:{EnvTools.required_load_env_var("FRONTEND_NGINX_PORT")}",
            f"http://127.0.0.1:{EnvTools.required_load_env_var("FRONTEND_NGINX_DEV_PORT")}",
            f"http://127.0.0.1:{EnvTools.required_load_env_var("FRONTEND_NGINX_PORT")}"
        }


    def path_segments(self, path: str) -> List[str]:
        return [seg for seg in path.strip("/").split("/") if seg]


    def is_public_endpoint(self, method: str, full_path: str) -> bool:
        segs = self.path_segments(full_path)
        if not segs:
            return False
        for m, tail in self.PUBLIC_ENDPOINTS:
            if m.upper() != method.upper():
                continue
            if len(segs) >= len(tail) and segs[-len(tail) :] == list(tail):
                return True
        return False


    def map_path_to_service_address(self, path: str) -> Optional[str]:
        path = path.lstrip("/")
        prefix = path.split("/", 1)[0] if path else ""
        return self.SERVICE_MAP.get(prefix)


    def _normalize(self, name: str) -> str:
        return name.lower().strip()


    def filter_request_headers(
        self,
        incoming_headers: Mapping[str, str],
        upstream_host: str,
        client_ip: Optional[str],
    ) -> dict[str, str]:
        """
        Remove hop-by-hop headers (including from Connection), Host;
        add/update X-Forwarded-For.
        """
        headers: dict[str, str] = dict(incoming_headers)

        conn_val: Optional[str] = None
        for k in list(headers.keys()):
            if self._normalize(k) == "connection":
                conn_val = headers.pop(k, None)
                break

        conn_tokens: set[str] = set()
        if conn_val:
            for tok in conn_val.split(","):
                tok = tok.strip().lower()
                if tok:
                    conn_tokens.add(tok)

        for key in list(headers.keys()):
            n = self._normalize(key)
            if n in self.HOP_BY_HOP or n in conn_tokens:
                headers.pop(key, None)

        headers.pop("host", None)
        headers.pop("Host", None)

        if client_ip:
            existing_xff = incoming_headers.get("x-forwarded-for") or incoming_headers.get("X-Forwarded-For")
            headers["X-Forwarded-For"] = f"{existing_xff}, {client_ip}" if existing_xff else client_ip

        return headers


    def filter_response_headers(self, incoming_headers: Mapping[str, str]) -> dict[str, str]:
        return {k: v for k, v in incoming_headers.items() if self._normalize(k) not in self.HOP_BY_HOP}



