from __future__ import annotations

import re
import colorama# type: ignore[import-untyped]
from loguru import logger


class LatexNormalizer:
    def __init__(self) -> None:
        self._space_cmds = re.compile(r'\\(?:,| |;|quad|qquad|!)')
        self._ops_around = re.compile(r'\s*([=+\-*/])\s*')
        self._multi_space = re.compile(r'\s+')


    def normalize_spaces(self, input_str: str) -> str:
        """
        Normalizes spaces and indents in a LaTeX string.
        """
        normalized = self._space_cmds.sub(" ", input_str)
        normalized = self._ops_around.sub(r" \1 ", normalized)
        normalized = self._multi_space.sub(" ", normalized).strip()

        logger.debug(
            f"Done normalizing spaces for {input_str} output result: {colorama.Fore.YELLOW}{normalized}"
        )
        return normalized


    def parse_latex_to_sympylatex(self, input_str: str) -> str:
        """
        Converts LaTeX to a format compatible with latex2sympy.
        """
        logger.debug(f"Parsing latex expression {input_str} to latex2sympy format.")
        return self.normalize_spaces(input_str)



