import os
import tomllib

from loguru import logger


class ConfigLoader:
    __instance = None  # char " _ " is used to indicate that this is a private variable
    __config = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls._load()
        return cls.__instance

    @classmethod
    def _load(cls):
        try:
            with open("pyproject.toml", "rb") as f:
                cls.__config = tomllib.load(f)
            os.environ["CONFIG_LOADED"] = "1"
        except Exception as error:
            logger.critical("Config load failed: {error}", error=error)
            raise

    @classmethod
    def get(cls, section: str, key: str = None):
        if key is None:
            return cls.__config.get(section, {})
        return cls.__config[section][key]

    def __getitem__(self, section: str):
        return self.get(section)
