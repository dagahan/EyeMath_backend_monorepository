import colorama
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import FileSystemTools


class Authorizer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        

    def autorize_user(self) -> None:
        pass