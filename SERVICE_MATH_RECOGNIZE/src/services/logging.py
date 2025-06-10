import inspect
import logging
import sys
import json
import asyncio

from loguru import logger
from google.protobuf.json_format import MessageToDict

from src.core.config import ConfigLoader
from src.core.utils import MethodTools


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
            level, record.getMessage())


class LogSetup:
    @staticmethod
    def configure():
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
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - {message}",
            level="DEBUG",
            catch=True,
        )


class LogAPI:
    def __init__(self):
        self.config = ConfigLoader()
        self.log_requests = self.config.get("grpc_server", "log_requests")
        self.log_responses = self.config.get("grpc_server", "log_responses")
        self.method_tools = MethodTools()
        self.log_huge_reqs_and_resps = self.config.get("grpc_server", "log_huge_reqs_and_resps")
        self.count_of_chars_in_huge_logs = self.config.get("grpc_server", "count_of_chars_in_huge_logs")
        self.replace_huge_logs_by_small_msgs = self.config.get("grpc_server", "replace_huge_logs_by_small_msgs")
        
    
    # def deco(self, function):  
    #     def wrap():  
    #         asyncio.run(self._logresponce(responce, context))
    #         function()  
    #         asyncio.run(self._logresponce(responce, context))
    #     return wrap  


    @logger.catch
    async def _logrequest(self, request, context):
        if not self.log_requests:
            return

        if (len(str(request)) < self.count_of_chars_in_huge_logs or self.log_huge_reqs_and_resps or self.replace_huge_logs_by_small_msgs):
            if self.replace_huge_logs_by_small_msgs:
                payload = "too huge to display."
            else:
                payload = MessageToDict(request)

            method_name = self.method_tools.name_of_method(9, 3)
            peer_info = context.peer()  # формат вида 'ipv4:127.0.0.1:54321'
            payload_json = json.dumps(payload, indent=4, ensure_ascii=False)

            logger.info(f"Method {method_name} has been called from {peer_info}\nWith data:{payload_json}")


    @logger.catch
    async def _logresponce(self, responce, context):
        if not self.log_responses:
            return

        if (len(str(responce)) < self.count_of_chars_in_huge_logs or self.log_huge_reqs_and_resps or self.replace_huge_logs_by_small_msgs):
            if self.replace_huge_logs_by_small_msgs:
                payload = "too huge to display."
            else:
                payload = MessageToDict(responce)

            method_name = self.method_tools.name_of_method(9, 3)
            peer_info = context.peer()  # формат вида 'ipv4:127.0.0.1:54321'
            payload_json = json.dumps(payload, indent=4, ensure_ascii=False)

            logger.info(f"Method {method_name} responsing to {peer_info}\nWith data:{payload_json}")
