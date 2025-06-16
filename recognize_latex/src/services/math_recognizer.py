import asyncio
import tempfile
from io import BytesIO

import colorama
from loguru import logger
from PIL import Image
from pix2tex import cli

from src.core.config import ConfigLoader
from src.core.utils import FileSystemTools
from src.services.math_img_processing import ImgProcessing


class MathRecognizer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.img_processing = ImgProcessing()
        self.model = cli.LatexOCR()
        self.save_receive_imgs = self.config.get("recognizer", "save_receive_imgs")
        self.save_imgs_dir = self.config.get("recognizer", "save_imgs_dir")


    def image_to_latex(self, image: Image.Image) -> str:
        try:
            return self.model(image)
        
        except Exception:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                image.save(tmp.name, format="JPG")
                tmp_path = tmp.name
            try:
                result = self.model(tmp_path)
            finally:
                try:
                    FileSystemTools.delete_file(tmp_path)
                except OSError:
                    pass
            return result
    

    def clear_saved_msgs_pictures(self, dir: str) -> None:
        FileSystemTools.delete_directory(dir)


    async def save_image_localy(self, image: Image.Image) -> None:
        if self.save_receive_imgs:
            image.save(f"recived_images/image{FileSystemTools.count_files_in_dir(self.save_imgs_dir)}.jpg")


    def _convert_bytes_to_img(self, img_bytes: bytes) -> Image.Image:
        return Image.open(BytesIO(img_bytes))
        
            
    @logger.catch
    def recognize_expression(self, request_picture: bytes) -> str:
        '''returns recognized LaTeX on picture.'''
        try:
            img_to_recognize = self._convert_bytes_to_img(request_picture)
            img_to_recognize = self.img_processing.preprocess_image(img_to_recognize)

            asyncio.run(self.save_image_localy(img_to_recognize))

            recognition_result = self.image_to_latex(img_to_recognize)
            logger.info(f"Recognition result: {colorama.Fore.YELLOW}{recognition_result}")

        except Exception as ex:
            logger.debug(f"Recognition error: {ex}")
            recognition_result = ""
        return recognition_result

