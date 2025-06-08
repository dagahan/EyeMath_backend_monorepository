import colorama
from loguru import logger

from src.core.config import ConfigLoader




class MathRecognizer:
    def __init__(self):
        self.config = ConfigLoader()
     

    @logger.catch
    def RecognizeExpression(self, request):
        return 23