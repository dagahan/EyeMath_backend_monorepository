import inspect, grpc, json
from loguru import logger
from src.core.config import ConfigLoader


from concurrent import futures
from google.protobuf.json_format import MessageToDict


from mpmath import mp
import sympy
from sympy import Eq, Symbol, preorder_traversal, solve



from sympy.parsing.latex import parse_latex
from grpc_reflection.v1alpha import reflection #reflections to gRPC server


import gen.service_math_solve_pb2 as sevice_math_solve_pb
import gen.service_math_solve_pb2_grpc as sevice_math_solve_rpc



class MathSolver:
    def __init__(self):
        self.__config = ConfigLoader()
        mp.dps = self.__config.get("MaL", "PRECISION")


    @logger.catch
    def _is_equation(self, expr):
        logger.debug(f"Checking if {expr} is an equation...")
        if isinstance(expr, Eq):
            logger.debug(f"{expr} is an equation.")
            return True
        return any(isinstance(node, Symbol) for node in preorder_traversal(expr))
    

    @logger.catch
    def RevomeExtraZeroesFloat(self, value):
        if isinstance(value, (sympy.core.numbers.Float)):
            value = float(str(value).strip("0"))
        return value


    @logger.catch    #this we call 'decorator'
    def SolveExpression(self, request):
        parsed = latex2sympy(request.expression)

        if self._is_equation(self, parsed):
            to_return = solve(parsed)
        else:
            to_return = parsed.evalf()

        return to_return
    

    





    @logger.catch
    def SolveExpressionDebugMode(self, request):
        parsed = parse_latex(request.expression)


        logger.debug(f"{parsed}")
        # to_return = sympy.sqrt(parsed)

        if self._is_equation(self, parsed):
            answer = sympy.solve(parsed)
        else:
            answer = parsed.evalf()

        # print(type(to_return))

        answer = self.RevomeExtraZeroesFloat(self, answer)
        
        # logger.info(DockerTools.is_docker())

        return answer







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
            if self.__config.get("host", "debug_mode"):
                MathAnswer = MathSolver.SolveExpressionDebugMode(MathSolver, request)
            else:
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
            

class service:
    def __init__(self):
        self.config = ConfigLoader()


    def RUN_MATH_SOLVE_SERVICE(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        sevice_math_solve_rpc.add_GRPC_math_solveServicer_to_server(GRPC_math_solve(), server)

        # Enable gRPC reflection for the service
        # SERVICE_NAMES = (
        #     sevice_math_solve_pb.DESCRIPTOR.services_by_name['GRPC_math_solve'].full_name,
        #     reflection.SERVICE_NAME,
        # )
        # reflection.enable_server_reflection(SERVICE_NAMES, server)

        host = self.config.get("host", "HOST")
        port = int(self.config.get("host", "PORT"))
        addr = f"{host}:{port}"
        server.add_insecure_port(addr)
        logger.info(f"gRPC сервер запущен на {addr}")
        server.start()
        server.wait_for_termination()


