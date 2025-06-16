from loguru import logger
import sympy
from sympy import Eq, Poly, sqrt, simplify, Symbol
from typing import Dict, List, Tuple, Union


class QuadraticEquationSolver:
    @staticmethod
    def solve_quadratic_equation(equation: Eq) -> Dict[str, Union[List[Union[float, complex]], List[str]]]:
        '''
        Solves a quadratic equation and generates human-readable solution steps.
        Args:
            equation: SymPy equation to solve
        Returns:
            Dictionary containing:
            - 'results': List of solution roots
            - 'solving_steps': List of human-readable solution steps in LaTeX
        '''
        try:
            variable = QuadraticEquationSolver._extract_variable(equation)
            a, b, c = QuadraticEquationSolver._get_coefficients(equation, variable)
            discriminant = QuadraticEquationSolver._calculate_discriminant(a, b, c)
            
            steps = QuadraticEquationSolver._build_solution_steps(
                equation, variable, a, b, c, discriminant
            )
            
            root1, root2 = QuadraticEquationSolver._calculate_roots(
                a, b, discriminant
            )
            
            return {
                'results': [root1, root2],
                'solving_steps': steps
            }
        
        except Exception as error:
            logger.error(f"Error solving quadratic equation: {error}")
            return {
                'results': ['None'],
                'solving_steps': [f"Error solving quadratic equation"]
            }


    @staticmethod
    def _extract_variable(equation: Eq) -> Symbol:
        '''
        Extracts the variable symbol from the equation.
        '''
        expression = equation.lhs - equation.rhs
        symbols = expression.free_symbols
        
        if not symbols:
            raise ValueError("No variables found in the equation")
        if len(symbols) > 1:
            raise ValueError("Equation must contain exactly one variable")
            
        return next(iter(symbols))


    @staticmethod
    def _get_coefficients(equation: Eq, variable: Symbol) -> Tuple[float, float, float]:
        '''
        Extracts coefficients a, b, c from the quadratic equation.
        '''
        expression = equation.lhs - equation.rhs
        poly = Poly(expression, variable)
        
        return (
            poly.coeff_monomial(variable**2),
            poly.coeff_monomial(variable),
            poly.coeff_monomial(1)
        )


    @staticmethod
    def _calculate_discriminant(a: float, b: float, c: float) -> float:
        '''
        Calculates the discriminant of the quadratic equation.
        '''
        return b**2 - 4*a*c


    @staticmethod
    def _build_solution_steps(
        equation: Eq,
        variable: Symbol,
        a: float,
        b: float,
        c: float,
        discriminant: float
    ) -> List[str]:
        '''
        Generates human-readable solution steps in LaTeX format.
        '''

        expression = equation.lhs - equation.rhs
        
        return [
            f"Original equation: {sympy.latex(equation)}",
            f"Standard form: {sympy.latex(Eq(expression, 0))}",
            f"Coefficients: a = {a}, b = {b}, c = {c}",
            (
                "Discriminant: D = b² - 4ac = "
                f"({b})² - 4⋅{a}⋅{c} = {discriminant}"
            ),
            QuadraticEquationSolver._get_discriminant_analysis(discriminant)
        ]


    @staticmethod
    def _get_discriminant_analysis(discriminant: float) -> str:
        '''
        Returns analysis of the discriminant value.
        '''
        if discriminant < 0:
            return "D < 0: Complex roots"
        if discriminant == 0:
            return "D = 0: One real root"
        return "D > 0: Two real roots"


    @staticmethod
    def _calculate_roots(
        a: float, 
        b: float, 
        discriminant: float
    ) -> Tuple[Union[float, complex], Union[float, complex]]:
        """Calculates the roots of the quadratic equation."""
        sqrt_d = sqrt(discriminant)
        return (
            (-b + sqrt_d) / (2*a),
            (-b - sqrt_d) / (2*a)
        )