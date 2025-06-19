from typing import Any, Dict, List, Union

import colorama
import sympy
from loguru import logger
from mpmath import mp
from sympy import Eq, Poly, Symbol, preorder_traversal
from sympy.parsing.latex import parse_latex as parse_string_to_latex

from src.core.config import ConfigLoader
from src.core.utils import MethodTools
from src.grpc.client.factory_grpc_client import GRPCClientFactory
from src.services.alghoritms.quadratic_equations import QuadraticEquationSolver


class MathSolver:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        mp.dps = self.config.get("math", "precision")
        self.using_algorithms = self.config.get("math", "using_algorithms_solving")


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
    def remove_extra_zeroes_for_answer(
        self,
        input_value: Union[float, Dict, List[Any]]
        ) -> Union[float, Dict, List[Any]]:
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
    def solve_math_expression(
        self,
        expression: str,
        show_solving_steps: bool,
        render_latex_expressions: bool
    ) -> Dict[str, List]:
        parsed_expression = parse_string_to_latex(expression)
        
        if self.using_algorithms and self._is_quadratic_equation(parsed_expression):
            return self._handle_quadratic_case(
                parsed_expression,
                show_solving_steps,
                render_latex_expressions
            )
        return self._handle_general_case(
            parsed_expression,
            render_latex_expressions
        )


    def _handle_quadratic_case(
        self,
        parsed_expr,
        show_steps,
        render_latex
    ) -> Dict[str, List]:
        answer = QuadraticEquationSolver.solve_quadratic_equation(parsed_expr)
        results = answer['results']
        solving_steps = answer['solving_steps'] if show_steps else ["None"]
        
        str_results = self._convert_results_to_strings(results, clean_zeros=False)
        renders = self._generate_renders(str_results, render_latex)
        
        return {
            "results": str_results,
            "renders": renders,
            "solving_steps": [str(step) for step in solving_steps]
        }


    def _handle_general_case(
        self,
        parsed_expr,
        render_latex
    ) -> Dict[str, List]:
        if self._is_equation(parsed_expr):
            result = sympy.solve(parsed_expr)
            solutions = list(result.values()) if isinstance(result, dict) else result
            solutions = solutions if isinstance(solutions, list) else [solutions]
        else:
            solutions = [parsed_expr.evalf()]
        
        str_results = self._convert_results_to_strings(solutions, clean_zeros=True)
        renders = self._generate_renders(str_results, render_latex)
        
        return {
            "results": str_results,
            "renders": renders,
            "solving_steps": ["None"]
        }


    def _convert_results_to_strings(
        self,
        results: Union[List, Any],
        clean_zeros: bool = False
    ) -> List[str]:
        if not isinstance(results, list):
            results = [results]
        
        str_results = [str(item) for item in results]
        
        if clean_zeros:
            str_results = self.remove_extra_zeroes_for_answer(str_results)
        
        return str_results


    def _generate_renders(
        self,
        str_results: List[str],
        render_latex: bool
    ) -> List[str]:
        if not render_latex:
            return ["None"] * len(str_results)
        
        return [
            self._render_latex(expr)
            for expr in str_results
        ]


    def _render_latex(self, expression: str) -> str:
        response = GRPCClientFactory.rpc_call(
            service_name="math_render",
            method_name="render_latex",
            latex_expression=expression,
        )
        return response.render_image
                
