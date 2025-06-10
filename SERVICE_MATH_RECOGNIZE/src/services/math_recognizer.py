import asyncio
import os
import os.path
import tempfile
from io import BytesIO

import colorama
from loguru import logger
from PIL import Image
from pix2tex import cli

from src.core.config import ConfigLoader


class ProcessImage():
    def __init__(self):
        pass


class MathRecognizer:
    def __init__(self):
        self.config = ConfigLoader()
        self.model = cli.LatexOCR()
        self.process = ProcessImage()
        self.save_receive_imgs = self.config.get("recognizer", "save_receive_imgs")
        self.save_imgs_dir = self.config.get("recognizer", "save_imgs_dir")
        self.preprocess_imgs = self.config.get("recognizer", "preprocess_imgs")


    def image_to_latex(self, image) -> str:
        try:
            # Если model может принять PIL.Image, это отработает
            return self.model(image)
        except Exception:
            # Иначе сохраним во временный файл и передадим путь
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                # Сохраняем изображение в файл
                image.save(tmp.name, format="PNG")
                tmp_path = tmp.name
            try:
                result = self.model(tmp_path)
            finally:
                # Удаляем временный файл
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            return result
        

    def count_files_in_dir(self, dir) -> int:
        return len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])
    

    # TODO: clear_saved_msgs_pictures()


    async def save_image_localy(self, image):
        image.save(f"recived_images/image{self.count_files_in_dir(self.save_imgs_dir) + 1}.jpg")


    @logger.catch
    def recognize_expression(self, request_picture) -> str:
        if not hasattr(request_picture, "image"):
            return ""
        try:
            img_to_recognize = Image.open(BytesIO(request_picture.image))
            if img_to_recognize.mode != "RGB":
                img_to_recognize = img_to_recognize.convert("RGB")

            if self.save_receive_imgs:
                asyncio.run(self.save_image_localy(img_to_recognize))

            recognition_result = self.image_to_latex(img_to_recognize)
            logger.info(f"recognition result: {colorama.Fore.YELLOW}{recognition_result}")

        except Exception as ex:
            logger.debug(f"Regognition error: {ex}")
            recognition_result = ""
        return recognition_result

