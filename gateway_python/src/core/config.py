import tomllib
from typing import Any

from loguru import logger

from src.core.utils import EnvTools


class ConfigLoader:
    __instance = None
    __config = None


    def __new__(cls) -> None:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls._load()
        return cls.__instance


    @classmethod
    def _load(cls) -> None:
        try:
            with open("pyproject.toml", "rb") as f:
                cls.__config = tomllib.load(f)
            EnvTools.set_env_var("CONFIG_LOADED", "1")
        except Exception as error:
            logger.critical("Config load failed: {error}", error=error)
            raise


    @classmethod
    def get(cls, section: str, key: str = "") -> Any:
        if key == "":
            return cls.__config.get(section, {})
        return cls.__config[section][key]


    def __getitem__(self, section: str) -> Any:
        return self.get(section)
