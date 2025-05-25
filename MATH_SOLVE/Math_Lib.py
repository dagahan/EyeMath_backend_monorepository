import os, sys, toml, re
from mpmath import mp, polyroots, mpf
from sympy import *
from latex2sympy2 import latex2sympy
from startup import CONFIG, load_toml, save_toml, read_key_toml, write_key_toml, read_key_config








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
    mp.dps = CONFIG["MaL"]["PRECISION"]

    print(read_key_config("paths", "base_dir"))
