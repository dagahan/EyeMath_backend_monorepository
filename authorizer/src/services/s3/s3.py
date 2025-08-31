from __future__ import annotations

import mimetypes
import os
from typing import TYPE_CHECKING

from contextlib import asynccontextmanager
from typing import Any, Protocol

from aiobotocore.session import get_session as get_s3_session  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]

from src.core.utils import EnvTools

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class S3Like(Protocol):
    async def put_object(self, **kwargs: Any) -> Any: ...
    async def delete_object(self, **kwargs: Any) -> Any: ...


class S3Client:
    def __init__(self) -> None:
        self.bucket_name: str = EnvTools.required_load_env_var("s3_bucket_name")
        self.s3_config: dict[str, str] = {
            "aws_access_key_id": EnvTools.required_load_env_var("s3_access_key"),
            "aws_secret_access_key": EnvTools.required_load_env_var("s3_secret_key"),
            "endpoint_url": EnvTools.required_load_env_var("s3_endpoint_url"),
        }
        self.s3_session = get_s3_session()
        self.botocore_config: Config = Config(
            region_name=EnvTools.required_load_env_var("s3_region"),
            s3={"addressing_style": "virtual"},
            proxies={"http": None, "https": None},
            retries={"max_attempts": 3, "mode": "standard"},
        )
        self.verify: bool = False


    @asynccontextmanager
    async def get_s3_client(self) -> AsyncIterator[S3Like]:
        async with self.s3_session.create_client(
            "s3",
            **self.s3_config,
            config=self.botocore_config,
            verify=self.verify,
        ) as client:
            yield client  # typed as S3Like


    async def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: str | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {"Bucket": self.bucket_name, "Key": key, "Body": data}
        if content_type:
            kwargs["ContentType"] = content_type
        async with self.get_s3_client() as s3:
            await s3.put_object(**kwargs)


    def make_key(
        self,
        user_id: str,
        filename: str,
        content_type: str | None,
    ) -> str:
        ext = os.path.splitext(filename or "")[1]
        if not ext:
            ext = mimetypes.guess_extension(content_type or "") or ".jpg"
        return f"avatars/{user_id}/{ext.lower()}"


    async def upload_file(
        self,
        file_path: str,
        object_name: str | None = None,
        content_type: str | None = None,
    ) -> str:
        key = object_name or os.path.basename(file_path)
        ctype = content_type or mimetypes.guess_type(file_path)[0]
        with open(file_path, "rb") as f:
            body = f.read()
        kwargs: dict[str, Any] = {"Bucket": self.bucket_name, "Key": key, "Body": body}
        if ctype:
            kwargs["ContentType"] = ctype
        async with self.get_s3_client() as s3:
            await s3.put_object(**kwargs)
        return key


    async def delete_object(self, key: str) -> None:
        async with self.get_s3_client() as s3:
            await s3.delete_object(Bucket=self.bucket_name, Key=key)
