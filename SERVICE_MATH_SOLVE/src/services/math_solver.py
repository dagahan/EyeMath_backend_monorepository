from typing import Any, Dict, List, Union

import colorama
import sympy
from loguru import logger
from mpmath import mp
from sympy import Eq, Symbol, preorder_traversal
from sympy.parsing.latex import parse_latex as parse_string_to_latex

from src.core.config import ConfigLoader
from src.core.utils import MethodTools


class MathSolver:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        mp.dps = self.config.get("MaL", "precision")


    @logger.catch
    def _is_equation(self, expr: str) -> bool:
        logger.debug(
            f"{colorama.Fore.MAGENTA}Checking if {colorama.Fore.YELLOW}{expr} {colorama.Fore.MAGENTA}is an equation..."
        )
        if isinstance(expr, Eq):
            logger.debug(
                f"{colorama.Fore.YELLOW}{expr} {colorama.Fore.MAGENTA}is an equation."
            )
            return True
        return any(isinstance(node, Symbol) for node in preorder_traversal(expr))


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
            logger.error(f"error with {MethodTools.name_of_method(1)}: {ex}")
            return input_value


    @logger.catch
    def solve_math_expression(self, request: Any) -> Union[float, Dict, List[Any]]:
        '''
        solving any math expressions,
        equations and returns the result.
        '''
        parsed = parse_string_to_latex(request.expression)

        logger.debug(f"{parsed}")
        # to_return = sympy.sqrt(parsed)

        if self._is_equation(parsed):
            answer = sympy.solve(parsed)
        else:
            answer = parsed.evalf()

        return self.remove_extra_zeroes_float(answer)








    @logger.catch
    def solve_math_expression_debug(self, request: Any) -> Union[float, Dict, List[Any]]:
        # TODO: we needed to remove extra zeroes for every object of list or dict in answer
        parsed = parse_string_to_latex(request.expression)

        logger.debug(f"{parsed}")
        # to_return = sympy.sqrt(parsed)

        if self._is_equation(parsed):
            answer = sympy.solve(parsed)
        else:
            answer = parsed.evalf()
        
        return self.remove_extra_zeroes_for_answer(answer)
         
