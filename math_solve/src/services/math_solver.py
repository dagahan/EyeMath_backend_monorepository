from typing import Any, Dict, List, Union

import colorama
import sympy
from loguru import logger
from mpmath import mp
from sympy import Eq, Poly, Symbol, preorder_traversal
from sympy.parsing.latex import parse_latex as parse_string_to_latex

from src.core.config import ConfigLoader
from src.core.utils import MethodTools
from src.services.alghoritms.quadratic_equations import QuadraticEquationSolver


class MathSolver:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        mp.dps = self.config.get("math", "precision")
        self.using_alghoritms = self.config.get("math", "using_alghoritms_solving")


    @logger.catch
    def _is_equation(self, expr: str) -> bool:
        if isinstance(expr, Eq):
            logger.debug(
                f"{colorama.Fore.YELLOW}{expr} {colorama.Fore.MAGENTA}is an equation."
            )
            return True
        return any(isinstance(node, Symbol) for node in preorder_traversal(expr))
    

    @logger.catch
    def _is_quadratic_equation(self, equation: Eq) -> bool:
        expr = equation.lhs - equation.rhs
        symbols = expr.free_symbols
        
        if len(symbols) == 1:
            var = next(iter(symbols))
            poly = Poly(expr, var)
            
            if poly.degree() == 2:
                return True
        return False


    @logger.catch
    def remove_extra_zeroes_float(self, value: float) -> float:
        return float(str(value).strip("0"))
    

    @logger.catch
    def remove_extra_zeroes_list(self, value: List) -> List:
        answer = []
        for allowable_answer in value:
            if MethodTools.check_type_of_var(allowable_answer) == "float":
                allowable_answer = self.remove_extra_zeroes_float(allowable_answer)
            answer.append(allowable_answer)
        return answer
    

    @logger.catch
    def remove_extra_zeroes_dict(self, value: Dict) -> Dict:
        answer = {}
        for allowable_answer in value:
            if MethodTools.check_type_of_var(allowable_answer[1]) == "float":
                allowable_answer = self.remove_extra_zeroes_float(allowable_answer[1])
            answer.update(allowable_answer)
        return answer
    

    @logger.catch
    def remove_extra_zeroes_for_answer(self, input_value: Union[float, Dict, List[Any]]) -> Union[float, Dict, List[Any]]:
        '''
        automaticly checks type of input value and trying
        to remove extra zeroes from all of values.
        '''
        try:
            type_of_input_value = MethodTools.check_type_of_var(input_value)
            match type_of_input_value.lower():
                case "list":
                    answer = self.remove_extra_zeroes_list(input_value)
                case "dict":
                    answer = self.remove_extra_zeroes_dict(input_value)
                case "float":
                    answer = self.remove_extra_zeroes_float(input_value)
            
            logger.debug(
                f"{colorama.Fore.YELLOW}{input_value} {colorama.Fore.MAGENTA}has {type_of_input_value} type. Try to remove extra zeroes for float values in it."
            )

            return answer
        except Exception as ex:
            logger.error(f"error with removing extra zeroes: {ex}")
            return input_value


    @logger.catch
    def solve_math_expression(self, expression: str,
                              show_solving_steps: bool,
                              render_latex_expressions: bool
                              ) -> Union[float, Dict, List[Any]]:
        '''
        solving any math expressions,
        equations and returns the result.
        --------------------------------
        there is two ways of solving:
        1. a unique solution algorithm has
        been written for a specific type
        of expression/equation
        2. an adaptive solution algorithm that
        does not provide the output of each
        step in the solution.
        '''
        parsed = parse_string_to_latex(expression)

        # Here we using unique alghoritms to solve specific type of expression
        if self.using_alghoritms and self._is_quadratic_equation(parsed):
            answer = QuadraticEquationSolver.solve_quadratic_equation(parsed)

            results = answer['results']
            if show_solving_steps:
                solving_steps = answer['solving_steps']
            else:
                solving_steps = ["None"]

            str_results = [str(root) for root in results]
            str_steps = [str(step) for step in solving_steps]

            return {
                "results": str_results,
                "solving_steps": str_steps
            }
        
        # Here an adaptive one
        if self._is_equation(parsed):
            result = sympy.solve(parsed)
        else:
            result = parsed.evalf()

        str_results = [str(root) for root in result]

        return {
                "results": self.remove_extra_zeroes_for_answer(str_results),
                "solving_steps": ["None"]
            }
         
