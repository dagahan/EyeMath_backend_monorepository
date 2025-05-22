# ******************************************************************************
#  *                              _Math_Lib_.py                                *
#  *                                                                            *
#  *  Project: EyeMath                                                         *
#  *  Author: Usov Nikita                                                      *
#  *  Created: April 23, 2025                                                  *
#  *  Last Modified: May 29, 2025                                              *
#  *                                                                            *
#  *  Description:                                                             *
#  *  This is the Mathimatician Library with many of functions for EyeMath     *
#  *  Project. Here's some funtions how multiply, power, Generate LaTeX and  *
#  *  simpy recognize LaTeX code from PNG image.                               * 
#  *                                                                            *
#  ******************************************************************************





#  ******************************************************************************
                        # SETUP MATH LIBRARY ENVIRONMENT #
try:
    import os, sys
    from _Headers_ import *
    os.system(f"pip install -r {RES_DIR}req_MaL.txt")

    from mpmath import mp, polyroots, mpf
    from sympy import *
    from latex2sympy2 import latex2sympy
    import re

    # Set the precision for mpmath #

    mp.dps = PRECISION
    # Set the precision for mpmath #

except Exception as e:
    print(f"Error installing requirements: {e}\n\nPlease install the requirements manually.")
    sys.exit(1)
#  ******************************************************************************








#TODO: переделать все переменные в я mpf из библиотеки mpmath


def is_equation(expr):
    if isinstance(expr, Eq):
        return any(isinstance(node, Symbol) for node in preorder_traversal(expr.lhs)) or \
               any(isinstance(node, Symbol) for node in preorder_traversal(expr.rhs))
    
    return any(isinstance(node, Symbol) for node in preorder_traversal(expr))   


def solve_expression(expr):
    try:
        print(__name__)

        parsed_expr = latex2sympy(expr)
        print(f"parsed_expr: {parsed_expr}")

        if is_equation(parsed_expr):
            evaluated = solve(parsed_expr)
        else:
            evaluated = parsed_expr.evalf()
        return str(evaluated)
    

    except Exception as e:
        return f"Error: {str(e)}"





if __name__ == "__main__" or __name__ == "_Math_Lib_":
    ()