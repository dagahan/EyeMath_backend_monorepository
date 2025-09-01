import re
from typing import Dict, List, Optional, Any
from loguru import logger

from .visma_engine import VismaEngine


class LaTeXToVismaConverter:
    """Converts LaTeX expressions to Visma format."""
    
    def __init__(self):
        """Initialize converter."""
        self.conversion_map = {
            # Basic operators
            r'\\times': '*',
            r'\\div': '/',
            r'\\cdot': '*',
            r'\\pm': '+/-',
            r'\\mp': '-/+',
            
            # Comparison operators
            r'\\leq': '<=',
            r'\\geq': '>=',
            r'\\neq': '!=',
            r'\\approx': '~=',
            
            # Functions
            r'\\sin': 'sin',
            r'\\cos': 'cos',
            r'\\tan': 'tan',
            r'\\cot': 'cot',
            r'\\sec': 'sec',
            r'\\csc': 'csc',
            r'\\arcsin': 'arcsin',
            r'\\arccos': 'arccos',
            r'\\arctan': 'arctan',
            r'\\sinh': 'sinh',
            r'\\cosh': 'cosh',
            r'\\tanh': 'tanh',
            r'\\log': 'log',
            r'\\ln': 'ln',
            r'\\exp': 'exp',
            r'\\sqrt': 'sqrt',
            r'\\abs': 'abs',
            r'\\max': 'max',
            r'\\min': 'min',
            
            # Greek letters
            r'\\alpha': 'alpha',
            r'\\beta': 'beta',
            r'\\gamma': 'gamma',
            r'\\delta': 'delta',
            r'\\epsilon': 'epsilon',
            r'\\zeta': 'zeta',
            r'\\eta': 'eta',
            r'\\theta': 'theta',
            r'\\iota': 'iota',
            r'\\kappa': 'kappa',
            r'\\lambda': 'lambda',
            r'\\mu': 'mu',
            r'\\nu': 'nu',
            r'\\xi': 'xi',
            r'\\pi': 'pi',
            r'\\rho': 'rho',
            r'\\sigma': 'sigma',
            r'\\tau': 'tau',
            r'\\upsilon': 'upsilon',
            r'\\phi': 'phi',
            r'\\chi': 'chi',
            r'\\psi': 'psi',
            r'\\omega': 'omega',
            
            # Constants
            r'\\infty': 'inf',
            r'\\partial': 'partial',
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {
            key: re.compile(key) for key in self.conversion_map.keys()
        }
    
    
    def convert(self, latex_expr: str) -> str:
        """
        Convert LaTeX expression to Visma format.
        
        Args:
            latex_expr: LaTeX mathematical expression
            
        Returns:
            Visma-compatible expression
        """
        if not latex_expr:
            return ""
        
        visma_expr = latex_expr
        
        # Step 1: Handle fractions
        visma_expr = self._convert_fractions(visma_expr)
        
        # Step 2: Handle radicals
        visma_expr = self._convert_radicals(visma_expr)
        
        # Step 3: Handle superscripts and subscripts
        visma_expr = self._convert_superscripts_subscripts(visma_expr)
        
        # Step 4: Handle functions
        visma_expr = self._convert_functions(visma_expr)
        
        # Step 5: Replace LaTeX symbols
        visma_expr = self._replace_symbols(visma_expr)
        
        # Step 6: Clean up parentheses and brackets
        visma_expr = self._clean_parentheses(visma_expr)
        
        # Step 7: Final cleanup
        visma_expr = self._final_cleanup(visma_expr)
        
        logger.debug(f"Converted LaTeX '{latex_expr}' to Visma format '{visma_expr}'")
        return visma_expr
    

    def _convert_fractions(self, expr: str) -> str:
        """Convert LaTeX fractions to Visma format."""
        # Handle \frac{a}{b} -> (a)/(b)
        frac_pattern = r'\\frac\{([^{}]+)\}\{([^{}]+)\}'
        
        def replace_frac(match):
            numerator = match.group(1)
            denominator = match.group(2)
            return f"({numerator})/({denominator})"
        
        return re.sub(frac_pattern, replace_frac, expr)
    

    def _convert_radicals(self, expr: str) -> str:
        """Convert LaTeX radicals to Visma format."""
        # Handle \sqrt{x} -> sqrt(x)
        sqrt_pattern = r'\\sqrt\{([^{}]+)\}'
        
        def replace_sqrt(match):
            radicand = match.group(1)
            return f"sqrt({radicand})"
        
        return re.sub(sqrt_pattern, replace_sqrt, expr)
    

    def _convert_superscripts_subscripts(self, expr: str) -> str:
        """Convert LaTeX superscripts and subscripts."""
        # Handle ^{power} -> ^power
        superscript_pattern = r'\^\{([^{}]+)\}'
        expr = re.sub(superscript_pattern, r'^\1', expr)
        
        # Handle ^{} -> ^
        expr = re.sub(r'\^\{\}', '^', expr)
        
        # Handle _{subscript} -> _subscript
        subscript_pattern = r'_\{([^{}]+)\}'
        expr = re.sub(subscript_pattern, r'_\1', expr)
        
        return expr
    

    def _convert_functions(self, expr: str) -> str:
        """Convert LaTeX functions to Visma format."""
        # Handle function calls like \sin(x) -> sin(x)
        for latex_func, visma_func in self.conversion_map.items():
            if latex_func.startswith('\\') and not latex_func.endswith('}'):
                # This is a function name
                pattern = latex_func + r'\{([^{}]+)\}'
                replacement = f"{visma_func}(\\1)"
                expr = re.sub(pattern, replacement, expr)
        
        return expr
    

    def _replace_symbols(self, expr: str) -> str:
        """Replace LaTeX symbols with Visma equivalents."""
        for latex_sym, visma_sym in self.conversion_map.items():
            if latex_sym in self.compiled_patterns:
                expr = self.compiled_patterns[latex_sym].sub(visma_sym, expr)
        
        return expr
    

    def _clean_parentheses(self, expr: str) -> str:
        """Clean up parentheses and brackets."""
        # Replace { } with ( )
        expr = expr.replace('{', '(').replace('}', ')')
        
        # Remove unnecessary spaces around operators
        expr = re.sub(r'\s*([+\-*/^=<>!])\s*', r'\1', expr)
        
        return expr
    

    def _final_cleanup(self, expr: str) -> str:
        """Final cleanup of the expression."""
        # Remove extra whitespace
        expr = re.sub(r'\s+', ' ', expr).strip()
        
        # Remove spaces around parentheses
        expr = re.sub(r'\s*\(\s*', '(', expr)
        expr = re.sub(r'\s*\)\s*', ')', expr)
        
        # Remove spaces around commas
        expr = re.sub(r'\s*,\s*', ',', expr)
        
        return expr


class VismaToLaTeXConverter:
    """Converts Visma results back to LaTeX format."""
    
    def __init__(self):
        """Initialize converter."""
        self.conversion_map = {
            # Basic operators
            '*': r'\\cdot',
            '/': r'\\div',
            '+/-': r'\\pm',
            '-/+': r'\\mp',
            
            # Comparison operators
            '<=': r'\\leq',
            '>=': r'\\geq',
            '!=': r'\\neq',
            '~=': r'\\approx',
            
            # Functions
            'sin': r'\\sin',
            'cos': r'\\cos',
            'tan': r'\\tan',
            'cot': r'\\cot',
            'sec': r'\\sec',
            'csc': r'\\csc',
            'arcsin': r'\\arcsin',
            'arccos': r'\\arccos',
            'arctan': r'\\arctan',
            'sinh': r'\\sinh',
            'cosh': r'\\cosh',
            'tanh': r'\\tanh',
            'log': r'\\log',
            'ln': r'\\ln',
            'exp': r'\\exp',
            'sqrt': r'\\sqrt',
            'abs': r'\\abs',
            'max': r'\\max',
            'min': r'\\min',
            
            # Greek letters
            'alpha': r'\\alpha',
            'beta': r'\\beta',
            'gamma': r'\\gamma',
            'delta': r'\\delta',
            'epsilon': r'\\epsilon',
            'zeta': r'\\zeta',
            'eta': r'\\eta',
            'theta': r'\\theta',
            'iota': r'\\iota',
            'kappa': r'\\kappa',
            'lambda': r'\\lambda',
            'mu': r'\\mu',
            'nu': r'\\nu',
            'xi': r'\\xi',
            'pi': r'\\pi',
            'rho': r'\\rho',
            'sigma': r'\\sigma',
            'tau': r'\\tau',
            'upsilon': r'\\upsilon',
            'phi': r'\\phi',
            'chi': r'\\chi',
            'psi': r'\\psi',
            'omega': r'\\omega',
            
            # Constants
            'inf': r'\\infty',
            'partial': r'\\partial',
        }
    

    def convert(self, visma_expr: str) -> str:
        """
        Convert Visma expression to LaTeX format.
        
        Args:
            visma_expr: Visma mathematical expression
            
        Returns:
            LaTeX formatted expression
        """
        if not visma_expr:
            return ""
        
        latex_expr = visma_expr
        
        # Step 1: Handle fractions
        latex_expr = self._convert_fractions(latex_expr)
        
        # Step 2: Handle radicals
        latex_expr = self._convert_radicals(latex_expr)
        
        # Step 3: Handle functions
        latex_expr = self._convert_functions(latex_expr)
        
        # Step 4: Replace Visma symbols
        latex_expr = self._replace_symbols(latex_expr)
        
        # Step 5: Clean up formatting
        latex_expr = self._clean_formatting(latex_expr)
        
        logger.debug(f"Converted Visma '{visma_expr}' to LaTeX '{latex_expr}'")
        return latex_expr
    

    def _convert_fractions(self, expr: str) -> str:
        """Convert Visma fractions to LaTeX format."""
        # Handle (a)/(b) -> \frac{a}{b}
        frac_pattern = r'\(([^)]+)\)/\(([^)]+)\)'
        
        def replace_frac(match):
            numerator = match.group(1)
            denominator = match.group(2)
            return f"\\frac{{{numerator}}}{{{denominator}}}"
        
        return re.sub(frac_pattern, replace_frac, expr)
    

    def _convert_radicals(self, expr: str) -> str:
        """Convert Visma radicals to LaTeX format."""
        # Handle sqrt(x) -> \sqrt{x}
        sqrt_pattern = r'sqrt\(([^)]+)\)'
        
        def replace_sqrt(match):
            radicand = match.group(1)
            return f"\\sqrt{{{radicand}}}"
        
        return re.sub(sqrt_pattern, replace_sqrt, expr)
    

    def _convert_functions(self, expr: str) -> str:
        """Convert Visma functions to LaTeX format."""
        # Handle function calls like sin(x) -> \sin(x)
        for visma_func, latex_func in self.conversion_map.items():
            if visma_func in ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln', 'exp']:
                pattern = f"{visma_func}\\("
                replacement = f"{latex_func}("
                expr = expr.replace(pattern, replacement)
        
        return expr
    

    def _replace_symbols(self, expr: str) -> str:
        """Replace Visma symbols with LaTeX equivalents."""
        for visma_sym, latex_sym in self.conversion_map.items():
            expr = expr.replace(visma_sym, latex_sym)
        
        return expr
    

    def _clean_formatting(self, expr: str) -> str:
        """Clean up LaTeX formatting."""
        # Add spaces around operators for better readability
        expr = re.sub(r'([+\-*/=<>!])(?=[^\s])', r'\1 ', expr)
        expr = re.sub(r'(?<=[^\s])([+\-*/=<>!])', r' \1', expr)
        
        # Clean up multiple spaces
        expr = re.sub(r'\s+', ' ', expr).strip()
        
        return expr


class VismaLaTeXEngine:
    """
    Visma Engine with LaTeX integration.
    
    Provides seamless LaTeX support for the Visma mathematical engine.
    """
    
    def __init__(self):
        """Initialize LaTeX-integrated Visma engine."""
        self.engine = VismaEngine()
        self.latex_to_visma = LaTeXToVismaConverter()
        self.visma_to_latex = VismaToLaTeXConverter()
    

    def solve_latex(
        self,
        latex_expression: str,
        operation: str = 'simplify',
        show_steps: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Solve LaTeX mathematical expression.
        
        Args:
            latex_expression: LaTeX mathematical expression
            operation: Operation to perform
            show_steps: Whether to include solving steps
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing results and metadata
        """
        try:
            # Convert LaTeX to Visma format
            visma_expr = self.latex_to_visma.convert(latex_expression)
            
            # Execute operation
            result = self.engine.execute_operation(operation, visma_expr, **kwargs)
            
            # Convert results back to LaTeX
            latex_results = []
            for visma_result in result['results']:
                latex_result = self.visma_to_latex.convert(str(visma_result))
                latex_results.append(latex_result)
            
            # Generate solving steps if requested
            solving_steps = []
            if show_steps and result['success']:
                solving_steps = self._generate_solving_steps(
                    latex_expression, visma_expr, result, operation
                )
            
            return {
                'results': latex_results,
                'solving_steps': solving_steps,
                'operation_used': operation,
                'visma_command': f"{operation}({visma_expr})",
                'raw_visma_output': '\n'.join(solving_steps),
                'success': result['success'],
                'error': result.get('error')
            }
            
        except Exception as e:
            logger.error(f"LaTeX solving failed: {e}")
            return {
                'results': [latex_expression],
                'solving_steps': [f"Error: {str(e)}"],
                'operation_used': operation,
                'visma_command': f"{operation}({latex_expression})",
                'raw_visma_output': f"Error: {str(e)}",
                'success': False,
                'error': str(e)
            }


    def _generate_solving_steps(
        self,
        original_latex: str,
        visma_expr: str,
        result: Dict[str, Any],
        operation: str
    ) -> List[str]:
        """Generate solving steps for the operation."""
        steps = []
        
        if operation == 'simplify':
            steps.append(f"Simplifying: {original_latex}")
            steps.append(f"Converted to: {visma_expr}")
            if result['success']:
                steps.append(f"Result: {result['results'][0]}")
            else:
                steps.append(f"Error: {result.get('error', 'Unknown error')}")
        
        elif operation == 'solve':
            steps.append(f"Solving equation: {original_latex}")
            steps.append(f"Converted to: {visma_expr}")
            if result['success']:
                for solution in result['results']:
                    steps.append(f"Solution: {solution}")
            else:
                steps.append(f"Error: {result.get('error', 'Unknown error')}")
        
        elif operation == 'factorize':
            steps.append(f"Factorizing: {original_latex}")
            steps.append(f"Converted to: {visma_expr}")
            if result['success']:
                steps.append(f"Factored form: {result['results'][0]}")
            else:
                steps.append(f"Error: {result.get('error', 'Unknown error')}")
        
        return steps

