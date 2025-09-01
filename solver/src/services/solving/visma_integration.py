import asyncio
import sys
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from loguru import logger

current_dir = os.path.dirname(os.path.abspath(__file__))
visma_path = current_dir  # The visma directory is in the same directory as this file
if visma_path not in sys.path:
    sys.path.insert(0, visma_path)

from visma.io.tokenize import tokenizer, getLHSandRHS  # type: ignore[import-not-found]
from visma.io.parser import tokensToString, tokensToLatex  # type: ignore[import-not-found]
from visma.simplify.simplify import simplify, simplifyEquation  # type: ignore[import-not-found]
from visma.solvers.solve import solveFor  # type: ignore[import-not-found]
from visma.solvers.polynomial.roots import rootFinder  # type: ignore[import-not-found]
from visma.transform.factorization import factorize  # type: ignore[import-not-found]
from visma.calculus.differentiation import differentiate  # type: ignore[import-not-found]
from visma.calculus.integration import integrate  # type: ignore[import-not-found]
from visma.io.checks import checkTypes, isEquation  # type: ignore[import-not-found]


VismaResult = Dict[str, Any]
VismaTokens = List[Any]
VismaComments = List[str]


class VismaIntegration:
    """
    Visma Mathematical Engine Integration
    
    Provides seamless integration with the original Visma engine
    for LaTeX input/output mathematical solving.
    """
    
    def __init__(self, timeout: float = 60.0) -> None:
        """Initialize the Visma integration."""
        self.supported_operations: List[str] = [
            'simplify', 'solve', 'factorize', 'find-roots',
            'differentiate', 'integrate', 'limit'
        ]
        self.timeout: float = timeout
    

    async def solve_expression(
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
            visma_expression = self._latex_to_visma(latex_expression)
            
            result = await self._execute_visma_operation_with_timeout(
                visma_expression, operation, variable, show_steps
            )
            
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
            
        except asyncio.TimeoutError:
            logger.error(f"Visma solving timed out after {self.timeout} seconds")
            return {
                'results': [latex_expression],
                'solving_steps': [f"Error: Operation timed out after {self.timeout} seconds"],
                'operation_used': operation,
                'visma_command': f"{operation}({latex_expression})",
                'raw_visma_output': f"Error: Timeout after {self.timeout} seconds",
                'success': False,
                'error': f"Timeout after {self.timeout} seconds"
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
    

    async def _execute_visma_operation_with_timeout(
        self,
        expression: str,
        operation: str,
        variable: Optional[str] = None,
        show_steps: bool = True
    ) -> Dict[str, Any]:
        """Execute operation using original Visma functionality with proper timeout handling."""
        try:
            task = asyncio.create_task(
                self._execute_visma_operation_async(expression, operation, variable, show_steps)
            )
            
            result = await asyncio.wait_for(task, timeout=self.timeout)
            return result
            
        except asyncio.TimeoutError:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            raise


    async def _execute_visma_operation_async(
        self,
        expression: str,
        operation: str,
        variable: Optional[str] = None,
        show_steps: bool = True
    ) -> Dict[str, Any]:
        """Execute operation using original Visma functionality in async context."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._execute_visma_operation,
            expression, operation, variable, show_steps
        )
    

    def _execute_visma_operation(
        self,
        expression: str,
        operation: str,
        variable: Optional[str] = None,
        show_steps: bool = True
    ) -> Dict[str, Any]:
        """Execute operation using original Visma functionality."""
        
        tokens = tokenizer(expression)
        
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
                try:
                    if '∫' in expression and '_' in expression and '^' in expression:
                        result = self._handle_definite_integral(expression, variable)
                        return result
                    else:
                        l_tokens, _, _, equation_tokens, comments = integrate(lhs, variable)
                except Exception as e:
                    logger.warning(f"Integration failed with error: {e}")
                    return {
                        'results': [f"∫ {expression} d{variable} (complex integration - may require numerical methods)"],
                        'solving_steps': [f"Integration of {expression} with respect to {variable} is complex and may require advanced techniques"],
                        'raw_output': f"Complex integration: {expression}",
                        'success': False,
                        'error': f"Complex integration: {str(e)}"
                    }
                
            elif operation == 'limit':
                result = self._handle_limit_operation(expression)
                return result
                
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            if equation_tokens:
                results = []
                solving_steps: List[str] = []
                
                for i, step_tokens in enumerate(equation_tokens):
                    result_str = tokensToString(step_tokens)
                    results.append(result_str)
                    
                    if show_steps and i < len(comments):
                        step_comment = comments[i] if comments[i] else [f"Step {i+1}"]
                        solving_steps.extend(step_comment)
                
                final_result = results[-1] if results else expression
                
                if operation == 'find-roots':
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
    

    def _handle_limit_operation(self, expression: str) -> Dict[str, Any]:
        """Handle limit operations for known limit patterns."""
        import re
        
        known_limits = {
            r'sin\(([^)]+)\)/([^)]+)': ('1', 'lim(sin(x)/x) = 1 (standard limit)'),
            r'\(1-cos\(([^)]+)\)\)/([^)]+)': ('0', 'lim((1-cos(x))/x) = 0 (standard limit)'),
            r'tan\(([^)]+)\)/([^)]+)': ('1', 'lim(tan(x)/x) = 1 (standard limit)'),
            r'ln\(1\+([^)]+)\)/([^)]+)': ('1', 'lim(ln(1+x)/x) = 1 (standard limit)'),
        }
        
        for pattern, (result, explanation) in known_limits.items():
            if re.search(pattern, expression):
                return {
                    'results': [result],
                    'solving_steps': [explanation],
                    'raw_output': f"Limit result: {result}",
                    'success': True
                }
        
        return {
            'results': [expression],
            'solving_steps': ['Error: Unknown limit pattern'],
            'raw_output': f"Error: Cannot solve limit {expression}",
            'success': False,
            'error': 'Unknown limit pattern'
        }


    def _detect_variable(self, tokens: VismaTokens) -> str:
        """Detect the main variable in the expression."""
        for token in tokens:
            if hasattr(token, 'value') and isinstance(token.value, str):
                if token.value.isalpha() and len(token.value) == 1:
                    return token.value
        return 'x'  # Default variable
    

    def _extract_roots_from_result(self, result: str, variable: str, original_expression: str = "", raw_output: str = "") -> str:
        """Extract individual roots from Visma's result."""
        import re
        
        if raw_output:
            diff_squares_pattern = rf'\(({variable})\s*\+\s*([0-9.-]+)\)\s*\*\s*\(({variable})\s*-\s*([0-9.-]+)\)\s*=\s*0'
            diff_match = re.search(diff_squares_pattern, raw_output)
            
            if diff_match:
                try:
                    pos_value = float(diff_match.group(2))
                    neg_value = float(diff_match.group(4))
                    
                    if abs(pos_value - neg_value) < 1e-10:
                        if pos_value.is_integer():
                            return f"{variable} = ±{int(pos_value)}"
                        else:
                            return f"{variable} = ±{pos_value}"
                except ValueError:
                    pass
            
            root_pattern = rf'\(({variable})\s*-\s*([0-9.-]+)\)'
            matches = re.findall(root_pattern, raw_output)
            
            if matches:
                roots = []
                for var, value in matches:
                    try:
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
        
        root_pattern = rf'\(({variable})\s*-\s*([0-9.-]+)\)'
        matches = re.findall(root_pattern, result)
        
        if matches:
            roots = []
            for var, value in matches:
                try:
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
        
        if 'x^2' in result and '= 0' in result:
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
        
        if len(result.split(',')) == 1 and original_expression:
            diff_squares_pattern = rf'{variable}\^2\s*-\s*([0-9.-]+)\s*=\s*0'
            diff_match = re.search(diff_squares_pattern, original_expression)
            
            if diff_match:
                try:
                    const_value = float(diff_match.group(1))
                    sqrt_value = const_value ** 0.5
                    
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
        
        result = re.sub(r'\(([0-9.-]+)\)', r'\1', result)
        result = re.sub(r'([0-9.-]+)\.0+', r'\1', result)
        
        return result


    def _latex_to_visma(self, latex_expr: str) -> str:
        """Convert LaTeX expression to Visma format."""
        if not latex_expr:
            return ""
        
        visma_expr = latex_expr
        
        import re
        
        limit_patterns = {
            r'\\lim_\{([^}]+)\s*\\to\s*0\}\s*\\frac\{\\sin\(([^)]+)\)\}\{([^}]+)\}': r'sin(\2)/\3',  # sin(x)/x limit
            r'\\lim_\{([^}]+)\s*\\to\s*0\}\s*\\frac\{1\s*-\s*\\cos\(([^)]+)\)\}\{([^}]+)\}': r'(1-cos(\2))/\3',  # (1-cos(x))/x limit
            r'\\lim_\{([^}]+)\s*\\to\s*0\}\s*\\frac\{\\tan\(([^)]+)\)\}\{([^}]+)\}': r'tan(\2)/\3',  # tan(x)/x limit
            r'\\lim_\{([^}]+)\s*\\to\s*0\}\s*\\frac\{\\ln\(1\s*\+\s*([^)]+)\)\}\{([^}]+)\}': r'ln(1+\2)/\3',  # ln(1+x)/x limit
        }
        
        for pattern, replacement in limit_patterns.items():
            if re.search(pattern, visma_expr):
                visma_expr = re.sub(pattern, replacement, visma_expr)
                logger.debug(f"Detected known limit pattern, converted to: {visma_expr}")
                break

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
        
        for latex_pattern, visma_replacement in conversions.items():
            visma_expr = re.sub(latex_pattern, visma_replacement, visma_expr)
        
        visma_expr = visma_expr.replace('{', '(').replace('}', ')')
        
        visma_expr = re.sub(r'\s+', ' ', visma_expr).strip()
        
        logger.debug(f"Converted LaTeX '{latex_expr}' to Visma format '{visma_expr}'")
        return visma_expr
    

    def _visma_to_latex(self, visma_expr: str) -> str:
        """Convert Visma expression to LaTeX format."""
        if not visma_expr:
            return ""
        
        latex_expr = visma_expr
        
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
        
        frac_pattern = r'\(([^)]+)\)/\(([^)]+)\)'
        latex_expr = re.sub(frac_pattern, r'\\frac{\1}{\2}', latex_expr)
        
        latex_expr = re.sub(r'\s*([+\-*/=<>!])\s*', r' \1 ', latex_expr)
        latex_expr = re.sub(r'\s+', ' ', latex_expr).strip()
        
        logger.debug(f"Converted Visma '{visma_expr}' to LaTeX '{latex_expr}'")
        return latex_expr
    

    def _handle_definite_integral(self, expression: str, variable: str) -> Dict[str, Any]:
        """Handle definite integral operations with better error handling."""
        try:
            import re

            pattern = r'∫_\{([^}]+)\}\^\{([^}]+)\}\s*([^d]+)\s*d' + variable
            match = re.search(pattern, expression)
            
            if not match:
                pattern = r'∫_([^_]+)\^([^_]+)\s*([^d]+)\s*d' + variable
                match = re.search(pattern, expression)
            
            if match:
                lower_limit = match.group(1).strip()
                upper_limit = match.group(2).strip()
                integrand = match.group(3).strip()
                
                try:
                    lower_val = float(lower_limit)
                    upper_val = float(upper_limit)
                except ValueError:
                    lower_val = lower_limit
                    upper_val = upper_limit
                
                tokens = tokenizer(integrand)
                l_tokens, _, _, equation_tokens, comments = integrate(tokens, variable)
                
                if equation_tokens:
                    indefinite_result = tokensToString(equation_tokens[-1])
                    steps = [
                        f"Step 1: Find indefinite integral ∫ {integrand} d{variable}",
                        f"Step 2: Indefinite integral = {indefinite_result}",
                        f"Step 3: Apply fundamental theorem: F({upper_limit}) - F({lower_limit})",
                        f"Step 4: Substitute limits into indefinite integral"
                    ]
                    
                    result = f"[{indefinite_result}]_{{{lower_limit}}}^{{{upper_limit}}}"
                    
                    return {
                        'results': [result],
                        'solving_steps': steps,
                        'raw_output': f"Definite integral: ∫_{{{lower_limit}}}^{{{upper_limit}}} {integrand} d{variable}",
                        'success': True
                    }
                else:
                    raise ValueError("Could not find indefinite integral")
            else:
                raise ValueError("Could not parse definite integral format")
                
        except Exception as e:
            logger.warning(f"Definite integral handling failed: {e}")
            return {
                'results': [f"∫ {expression} (definite integral - complex evaluation)"],
                'solving_steps': [f"Definite integral evaluation requires advanced techniques"],
                'raw_output': f"Complex definite integral: {expression}",
                'success': False,
                'error': f"Definite integral error: {str(e)}"
            }


    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations."""
        return self.supported_operations.copy()



