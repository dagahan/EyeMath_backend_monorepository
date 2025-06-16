import colorama
import re
from loguru import logger

from src.core.config import ConfigLoader



class LatexParser:
    def __init__(self) -> None:
        self.config = ConfigLoader()


    def normalize_spaces(self, input_str: str) -> str:
        # Заменяем все виды LaTeX-пробелов на обычные пробелы
        normalized = re.sub(r'\\(?:,| |;|quad|qquad|!)', ' ', input_str)
        
        # Убираем пробелы вокруг операторов где они избыточны
        normalized = re.sub(r'\s*([=+\-*/])\s*', r' \1 ', normalized)
        
        # Заменяем множественные пробелы на один
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        logger.debug(f"Done normalizing spaces for {input_str} output result: {colorama.Fore.YELLOW}{normalized}")
        return normalized


    def parse_latex_to_sympylatex(self, input_str: str) -> str:
        logger.debug(f"Parsing latex expression {input_str} to latex2sympy format.")
        return self.normalize_spaces(input_str)