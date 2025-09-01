"""
Visma Integration for EyeMath Solver

This module provides integration with the original Visma mathematical engine,
converting LaTeX input to Visma format, solving, and returning LaTeX output.
"""

import sys
import os
from typing import Dict, List, Any, Optional
from loguru import logger

# Add the visma module to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
visma_path = current_dir  # The visma directory is in the same directory as this file
if visma_path not in sys.path:
    sys.path.insert(0, visma_path)

# Import original Visma modules
from visma.io.tokenize import tokenizer, getLHSandRHS
from visma.io.parser import tokensToString, tokensToLatex
from visma.simplify.simplify import simplify, simplifyEquation
from visma.solvers.solve import solveFor
from visma.solvers.polynomial.roots import rootFinder
from visma.transform.factorization import factorize
from visma.calculus.differentiation import differentiate
from visma.calculus.integration import integrate
from visma.io.checks import checkTypes, isEquation


class VismaIntegration:
    """
    Visma Mathematical Engine Integration
    
    Provides seamless integration with the original Visma engine
    for LaTeX input/output mathematical solving.
    """
    
    def __init__(self):
        """Initialize the Visma integration."""
        self.supported_operations = [
            'simplify', 'solve', 'factorize', 'find-roots',
            'differentiate', 'integrate'
        ]
    
    def solve_expression(
        self,
        latex_expression: str,
        operation: str = 'simplify',
        variable: Optional[str] = None,
        show_steps: bool = True
    ) -> Dict[str, Any]:
        """
        Solve mathematical expression using Visma engine.
        
        Args:
            latex_expression: LaTeX mathematical expression
            operation: Operation to perform
            variable: Variable for solving/differentiation/integration
            show_steps: Whether to include solving steps
            
        Returns:
            Dictionary containing results and metadata
        """
        try:
            # Convert LaTeX to Visma format
            visma_expression = self._latex_to_visma(latex_expression)
            
            # Execute operation using original Visma
            result = self._execute_visma_operation(
                visma_expression, operation, variable, show_steps
            )
            
            # Convert results back to LaTeX
            latex_results = []
            for visma_result in result['results']:
                latex_result = self._visma_to_latex(str(visma_result))
                latex_results.append(latex_result)
            
            return {
                'results': latex_results,
                'solving_steps': result['solving_steps'],
                'operation_used': operation,
                'visma_command': f"{operation}({visma_expression})",
                'raw_visma_output': result['raw_output'],
                'success': result['success'],
                'error': result.get('error')
            }
            
        except Exception as e:
            logger.error(f"Visma solving failed: {e}")
            return {
                'results': [latex_expression],
                'solving_steps': [f"Error: {str(e)}"],
                'operation_used': operation,
                'visma_command': f"{operation}({latex_expression})",
                'raw_visma_output': f"Error: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def _execute_visma_operation(
        self,
        expression: str,
        operation: str,
        variable: Optional[str] = None,
        show_steps: bool = True
    ) -> Dict[str, Any]:
        """Execute operation using original Visma functionality."""
        
        # Tokenize the expression
        tokens = tokenizer(expression)
        
        # Check if it's an equation
        is_eq = '=' in expression
        lhs, rhs = getLHSandRHS(tokens) if is_eq else ([], [])
        
        equation_tokens = []
        comments = []
        solution_type = ''
        
        try:
            if operation == 'simplify':
                if is_eq:
                    l_tokens, r_tokens, _, _, equation_tokens, comments = simplifyEquation(lhs, rhs)
                else:
                    tokens, _, _, equation_tokens, comments = simplify(tokens)
                    
            elif operation == 'solve':
                if not is_eq:
                    raise ValueError("Solve operation requires an equation")
                if not variable:
                    # Try to detect variable
                    variable = self._detect_variable(tokens)
                l_tokens, r_tokens, _, _, equation_tokens, comments = solveFor(lhs, rhs, variable)
                
            elif operation == 'find-roots':
                if not is_eq:
                    raise ValueError("Find-roots operation requires an equation")
                l_tokens, r_tokens, _, _, equation_tokens, comments = rootFinder(lhs, rhs)
                
            elif operation == 'factorize':
                tokens, _, _, equation_tokens, comments = factorize(tokens)
                
            elif operation == 'differentiate':
                if not variable:
                    variable = self._detect_variable(tokens)
                l_tokens, _, _, equation_tokens, comments = differentiate(lhs, variable)
                
            elif operation == 'integrate':
                if not variable:
                    variable = self._detect_variable(tokens)
                l_tokens, _, _, equation_tokens, comments = integrate(lhs, variable)
                
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Generate results
            if equation_tokens:
                results = []
                solving_steps = []
                
                for i, step_tokens in enumerate(equation_tokens):
                    result_str = tokensToString(step_tokens)
                    results.append(result_str)
                    
                    if show_steps and i < len(comments):
                        step_comment = comments[i] if comments[i] else [f"Step {i+1}"]
                        solving_steps.extend(step_comment)
                
                # Final result
                final_result = results[-1] if results else expression
                
                return {
                    'results': [final_result],
                    'solving_steps': solving_steps,
                    'raw_output': '\n'.join(results),
                    'success': True
                }
            else:
                return {
                    'results': [expression],
                    'solving_steps': ["No steps available"],
                    'raw_output': expression,
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Visma operation {operation} failed: {e}")
            return {
                'results': [expression],
                'solving_steps': [f"Error: {str(e)}"],
                'raw_output': f"Error: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def _detect_variable(self, tokens) -> str:
        """Detect the main variable in the expression."""
        # Look for variables in tokens
        for token in tokens:
            if hasattr(token, 'value') and isinstance(token.value, str):
                if token.value.isalpha() and len(token.value) == 1:
                    return token.value
        return 'x'  # Default variable
    
    def _latex_to_visma(self, latex_expr: str) -> str:
        """Convert LaTeX expression to Visma format."""
        if not latex_expr:
            return ""
        
        visma_expr = latex_expr
        
        # Handle common LaTeX to Visma conversions
        conversions = {
            r'\\times': '*',
            r'\\cdot': '*',
            r'\\div': '/',
            r'\\frac\{([^{}]+)\}\{([^{}]+)\}': r'(\1)/(\2)',
            r'\\sqrt\{([^{}]+)\}': r'sqrt(\1)',
            r'\^\{([^{}]+)\}': r'^\1',
            r'_\{([^{}]+)\}': r'_\1',
            r'\\sin': 'sin',
            r'\\cos': 'cos',
            r'\\tan': 'tan',
            r'\\log': 'log',
            r'\\ln': 'ln',
            r'\\exp': 'exp',
            r'\\pi': 'pi',
            r'\\infty': 'inf',
        }
        
        import re
        for latex_pattern, visma_replacement in conversions.items():
            visma_expr = re.sub(latex_pattern, visma_replacement, visma_expr)
        
        # Clean up braces
        visma_expr = visma_expr.replace('{', '(').replace('}', ')')
        
        # Remove extra spaces
        visma_expr = re.sub(r'\s+', ' ', visma_expr).strip()
        
        logger.debug(f"Converted LaTeX '{latex_expr}' to Visma format '{visma_expr}'")
        return visma_expr
    
    def _visma_to_latex(self, visma_expr: str) -> str:
        """Convert Visma expression to LaTeX format."""
        if not visma_expr:
            return ""
        
        latex_expr = visma_expr
        
        # Handle common Visma to LaTeX conversions
        conversions = {
            r'\*': r'\\cdot',
            r'sqrt\(([^)]+)\)': r'\\sqrt{\1}',
            r'sin\(([^)]+)\)': r'\\sin(\1)',
            r'cos\(([^)]+)\)': r'\\cos(\1)',
            r'tan\(([^)]+)\)': r'\\tan(\1)',
            r'log\(([^)]+)\)': r'\\log(\1)',
            r'ln\(([^)]+)\)': r'\\ln(\1)',
            r'exp\(([^)]+)\)': r'\\exp(\1)',
            r'pi': r'\\pi',
            r'inf': r'\\infty',
        }
        
        import re
        for visma_pattern, latex_replacement in conversions.items():
            latex_expr = re.sub(visma_pattern, latex_replacement, latex_expr)
        
        # Handle fractions
        frac_pattern = r'\(([^)]+)\)/\(([^)]+)\)'
        latex_expr = re.sub(frac_pattern, r'\\frac{\1}{\2}', latex_expr)
        
        # Clean up formatting
        latex_expr = re.sub(r'\s*([+\-*/=<>!])\s*', r' \1 ', latex_expr)
        latex_expr = re.sub(r'\s+', ' ', latex_expr).strip()
        
        logger.debug(f"Converted Visma '{visma_expr}' to LaTeX '{latex_expr}'")
        return latex_expr
    
    def is_available(self) -> bool:
        """Check if the Visma engine is available."""
        try:
            # Test basic functionality
            test_tokens = tokenizer("x^2 + 2*x + 1")
            return len(test_tokens) > 0
        except Exception as e:
            logger.error(f"Visma engine not available: {e}")
            return False
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations."""
        return self.supported_operations.copy()