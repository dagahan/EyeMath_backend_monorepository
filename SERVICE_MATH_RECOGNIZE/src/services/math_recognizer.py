import colorama
from loguru import logger
from PIL import Image
from pix2tex import cli

from src.core.config import ConfigLoader


class MathRecognizer:
    def __init__(self):
        self.config = ConfigLoader()
        self.model = cli.LatexOCR()


    def image_to_latex(self, image_path: str) -> str:
        return self.model(image_path)


    @logger.catch
    def recognize_expression(self, request):
        img = Image.open('recognize_test/test2.jpg')
        recognition_result = self.image_to_latex(img)
        logger.info(f"recognition result: {colorama.Fore.YELLOW}{recognition_result}")
        return recognition_result

