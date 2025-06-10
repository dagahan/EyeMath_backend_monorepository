import inspect
import json
import os
from typing import List

import chardet
from dotenv import load_dotenv
from loguru import logger


class MethodTools:
    def __init__(self):
        pass


    @staticmethod
    def name_of_method(one=+1, two=3):
        try:
            return inspect.stack()[one][two]
        except Exception as ex:
            logger.error(f"There is an error with checking your method's name: {ex}")
            return "Unknown Method"



class EnvTools:
    def __init__(self):
        load_dotenv()


    @staticmethod
    def load_env_var(variable_name):
        try:
            return os.getenv(variable_name)
        except Exception as ex:
            logger.critical(f"Error with {inspect.stack()[0][3]}\n{ex}")
            return None


    @staticmethod
    def is_debug_mode():
        return EnvTools.load_env_var("debug_mode")


    @staticmethod
    def is_running_inside_docker():
        try:
            if EnvTools.load_env_var('RUNNING_INSIDE_DOCKER') == "1":
                return True
        except KeyError as ex:
            logger.error(f"Error with {inspect.stack()[0][3]}. Returns default 'False'\n{ex}")
        return False


    @staticmethod
    def is_file_exist(directory, file):
        return os.path.exists(os.path.join(os.getcwd(), directory, file))


    @staticmethod
    def create_file_in_directory(dir, file):
        os.makedirs(dir)
        with open(dir+file, 'w') as newfile:
            newfile.write("")



class JsonLoader:
    @staticmethod
    def read_json(path):
        try:
            with open(os.path.abspath(path), 'rb') as file:
                raw_data = file.read()
                detected_encoding = chardet.detect(raw_data)['encoding']

            with open(os.path.abspath(path), encoding=detected_encoding) as file:
                info = json.load(file)
        except FileNotFoundError:
            info = {}
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.error(f"Error during reading JSON file {path}: {e}")
            info = {}
        return info


    @staticmethod
    def write_json(path, data):
        try:
            with open(os.path.abspath(path), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error writing JSON file {path}: {e}")



class Filters:
    @staticmethod
    def filter_strings(list1: List[str], list2: List[str]) -> List[str]:
        set2 = set(list2)
        return [s for s in list1 if s not in set2]


    @staticmethod
    def personalized_line(line, artifact, name):
        return  line.replace(artifact, name)
