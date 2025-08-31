from __future__ import annotations

import mimetypes
import os
import re
from contextlib import asynccontextmanager
from typing import Any, Protocol, TYPE_CHECKING
from urllib.parse import urlparse
from uuid import uuid4

from aiobotocore.session import get_session as get_s3_session  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]

from src.core.utils import EnvTools

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class S3Like(Protocol):
    async def put_object(self, **kwargs: Any) -> Any: ...
    async def delete_object(self, **kwargs: Any) -> Any: ...


class S3Client:
    """
    Lightweight async client for S3 compatible storage.
    It can: upload_bytes / upload_file / delete_object / make_key / public_ur
    """
    def __init__(self) -> None:
        self.bucket_name: str = EnvTools.required_load_env_var("s3_bucket_name")
        self.endpoint_url: str = EnvTools.required_load_env_var("s3_endpoint_url")

        self.s3_config: dict[str, str] = {
            "aws_access_key_id": EnvTools.required_load_env_var("s3_access_key"),
            "aws_secret_access_key": EnvTools.required_load_env_var("s3_secret_key"),
            "endpoint_url": self.endpoint_url,
        }

        self.s3_session = get_s3_session()
        self.botocore_config: Config = Config(
            region_name=EnvTools.required_load_env_var("s3_region"),
            s3={"addressing_style": "virtual"},
            proxies={"http": None, "https": None},
            retries={"max_attempts": 3, "mode": "standard"},
        )
        self.default_acl: str = "public-read"
        self.public_domain: str = EnvTools.required_load_env_var("s3_public_domain")
        self.verify: bool = int(EnvTools.required_load_env_var("s3_tls_verify")) == 1


    @asynccontextmanager
    async def get_s3_client(self) -> AsyncIterator[S3Like]:
        async with self.s3_session.create_client(
            "s3",
            **self.s3_config,
            config=self.botocore_config,
            verify=self.verify,
        ) as client:
            yield client  # S3Like


    @staticmethod
    def _ext_from(filename: str, content_type: str | None) -> str:
        ext = os.path.splitext(filename)[1]
        if not ext and content_type:
            guessed = mimetypes.guess_extension(content_type)
            if guessed:
                ext = guessed
        if not ext:
            ext = ".jpg"
        return ext.lower()


    @staticmethod
    def _safe_name(name: str) -> str:
        base = os.path.splitext(os.path.basename(name))[0] or "file"
        base = re.sub(r"[^a-zA-Z0-9._-]+", "-", base).strip("-_.")
        return base or "file"


    async def upload_bytes(self, data: bytes, key: str, content_type: str | None = None) -> None:
        kwargs: dict[str, Any] = {"Bucket": self.bucket_name, "Key": key, "Body": data}
        if content_type:
            kwargs["ContentType"] = content_type
        if self.default_acl:
            kwargs["ACL"] = self.default_acl
        async with self.get_s3_client() as s3:
            await s3.put_object(**kwargs)


    def make_key(self, prefix: str, user_id: str, filename: str, content_type: str | None) -> str:
        ext = self._ext_from(filename, content_type)
        safe = self._safe_name(filename)
        uid = uuid4().hex[:8]
        return f"{prefix}/{user_id}/{safe}-{uid}{ext}"


    async def upload_file(self, file_path: str, object_name: str | None = None, content_type: str | None = None) -> str:
        key = object_name or os.path.basename(file_path)
        ctype = content_type or mimetypes.guess_type(file_path)[0]
        with open(file_path, "rb") as f:
            body = f.read()
        kwargs: dict[str, Any] = {"Bucket": self.bucket_name, "Key": key, "Body": body}
        if ctype:
            kwargs["ContentType"] = ctype
        if self.default_acl:
            kwargs["ACL"] = self.default_acl
        async with self.get_s3_client() as s3:
            await s3.put_object(**kwargs)
        return key


    async def delete_object(self, key: str) -> None:
        async with self.get_s3_client() as s3:
            await s3.delete_object(Bucket=self.bucket_name, Key=key)


    def public_url(self, key: str) -> str:
        """
        Builds a public URL:
        - virtual: https://<bucket>.<host>/<key>
        - path:    https://<host>/<bucket>/<key>
        """
        return f"https://{self.public_domain}/{key.lstrip('/')}"


