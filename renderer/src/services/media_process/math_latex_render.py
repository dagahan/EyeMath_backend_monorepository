from __future__ import annotations

import hashlib
import os
import time
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.core.config import ConfigLoader
from src.core.utils import FileSystemTools
from src.services.s3.s3 import S3Client
import asyncio


class LatexRenderTool:
    """
    Renders LaTeX to JPG and uploads the file to S3. Returns the public URL..
    """
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.save_render_img: bool = bool(self.config.get("latex_render", "save_render_img"))
        self.rendered_img_dir: str = str(self.config.get("latex_render", "rendered_img_dir"))
        self.s3 = S3Client()


    def clear_saved_renders(self, dir_path: str) -> None:
        FileSystemTools.delete_directory(dir_path)


    async def _save_image_locally(
        self,
        jpg_bytes: bytes
    ) -> None:

        if not self.save_render_img:
            return
        FileSystemTools.ensure_directory_exists(self.rendered_img_dir)
        idx = FileSystemTools.count_files_in_dir(self.rendered_img_dir)
        file_path = os.path.join(self.rendered_img_dir, f"image{idx}.jpg")
        FileSystemTools.save_file(file_path, jpg_bytes)


    def render_latex_jpg(
        self,
        latex_expression: str,
        dpi: int
    ) -> bytes:

        fig = plt.figure(figsize=(0.1, 0.1), dpi=dpi)
        plt.text(0.5, 0.5, f"${latex_expression}$", fontsize=12, ha="center", va="center")
        plt.axis("off")

        buf = BytesIO()
        plt.savefig(
            buf,
            format="jpg",
            bbox_inches="tight",
            pad_inches=0.05,
            transparent=False,
            dpi=dpi,
        )
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()


    def _make_render_key(
        self,
        user_id: str,
        jpg_bytes: bytes
    ) -> str:
        """
        Stable, unique name in S3: renders/{uid}/ts_hash16.jpg
        """
        digest = hashlib.sha256(jpg_bytes).hexdigest()[:16]
        ts = int(time.time())
        return f"renders/{user_id}/{ts}_{digest}.jpg"


    async def render_and_upload(
        self,
        latex_expression: str,
        dpi: int,
        user_id: str
    ) -> str:
        """
        Render → JPG → (optional) save locally → upload to S3 → return public URL.
        """
        jpg = self.render_latex_jpg(latex_expression, dpi)
        await self._save_image_locally(jpg)

        key = self._make_render_key(user_id, jpg)
        await self.s3.upload_bytes(jpg, key, content_type="image/jpeg")

        return self.s3.public_url(key)


    async def render_and_upload_batch(
        self,
        latex_expressions: list[str],
        dpi: int,
        user_id: str
    ) -> list[str]:
        sem = asyncio.Semaphore(5)

        async def one(expr: str) -> str:
            async with sem:
                jpg = self.render_latex_jpg(expr, dpi)
                await self._save_image_locally(jpg)
                key = self._make_render_key(user_id, jpg)
                await self.s3.upload_bytes(jpg, key, content_type="image/jpeg")
                return self.s3.public_url(key)

        return await asyncio.gather(*(one(e) for e in latex_expressions))


