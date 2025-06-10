import colorama

from loguru import logger
from PIL import ImageFilter, ImageEnhance

from src.core.config import ConfigLoader




class ImgProcessing():
    def __init__(self):
        self.config = ConfigLoader()
        self.preprocess_imgs = self.config.get("recognizer", "preprocess_imgs")


    @logger.catch
    def preprocess_image(self, image):
        '''
        increase sharpness, contrast and enhance the image
        it's needed to getting better result of recognition
        of LaTeX on image.
        '''
        try:
            if not self.preprocess_imgs:
                return image
            if image.mode != "RGB":
                image = image.convert("RGB")
            image = image.filter(ImageFilter.SHARPEN)
            image = ImageEnhance.Contrast(image).enhance(10000.0)
            processed_image = image.convert("L")
            logger.debug(f"{colorama.Fore.GREEN}Image preprocessing done.")
            return processed_image
        except Exception as ex:
            logger.error(f"There is an error with preprocessing of image: {ex}\n returning image without preprocess.")
            return image