import os, sys, logging, inspect, toml, grpc, json
from concurrent import futures
from google.protobuf.json_format import MessageToDict
from loguru import logger
from mpmath import mp
from sympy import Eq, Symbol, preorder_traversal, solve
from latex2sympy2 import latex2sympy
from grpc_reflection.v1alpha import reflection #reflections to gRPC server


sys.path.insert(0, './gen')
import service_math_solve_pb2 as sevice_math_solve_pb
import service_math_solve_pb2_grpc as sevice_math_solve_rpc




# Setuping the exception handler
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
    __instance = None # char " _ " is used to indicate that this is a private variable
    __config = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls._load()
        return cls.__instance

    @classmethod
    def _load(cls):
        try:
            with open("pyproject.toml", "r") as f:
                cls.__config = toml.load(f)
            os.environ["CONFIG_LOADED"] = "1"
        except Exception as error:
            logger.critical("Config load failed: {error}", error=error)
            raise
   
    @classmethod
    def get(cls, section: str, key: str):
        return cls.__config[section][key]




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
            rotation="04:00",
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


class MathSolver:
    def __init__(self):
        self.__config = ConfigLoader()
        mp.dps = self.__config.get("MaL", "PRECISION")


    @logger.catch
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


    @logger.catch    #this we call 'decorator'
    def SolveExpression(self, request):
        parsed = latex2sympy(request.expression)

        if self._is_equation(self, parsed):
            to_return = solve(parsed)
        else:
            to_return = parsed.evalf()

        return to_return





class GRPC_math_solve(sevice_math_solve_rpc.GRPC_math_solve):
    def __init__(self):
        self.__config = ConfigLoader()
        mp.dps = self.__config.get("MaL", "PRECISION")
    

    @logger.catch
    def _logrequest(self, request, context):
        if self.__config.get("project", "LOGGING_REQUESTS"):
            payload = MessageToDict(request)
            logger.info(
                f"Method \"{inspect.stack()[2][3]}\" has called from  |  {context.peer()}\n" #format: 'ipv4:127.0.0.1:54321'
                f"{json.dumps(payload, indent=4, ensure_ascii=False)}"
            )

    @logger.catch
    def _logresponce(self, responce, context):
        if self.__config.get("project", "LOGGING_RESPONSES"):
            payload = MessageToDict(responce)
            logger.info(
                f"Method \"{inspect.stack()[2][3]}\" responsing to  |  {context.peer()}\n"
                f"{json.dumps(payload, indent=4, ensure_ascii=False)}"
            )


    @logger.catch
    def Metadata(self, request: sevice_math_solve_pb.MetadataRequest, context) -> sevice_math_solve_pb.MetadataResponse:
        self._logrequest(request, context)

        try:
            responce = sevice_math_solve_pb.MetadataResponse(
                name = self.__config.get("project", "name"),
                version = self.__config.get("project", "version"),
            )

            self._logresponce(responce, context)
            return responce

        except Exception as error:
            logger.error(f"Checking of metadata error: {error}")
            return sevice_math_solve_pb.MetadataResponse(
                )
        
    @logger.catch
    def Solve(self, request: sevice_math_solve_pb.SolveRequest, context) -> sevice_math_solve_pb.SolveResponse: #that function we call "endpoint of the gRPC api"
        self._logrequest(request, context)

        try:
            MathAnswer = MathSolver.SolveExpression(MathSolver, request)
            responce = sevice_math_solve_pb.SolveResponse(
                status=sevice_math_solve_pb.SolveResponse.OK,
                result=str(MathAnswer),
            )

            self._logresponce(responce, context)
            return responce

        except Exception as error:
            logger.error(f"Solve error: {error}")
            return sevice_math_solve_pb.SolveResponse(
                status=sevice_math_solve_pb.SolveResponse.ERROR,
                )
            


def RUN_MATH_SOLVE_SERVICE():
    LogSetup()
    config = ConfigLoader()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sevice_math_solve_rpc.add_GRPC_math_solveServicer_to_server(GRPC_math_solve(), server)

    # Enable gRPC reflection for the service
    SERVICE_NAMES = (
        sevice_math_solve_pb.DESCRIPTOR.services_by_name['GRPC_math_solve'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    host = config.get("host", "HOST")
    port = int(config.get("host", "PORT"))
    addr = f"{host}:{port}"
    server.add_insecure_port(addr)
    logger.info(f"gRPC сервер запущен на {addr}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        RUN_MATH_SOLVE_SERVICE()
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as error:
        logger.critical(f"Service crashed: {error}")
        sys.exit(1)