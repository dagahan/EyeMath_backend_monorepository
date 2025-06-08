import colorama, sympy

from sympy import Eq, Symbol, preorder_traversal, solve
from sympy.parsing.latex import parse_latex
from mpmath import mp
from loguru import logger

from src.core.config import ConfigLoader




class MathSolver:
    def __init__(self):
        self.config = ConfigLoader()
        mp.dps = self.config.get("MaL", "precision")
     

    @logger.catch
    def _is_equation(self, expr):
        logger.debug(f"{colorama.Fore.MAGENTA}Checking if {colorama.Fore.YELLOW}{expr} {colorama.Fore.MAGENTA}is an equation...")
        if isinstance(expr, Eq):
            logger.debug(f"{colorama.Fore.YELLOW}{expr} {colorama.Fore.MAGENTA}is an equation.")
            return True
        return any(isinstance(node, Symbol) for node in preorder_traversal(expr))
    

    @logger.catch
    def RevomeExtraZeroesFloat(self, value):
        if isinstance(value, (sympy.core.numbers.Float)):
            value = float(str(value).strip("0"))
        return value


    @logger.catch    #this we call 'decorator'
    def SolveExpression(self, request):
        parsed = parse_latex(request.expression)


        logger.debug(f"{parsed}")
        # to_return = sympy.sqrt(parsed)

        if self._is_equation(parsed):
            answer = sympy.solve(parsed)
        else:
            answer = parsed.evalf()


        answer = self.RevomeExtraZeroesFloat(answer)

        return answer
    

    





    @logger.catch
    def SolveExpressionDebugMode(self, request):
        parsed = parse_latex(request.expression)


        logger.debug(f"{parsed}")
        # to_return = sympy.sqrt(parsed)

        if self._is_equation(parsed):
            answer = sympy.solve(parsed)
        else:
            answer = parsed.evalf()


        answer = self.RevomeExtraZeroesFloat(answer)

        return answer
