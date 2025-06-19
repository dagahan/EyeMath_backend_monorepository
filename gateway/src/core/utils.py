import json
import os
import os.path
import shutil
from inspect import getframeinfo, stack
from typing import Any, List, Tuple
from pathlib import Path

import chardet
from dotenv import load_dotenv
from loguru import logger


class MethodTools:
    def __init__(self) -> None:
        pass


    @staticmethod
    def get_method_info(stack_level: int =+ 1) -> Tuple[str, str, int]:
        try:
            current_stack = stack()
            if not len(current_stack) > stack_level:
                return ("Unknown File", "Unknown Method", 0)
            
            frame = current_stack[stack_level][0]
            frame_info = getframeinfo(frame)
            return (
                frame_info.filename,
                frame_info.function,
                frame_info.lineno
            )
        
        except Exception as ex:
            logger.error(f"There is an error with checking your method's name: {ex}")
            return ("Unknown File", "Unknown Method", 0)
        
    
    @staticmethod
    def check_type_of_var(variable: Any) -> str:
        return type(variable).__name__


class FileSystemTools:
    def __init__(self) -> None:
        pass

    @staticmethod
    def ensure_directory_exists(directory: str) -> None:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)


    @staticmethod
    def count_files_in_dir(dir: str) -> int:
        return len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])
    

    @staticmethod
    def save_file(file_path: str, data: bytes) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
    

    @staticmethod
    def delete_directory(dir: str) -> None:
        shutil.rmtree(dir)


    @staticmethod
    def delete_file(file_path: str) -> None:
        os.remove(file_path)


class EnvTools:
    @staticmethod
    def load_env_var(variable_name: str) -> Any:
        try:
            load_dotenv()
            return os.getenv(variable_name)
        except Exception as ex:
            logger.critical(f"Error with loading env variable\n{ex}")
            return None
        
    
    @staticmethod
    def set_env_var(variable_name: str, variable_value: str) -> None:
        os.environ[variable_name] = variable_value


    @staticmethod
    def is_debug_mode() -> str:
        return EnvTools.load_env_var("debug_mode")


    @staticmethod
    def is_running_inside_docker() -> bool:
        try:
            return EnvTools.load_env_var("RUNNING_INSIDE_DOCKER") == "1"
        except KeyError as ex:
            logger.error(
                f"Error with checking if programm running inside docker. Returns default False\n{ex}"
            )
        return False


    @staticmethod
    def is_file_exist(directory: str, file: str) -> bool:
        return os.path.exists(os.path.join(os.getcwd(), directory, file))


    @staticmethod
    def create_file_in_directory(dir, file) -> None:
        try:
            os.makedirs(dir)
            with open(dir + file, "w") as newfile:
                newfile.write("")
        except Exception as ex:
            logger.error(
                f"Error with creating {dir}{file}\n{ex}"
            )


class JsonLoader:
    @staticmethod
    def read_json(path: str) -> dict:
        try:
            with open(os.path.abspath(path), "rb") as file:
                raw_data = file.read()
                detected_encoding = chardet.detect(raw_data)["encoding"]

            with open(os.path.abspath(path), encoding=detected_encoding) as file:
                info = json.load(file)
        except FileNotFoundError as ex:
            logger.error(f"Error during reading JSON file {path}: {ex}")
            info = {}
        except (UnicodeDecodeError, json.JSONDecodeError) as ex:
            logger.error(f"Error during reading JSON file {path}: {ex}")
            info = {}
        return info


    @staticmethod
    def write_json(path: str, data: str) -> None:
        try:
            with open(os.path.abspath(path), "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error writing JSON file {path}: {e}")


class Filters:
    @staticmethod
    def filter_strings(list1: List[str], list2: List[str]) -> List[str]:
        set2 = set(list2)
        return [s for s in list1 if s not in set2]


    @staticmethod
    def personalized_line(line: str, artifact: str, name: str) -> str:
        return line.replace(artifact, name)
