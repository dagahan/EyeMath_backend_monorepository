import sys
import tomllib
from pathlib import Path
from typing import Any

import colorama
from loguru import logger

from src.core.utils import EnvTools, MethodTools


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
            if hasattr(sys, 'ps1') or 'ipykernel' in sys.modules:
                cls.project_root = Path().resolve()
            else:
                cls.project_root = Path(__file__).resolve().parents[2]

            cls.pyproject_path = cls.project_root / "pyproject.toml"

            with open(cls.pyproject_path, "rb") as f:
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
        return self.get(section)
