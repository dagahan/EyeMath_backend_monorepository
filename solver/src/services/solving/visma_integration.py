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
                
                # Process final result based on operation type
                final_result = results[-1] if results else expression
                
                # Post-process results for better formatting
                if operation == 'find-roots':
                    # Use raw output for better root extraction
                    raw_output = '\n'.join(results)
                    final_result = self._extract_roots_from_result(final_result, variable or 'x', expression, raw_output)
                elif operation == 'solve':
                    final_result = self._simplify_solution(final_result)
                
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
    
    def _extract_roots_from_result(self, result: str, variable: str, original_expression: str = "", raw_output: str = "") -> str:
        """Extract individual roots from Visma's result."""
        import re
        
        # First, try to extract roots from raw output if available
        if raw_output:
            # First, check for difference of squares pattern like (x + 2.0) * (x - 2.0) = 0
            diff_squares_pattern = rf'\(({variable})\s*\+\s*([0-9.-]+)\)\s*\*\s*\(({variable})\s*-\s*([0-9.-]+)\)\s*=\s*0'
            diff_match = re.search(diff_squares_pattern, raw_output)
            
            if diff_match:
                try:
                    pos_value = float(diff_match.group(2))
                    neg_value = float(diff_match.group(4))
                    
                    # Check if they're the same (difference of squares)
                    if abs(pos_value - neg_value) < 1e-10:
                        if pos_value.is_integer():
                            return f"{variable} = ±{int(pos_value)}"
                        else:
                            return f"{variable} = ±{pos_value}"
                except ValueError:
                    pass
            
            # Then look for patterns like (x - 2.0) * (x - 3.0) = 0 in raw output
            root_pattern = rf'\(({variable})\s*-\s*([0-9.-]+)\)'
            matches = re.findall(root_pattern, raw_output)
            
            if matches:
                roots = []
                for var, value in matches:
                    try:
                        # Convert to float and back to clean format
                        num_value = float(value)
                        if num_value.is_integer():
                            roots.append(f"{variable} = {int(num_value)}")
                        else:
                            roots.append(f"{variable} = {num_value}")
                    except ValueError:
                        roots.append(f"{variable} = {value}")
                
                if len(roots) > 1:
                    return ", ".join(roots)
                elif len(roots) == 1:
                    return roots[0]
        
        # Fallback to original result processing
        root_pattern = rf'\(({variable})\s*-\s*([0-9.-]+)\)'
        matches = re.findall(root_pattern, result)
        
        if matches:
            roots = []
            for var, value in matches:
                try:
                    # Convert to float and back to clean format
                    num_value = float(value)
                    if num_value.is_integer():
                        roots.append(f"{variable} = {int(num_value)}")
                    else:
                        roots.append(f"{variable} = {num_value}")
                except ValueError:
                    roots.append(f"{variable} = {value}")
            
            if len(roots) > 1:
                return ", ".join(roots)
            elif len(roots) == 1:
                return roots[0]
        
        # Look for patterns like (x + 3.0)^(2) = 0
        # Extract the root: x = -3
        perfect_square_pattern = rf'\(({variable})\s*\+\s*([0-9.-]+)\)\^\(2\)\s*=\s*0'
        perfect_square_match = re.search(perfect_square_pattern, result)
        
        if perfect_square_match:
            try:
                value = float(perfect_square_match.group(2))
                if value.is_integer():
                    return f"{variable} = {-int(value)}"
                else:
                    return f"{variable} = {-value}"
            except ValueError:
                pass
        
        # Look for patterns like (x - 3.0)^(2) = 0
        perfect_square_pattern2 = rf'\(({variable})\s*-\s*([0-9.-]+)\)\^\(2\)\s*=\s*0'
        perfect_square_match2 = re.search(perfect_square_pattern2, result)
        
        if perfect_square_match2:
            try:
                value = float(perfect_square_match2.group(2))
                if value.is_integer():
                    return f"{variable} = {int(value)}"
                else:
                    return f"{variable} = {value}"
            except ValueError:
                pass
        
        # Handle cases like x^2 - 4 = 0 which should give x = ±2
        # This is a special case that needs to be handled differently
        if 'x^2' in result and '= 0' in result:
            # Try to extract the constant term
            const_pattern = r'x\^2\s*-\s*([0-9.-]+)\s*=\s*0'
            const_match = re.search(const_pattern, result)
            if const_match:
                try:
                    const_value = float(const_match.group(1))
                    sqrt_value = const_value ** 0.5
                    if sqrt_value.is_integer():
                        return f"{variable} = ±{int(sqrt_value)}"
                    else:
                        return f"{variable} = ±{sqrt_value}"
                except ValueError:
                    pass
        
        # Handle cases where Visma returns only one root but we know there should be two
        # Check if the original expression was a difference of squares
        if len(result.split(',')) == 1 and original_expression:
            # Check if original expression was x^2 - c = 0 (difference of squares)
            diff_squares_pattern = rf'{variable}\^2\s*-\s*([0-9.-]+)\s*=\s*0'
            diff_match = re.search(diff_squares_pattern, original_expression)
            
            if diff_match:
                try:
                    const_value = float(diff_match.group(1))
                    sqrt_value = const_value ** 0.5
                    
                    # Check if the result matches the positive root
                    single_root_pattern = rf'{variable}\s*=\s*([0-9.-]+)'
                    single_match = re.search(single_root_pattern, result)
                    
                    if single_match:
                        result_value = float(single_match.group(1))
                        if abs(result_value - sqrt_value) < 1e-10:  # They match
                            if sqrt_value.is_integer():
                                return f"{variable} = ±{int(sqrt_value)}"
                            else:
                                return f"{variable} = ±{sqrt_value}"
                except ValueError:
                    pass
        
        # If no roots found, return original result
        return result
    
    def _simplify_solution(self, result: str) -> str:
        """Simplify solution expressions."""
        import re
        
        # Handle cases like x = 0.08333333333333333*(12.0)
        # Convert to x = 1
        pattern = r'x\s*=\s*([0-9.-]+)\*\(([0-9.-]+)\)'
        match = re.search(pattern, result)
        
        if match:
            try:
                coeff = float(match.group(1))
                const = float(match.group(2))
                result_value = coeff * const
                
                if result_value.is_integer():
                    return f"x = {int(result_value)}"
                else:
                    return f"x = {result_value}"
            except ValueError:
                pass
        
        # Handle other simplification cases
        # Remove unnecessary parentheses and simplify expressions
        result = re.sub(r'\(([0-9.-]+)\)', r'\1', result)
        result = re.sub(r'([0-9.-]+)\.0+', r'\1', result)
        
        return result
    
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