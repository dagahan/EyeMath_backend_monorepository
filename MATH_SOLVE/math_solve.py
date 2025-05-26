import os, sys, logging, inspect, toml, uvicorn, asyncio
from typing import Optional
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from loguru import logger
from mpmath import mp
from pydantic import BaseModel
from sympy import Eq, Symbol, preorder_traversal, solve
from latex2sympy2 import latex2sympy




class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and depth < 10:
            if frame.f_code.co_filename == logging.__file__:
                depth += 1
            frame = frame.f_back

        logger.opt(depth=depth, exception=record.exc_info, record=True).log(
            level, record.getMessage()
        )



class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load()
        return cls._instance

    @classmethod
    def _load(cls):
        try:
            with open("math_config.toml", "r") as f:
                cls._config = toml.load(f)
            os.environ["CONFIG_LOADED"] = "1"
        except Exception as error:
            logger.critical("Config load failed: {error}", error=error)
            raise
   
    @classmethod
    def get(cls, section: str, key: str):
        return cls._config[section][key]




class LogSetup:
    def __init__(self):
        self.configure_loguru()
        self.configure_uvicorn()


    @staticmethod
    def configure_loguru():
        logger.remove()
        logger.add(
            "debug/debug.json",
            format="{time} {level} {message}",
            serialize=True,
            rotation="05:00",
            retention="14 days",
            compression="zip",
            level="DEBUG",
            catch=True,
        )


        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> – {message}",
            level="DEBUG",
            catch=True,
        )


    @staticmethod
    def configure_uvicorn():
        logging.getLogger().handlers = []
        logging.basicConfig(handlers=[InterceptHandler()], level=logging.NOTSET, force=True)

        for name in logging.root.manager.loggerDict:
            if name.startswith(("uvicorn", "fastapi", "gunicorn")):
                lg = logging.getLogger(name)
                lg.handlers = []
                lg.propagate = True





class MathSolver:
    def __init__(self):
        self.config = ConfigLoader()
        mp.dps = self.config.get("MaL", "PRECISION")


    def _is_equation(self, expr):
        logger.debug(f"Checking if {expr} is an equation...")
        if isinstance(expr, Eq):
            logger.debug(f"{expr} is an equation.")
            lhs_vars = any(isinstance(node, Symbol) for node in preorder_traversal(expr.lhs))
            rhs_vars = any(isinstance(node, Symbol) for node in preorder_traversal(expr.rhs))
            return lhs_vars or rhs_vars
        else:
            logger.debug(f"{expr} is not an equation.")
            return any(isinstance(node, Symbol) for node in preorder_traversal(expr))


    def solve(self, expression: str) -> str:
        try:
            parsed = latex2sympy(expression)
            if self._is_equation(parsed):
                to_return = solve(parsed)
            else:
                to_return = parsed.evalf()
            return str(to_return)

        except Exception as error:
            logger.error("Solve error: {error}")
            return f"Error: {str(error)}"





class APIService:
    def __init__(self):
        self.config = ConfigLoader()
        self.app = FastAPI(title=self.config.get("metadata", "NAME"), version=self.config.get("metadata", "VERSION"))
        self.solver = MathSolver()
        self._setup_routes()


    class AnswerModel(BaseModel):
        answer_class: str
        response_data: Optional[str] = None



    def _setup_routes(self):
        @self.app.get("/") #that function we call "endpoint of the rest api"
        async def read_root():
            api_answer = self.AnswerModel(answer_class="root", response_data=self.app.version)
            return {self.app.title: api_answer}



        @self.app.get("/MaL/{operation}")
        async def read_operation(operation: str):

            logger.debug(f"Processing expression: {operation}")
            solver_answer = str(self.solver.solve(operation))
            logger.debug(f"Solver answer: {solver_answer}")

            api_answer = self.AnswerModel(answer_class="operation", response_data=solver_answer)
            return {self.app.title: api_answer}
            




app = APIService().app


def run_service():
    LogSetup()
    config = ConfigLoader()

    
    uvicorn.run(
        "math_solve:app",
        host="0.0.0.0",
        port=int(config.get("host", "PORT")),
        reload=config.get("host", "reload"),
        reload_excludes=["debug/*", "math_config.toml"],
        log_config=None,
        access_log=False
    )


if __name__ == "__main__":
    try:
        run_service()
    except Exception as critical_error:
        logger.critical("Service crashed: {error}", error=critical_error)
        sys.exit(1)