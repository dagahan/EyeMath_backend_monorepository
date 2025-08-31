from __future__ import annotations

import asyncio
import tempfile
from io import BytesIO
import os
import colorama# type: ignore[import-untyped]
from typing import Optional, TYPE_CHECKING

from loguru import logger
from pix2tex import cli# type: ignore[import-untyped]

from src.core.config import ConfigLoader
from src.core.utils import FileSystemTools
from .math_img_processing import ImgProcessing

if TYPE_CHECKING:
    from PIL import Image


class MathRecognizer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.img_processing = ImgProcessing()
        self.model = cli.LatexOCR()

        self.save_receive_img: bool = bool(self.config.get("recognizer", "save_receive_img"))
        self.recieved_img_dir: str = str(self.config.get("recognizer", "recieved_img_dir"))


    def image_to_latex(self, image: Image.Image) -> str:
        """
        OCR LaTeX from PIL.Image. In case of a fall, a fallback is sent via a temporary file.
        """
        try:
            result: str = self.model(image)
            return result
        except Exception:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                image.save(tmp.name, format="JPEG")
                tmp_path = tmp.name
            try:
                result = self.model(tmp_path) 
            finally:
                try:
                    FileSystemTools.delete_file(tmp_path)
                except OSError:
                    pass
            return result


    def clear_saved_msgs_pictures(self, dir_path: str) -> None:
        FileSystemTools.delete_directory(dir_path)


    async def save_image_localy(self, image: Image.Image) -> None:
        """
        Asynchronously save the received snapshot (if enabled in the config).
        """
        if not self.save_receive_img:
            return

        FileSystemTools.ensure_directory_exists(self.recieved_img_dir)
        file_name = f"image{FileSystemTools.count_files_in_dir(self.recieved_img_dir)}.jpg"
        file_path = os.path.join(self.recieved_img_dir, file_name)

        img_bytes = self.image_to_bytes(image)
        FileSystemTools.save_file(file_path, img_bytes)


    def image_to_bytes(self, image: Image.Image, format: str = "JPEG") -> bytes:
        buf = BytesIO()
        image.save(buf, format=format)
        return buf.getvalue()


    def recognize_image(self, image: Image.Image) -> str:
        """
        Full cycle of recognition from PIL.Image:
        - preprocessing;
        - (best-effort) saving the snapshot;
        - OCR.
        Synchronous wrapping — saving goes on in the background if there is an event loop..
        """
        try:
            img_to_recognize = self.img_processing.preprocess_image(image)

            if self.save_receive_img:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    asyncio.run(self.save_image_localy(img_to_recognize))
                else:
                    loop.create_task(self.save_image_localy(img_to_recognize))

            recognition_result = self.image_to_latex(img_to_recognize)
            logger.info(f"Recognition result: {colorama.Fore.YELLOW}{recognition_result}")
            return recognition_result

        except Exception as ex:
            logger.debug(f"Recognition error: {ex}")
            return ""


