import inspect
import json
import os
import os.path
import shutil
from typing import Any, List

import chardet
from dotenv import load_dotenv
from loguru import logger


class MethodTools:
    @staticmethod
    def name_of_method(one: int =+ 1, two: int = 3) -> str:
        try:
            return inspect.stack()[one][two]
        except Exception as ex:
            logger.error(f"There is an error with checking your method's name: {ex}")
            return "Unknown Method"
        
    
    @staticmethod
    def check_type_of_var(variable: Any) -> str:
        return type(variable).__name__
    

class FileSystemTools:
    @staticmethod
    def count_files_in_dir(dir: str) -> int:
        return len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])
    

    @staticmethod
    def delete_directory(dir: str) -> None:
        shutil.rmtree(dir)


    @staticmethod
    def delete_file(file_path: str) -> None:
        os.remove(file_path)


class EnvTools:
    def __init__(self) -> None:
        load_dotenv()


    @staticmethod
    def load_env_var(variable_name: str) -> str:
        try:
            return str(os.getenv(variable_name))
        except Exception as ex:
            logger.critical(f"Error with {inspect.stack()[0][3]}\n{ex}")
            return ""
        
    
    @staticmethod
    def set_env_var(variable_name: str, variable_value: str) -> None:
        os.environ[variable_name] = variable_value


    @staticmethod
    def is_debug_mode() -> str:
        return EnvTools.load_env_var("debug_mode")


    @staticmethod
    def is_running_inside_docker() -> str:
        try:
            return EnvTools.load_env_var("RUNNING_INSIDE_DOCKER")
        except KeyError as ex:
            logger.error(
                f"Error with {inspect.stack()[0][3]}. Returns default '0'\n{ex}"
            )
        return ""


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
                f"Error with {inspect.stack()[0][3]}. Returns default 'False'\n{ex}"
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
