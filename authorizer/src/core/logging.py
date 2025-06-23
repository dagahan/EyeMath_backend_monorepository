import inspect
import json
import logging
import sys

from google.protobuf.json_format import MessageToDict
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import MethodTools


class InterceptHandler(logging.Handler):
    def emit(self, record) -> None:
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


class LogSetup:
    @staticmethod
    def configure() -> None:
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
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.log_requests = self.config.get("grpc_server", "log_requests")
        self.log_responses = self.config.get("grpc_server", "log_responses")
        self.method_tools = MethodTools()
        self.log_huge_reqs_and_resps = self.config.get("grpc_server", "log_huge_reqs_and_resps")
        self.count_of_chars_in_huge_logs = self.config.get("grpc_server", "count_of_chars_in_huge_logs")
        self.replace_huge_logs_by_small_msgs = self.config.get("grpc_server", "replace_huge_logs_by_small_msgs")
        

    def _should_abbreviate(self, content: str) -> bool:
        '''Do we need to use an abbreviation for replacing huge body of req/res?'''
        return len(content) > self.count_of_chars_in_huge_logs and not self.log_huge_reqs_and_resps
    

    def _format_payload(self, message: str) -> str:
        '''Formats the logging message based on the settings'''
        if self._should_abbreviate(str(message)):
            return "too huge to display." if self.replace_huge_logs_by_small_msgs else MessageToDict(message)
        return MessageToDict(message)


    @logger.catch
    def _logrequest(self, request: str, context) -> None:
        if not self.log_requests:
            return

        payload = self._format_payload(request)

        called_file, called_method, called_line = self.method_tools.get_method_info(3)
        peer_info = context.peer()  # формат вида 'ipv4:127.0.0.1:54321'
        payload_json = json.dumps(payload, indent=4, ensure_ascii=False)

        logger.info(f"Method {called_method} has been called from {peer_info}\nWith data: {payload_json}")


    @logger.catch
    def _logresponse(self, response: str, context) -> None:
        if not self.log_responses:
            return

        if self._should_abbreviate:
            if self.replace_huge_logs_by_small_msgs:
                payload = "too huge to display."
            else:
                payload = MessageToDict(response)

            called_file, called_method, called_line = self.method_tools.get_method_info(3, 3)
            peer_info = context.peer()  # формат вида 'ipv4:127.0.0.1:54321'
            payload_json = json.dumps(payload, indent=4, ensure_ascii=False)

            logger.info(f"Method {called_method} responsing to {peer_info}\nWith data: {payload_json}")


class LogBenchmark:
    # TODO: Create decorator to check how many time takes an executing function.
    pass
