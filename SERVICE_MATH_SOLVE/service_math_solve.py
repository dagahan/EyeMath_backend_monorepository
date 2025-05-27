import os, sys, logging, inspect, toml


from concurrent import futures
import grpc
import service_math_solve_pb2 as pb
import service_math_solve_pb2_grpc as rpc
from google.protobuf.json_format import MessageToDict
import json


from loguru import logger
from mpmath import mp
from sympy import Eq, Symbol, preorder_traversal, solve
from latex2sympy2 import latex2sympy



#logger = logging.getLogger(__name__)

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
            with open("service_math_config.toml", "r") as f:
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




class MathSolver(rpc.MathSolver):
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
        


    def _logrequest(self, request, context):
        if self.config.get("metadata", "LOGGING_REQUESTS"):
            payload = MessageToDict(request)
            logger.info(
                f"Method \"{inspect.stack()[1][3]}\" has called from  |  {context.peer()}\n" #format: 'ipv4:127.0.0.1:54321'
                f"{json.dumps(payload, indent=4, ensure_ascii=False)}"
            )

    def _logresponce(self, responce, context):
        if self.config.get("metadata", "LOGGING_RESPONSES"):
            payload = MessageToDict(responce)
            logger.info(
                f"Method \"{inspect.stack()[1][3]}\" responsing to  |  {context.peer()}\n"
                f"{json.dumps(payload, indent=4, ensure_ascii=False)}"
            )



    def Metadata(self, request: pb.MetadataRequest, context) -> pb.MetadataResponse:
        self._logrequest(request, context)

        try:
            responce = pb.MetadataResponse(
                name = self.config.get("metadata", "NAME"),
                version = self.config.get("metadata", "VERSION"),
            )

            self._logresponce(responce, context)
            return responce

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return pb.MetadataResponse(
                )




    def Solve(self, request: pb.SolveRequest, context) -> pb.SolveResponse: #that function we call "endpoint of the gRPC api"
        self._logrequest(request, context)

        try:
            parsed = latex2sympy(request.expression)
            if self._is_equation(parsed):
                to_return = solve(parsed)
            else:
                to_return = parsed.evalf()

            responce = pb.SolveResponse(
                status=pb.SolveResponse.OK,
                result=str(to_return),
            )

            self._logresponce(responce, context)
            return responce


        except Exception as error:
            logger.error(f"Solve error: {error}")
            return pb.SolveResponse(
                status=pb.SolveResponse.ERROR,
                )
            


def run_service():
    LogSetup()
    config = ConfigLoader()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_MathSolverServicer_to_server(MathSolver(), server)

    host = config.get("host", "HOST")
    port = int(config.get("host", "PORT"))
    addr = f"{host}:{port}"
    server.add_insecure_port(addr)
    logger.info(f"gRPC сервер запущен на {addr}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        run_service()
    except Exception as error:
        logger.critical(f"Service crashed: {error}")
        sys.exit(1)