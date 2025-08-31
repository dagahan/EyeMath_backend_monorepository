from __future__ import annotations

from typing import Final
import colorama# type: ignore[import-untyped]
from loguru import logger
from PIL import Image, ImageEnhance, ImageFilter

from src.core.config import ConfigLoader


class ImgProcessing:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.preprocess_imgs: bool = bool(self.config.get("recognizer", "preprocess_imgs"))


    @logger.catch
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Increase sharpness/contrast.
        """
        try:
            if not self.preprocess_imgs:
                return image

            processed_image: Image.Image = image

            if processed_image.mode != "RGB":
                processed_image = processed_image.convert("RGB")

            processed_image = processed_image.filter(ImageFilter.SHARPEN)
            processed_image = ImageEnhance.Contrast(processed_image).enhance(10000.0)

            processed_image = processed_image.convert("L")

            logger.debug(f"{colorama.Fore.GREEN}Image preprocessing done.")
            return processed_image

        except Exception as ex:
            logger.error(
                f"There is an error with preprocessing of image: {ex}\nReturning image without preprocess."
            )
            return image


            