from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Union, Sequence

import colorama
import sympy
from loguru import logger
from mpmath import mp
from sympy import Eq, Poly, Symbol, preorder_traversal
from sympy.core.basic import Basic
from sympy.parsing.latex import parse_latex as parse_string_to_latex

from src.core.config import ConfigLoader
from src.core.utils import MethodTools
from .alghoritms.quadratic_equations import QuadraticEquationSolver
from src.services.http_clients.renderer_client import RendererHttpClient


class MathSolver:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        mp.dps = int(self.config.get("math", "precision"))
        self.using_algorithms: bool = bool(self.config.get("math", "using_algorithms_solving"))


    @logger.catch
    def _is_equation(self, expr: Basic) -> bool:
        if isinstance(expr, Eq):
            logger.debug(f"{colorama.Fore.YELLOW}{expr} {colorama.Fore.MAGENTA}is an equation.")
            return True
        return any(isinstance(node, Symbol) for node in preorder_traversal(expr))


    @logger.catch
    def _is_quadratic_equation(self, equation: Eq) -> bool:
        expr = equation.lhs - equation.rhs
        symbols = expr.free_symbols
        if len(symbols) == 1:
            var = next(iter(symbols))
            poly = Poly(expr, var)
            return poly.degree() == 2
        return False


    @logger.catch
    def remove_extra_zeroes_float(self, value: float) -> float:
        return float(str(value).strip("0"))


    @logger.catch
    def remove_extra_zeroes_list(self, value: List[Any]) -> List[Any]:
        out: List[Any] = []
        for v in value:
            if isinstance(v, float):
                v = self.remove_extra_zeroes_float(float(v))
            out.append(v)

        return out


    @logger.catch
    def remove_extra_zeroes_dict(self, value: Dict[Any, Any]) -> Dict[Any, Any]:
        out: Dict[Any, Any] = {}
        for k, v in value.items():
            if isinstance(v, float):
                v = self.remove_extra_zeroes_float(float(v))
            out[k] = v

        return out


    @logger.catch
    def remove_extra_zeroes_for_answer(
        self,
        input_value: Union[float, Dict[Any, Any], List[Any]],
    ) -> Union[float, Dict[Any, Any], List[Any]]:
        try:
            if isinstance(input_value, list):
                return self.remove_extra_zeroes_list(list(input_value))
            if isinstance(input_value, dict):
                return self.remove_extra_zeroes_dict(dict(input_value))
            if isinstance(input_value, float):
                return self.remove_extra_zeroes_float(float(input_value))
            return input_value
        except Exception as ex:
            logger.error(f"error with removing extra zeroes: {ex}")
            return input_value


    @logger.catch
    def _handle_quadratic_case(
        self,
        parsed_expr: Eq,
        show_steps: bool,
        render_latex: bool,
    ) -> Dict[str, List[str]]:

        answer = QuadraticEquationSolver.solve_quadratic_equation(parsed_expr)
        results_raw: List[Any] = answer["results"]  # roots
        solving_steps: List[str] = answer["solving_steps"] if show_steps else ["None"]

        str_results = self._convert_results_to_strings(results_raw, clean_zeros=False)
        return {
            "results": str_results,
            "renders_urls": ["None"] * len(str_results),
            "solving_steps": [str(step) for step in solving_steps],
        }


    @logger.catch
    def _handle_general_case(
        self,
        parsed_expr: Basic,
        render_latex: bool,
    ) -> Dict[str, List[str]]:
        if self._is_equation(parsed_expr):
            result = sympy.solve(parsed_expr)
            if isinstance(result, dict):
                solutions: Sequence[Any] = list(result.values())
            else:
                solutions = result if isinstance(result, list) else [result]
        else:
            solutions = [parsed_expr.evalf()]

        str_results = self._convert_results_to_strings(list(solutions), clean_zeros=True)
        return {
            "results": str_results,
            "renders_urls": ["None"] * len(str_results),
            "solving_steps": ["None"],
        }


    def _convert_results_to_strings(
        self,
        results: Union[List[Any], Any],
        clean_zeros: bool = False,
    ) -> List[str]:
        items: List[Any] = results if isinstance(results, list) else [results]
        str_results = [str(item) for item in items]
        if clean_zeros:
            trimmed = self.remove_extra_zeroes_for_answer(str_results)
            return [str(x) for x in (trimmed if isinstance(trimmed, list) else str_results)]
        return str_results


    async def _render_one(self, expr: str, access_token: str) -> str:
        client = RendererHttpClient()
        return await client.render_latex_url(expr, access_token)


    async def _render_many(self, expressions: List[str], access_token: str) -> List[str]:
        client = RendererHttpClient()
        tasks = [client.render_latex_url(expr, access_token) for expr in expressions]
        urls = await asyncio.gather(*tasks, return_exceptions=False)
        return list(urls)


    async def _generate_renders_async(
        self,
        str_results: List[str],
        render_latex: bool,
        access_token: str,
    ) -> List[str]:

        if not render_latex:
            return ["None"] * len(str_results)
        if len(str_results) == 1:
            return [await self._render_one(str_results[0], access_token)]
        return await self._render_many(str_results, access_token)



    @logger.catch
    async def solve_math_expression(
        self,
        expression: str,
        show_solving_steps: bool,
        render_latex_expressions: bool,
        access_token: str,
    ) -> Dict[str, List[str]]:

        parsed = parse_string_to_latex(expression)

        if self.using_algorithms and isinstance(parsed, Eq) and self._is_quadratic_equation(parsed):
            base = self._handle_quadratic_case(parsed, show_solving_steps, render_latex_expressions)
        else:
            base = self._handle_general_case(parsed, render_latex_expressions)

        results: List[str] = base["results"]
        images_urls = await self._generate_renders_async(results, render_latex_expressions, access_token)
        base["images_urls"] = images_urls

        return base


