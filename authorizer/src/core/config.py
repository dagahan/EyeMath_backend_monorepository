from __future__ import annotations

import tomllib
from typing import Any, ClassVar

import colorama# type: ignore[import-untyped]
from loguru import logger

from src.core.utils import EnvTools, MethodTools


class ConfigLoader:
    __instance: ClassVar[ConfigLoader | None] = None
    __config: ClassVar[dict[str, Any]] = {}


    def __new__(cls) -> ConfigLoader:
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
        try:
            if key == "":
                return cls.__config.get(section, {})
            return cls.__config[section][key]
        
        except Exception as ex:
            called_file, called_method, called_line = MethodTools.get_method_info(2)
            logger.critical(f"Cannot get {colorama.Fore.YELLOW}[{section}][{key}] {colorama.Fore.WHITE}on the line {colorama.Fore.YELLOW}{called_line} {colorama.Fore.WHITE}in method {colorama.Fore.YELLOW}{called_method} {colorama.Fore.RED}{ex}")
            logger.critical(f"{called_file}")
            raise


    def __getitem__(self, section: str) -> Any:
        return type(self).get(section)
