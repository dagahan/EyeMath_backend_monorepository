import colorama
from loguru import logger
import psycopg2
import bcrypt
import re
from psycopg2 import sql
from psycopg2.extras import DictCursor

from src.core.config import ConfigLoader
from src.services.jwt_parser import JwtParser
from src.core.utils import EnvTools
from typing import Any, Dict


class Authorizer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.jwt_parser = JwtParser()
        self.db_config = self._load_db_config()
        self.db_connection = self._get_db_connection()
        

    def _load_db_config(self) -> dict:
        if EnvTools.is_running_inside_docker():
            db_host = "postgres"
        else:
            db_host = EnvTools.load_env_var("POSTGRES_HOST")
        return {
            'dbname': EnvTools.load_env_var("POSTGRES_DB"),
            'user': EnvTools.load_env_var("POSTGRES_USER"),
            'password': EnvTools.load_env_var("POSTGRES_PASSWORD"),
            'host': db_host,
            'port': EnvTools.load_env_var("POSTGRES_APP_PORT")
        }
    

    def _get_db_connection(self):
        return psycopg2.connect(**self.db_config, cursor_factory=DictCursor)
    

    def _validate_user_data(self, username: str, password: str, email: str) -> dict:
        errors = {}
        
        if not 3 <= len(username) <= 30:
            errors['username'] = "Имя пользователя должно быть от 3 до 30 символов"
        elif not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors['username'] = "Имя пользователя может содержать только буквы, цифры и подчеркивания"
        
        if len(password) < 8:
            errors['password'] = "Пароль должен содержать минимум 8 символов"
        elif not any(char.isdigit() for char in password):
            errors['password'] = "Пароль должен содержать хотя бы одну цифру"
        elif not any(char.isupper() for char in password):
            errors['password'] = "Пароль должен содержать хотя бы одну заглавную букву"
        
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            errors['email'] = "Некорректный формат email"
        return errors
    

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    
    
    def register_user(self, username: str, password: str, email: str) -> dict:
        try:
            validation_errors = self._validate_user_data(username, password, email)
            if validation_errors:
                return {
                    "result": False,
                    "description": "; ".join(validation_errors.values())
                }
            
            hashed_password = self._hash_password(password)
            
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("""
                        SELECT EXISTS(
                            SELECT 1 FROM users 
                            WHERE username = %s OR email = %s
                        )
                    """), 
                    (username, email)
                )
                exists = cursor.fetchone()[0]
                
                if exists:
                    return {
                        "result": False,
                        "description": "Пользователь с таким именем или email уже существует"
                    }
                
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO users (username, email, password_hash, created_at)
                        VALUES (%s, %s, %s, NOW())
                        RETURNING id
                    """), 
                    (username, email, hashed_password)
                )
                
                user_id = cursor.fetchone()[0]
                self.db_connection.commit()
                
                logger.success(f"Зарегистрирован новый пользователь: ID={user_id}, username={username}")
                return {
                    "result": True,
                    "description": "Пользователь успешно зарегистрирован",
                    "user_id": user_id
                }
        
        except psycopg2.Error as e:
            logger.error(f"Ошибка базы данных при регистрации пользователя: {e}")
            return {
                "result": False,
                "description": f"Ошибка базы данных: {e.pgerror}"
            }
        
        except Exception as e:
            logger.critical(f"Непредвиденная ошибка при регистрации: {e}")
            return {
                "result": False,
                "description": "Внутренняя ошибка сервера"
            }
        

    def authorize_user(self, username: str, password: str) -> Dict[str, Any]:
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("""
                        SELECT id, username, password_hash 
                        FROM users 
                        WHERE username = %s
                    """), 
                    (username,)
                )
                user = cursor.fetchone()
                
                if not user:
                    logger.warning(f"Пользователь не найден: {username}")
                    return {
                        "result": False,
                        "description": "Неверное имя пользователя или пароль"
                    }
                
                if not self._verify_password(password, user["password_hash"]):
                    logger.warning(f"Неверный пароль для пользователя: {username}")
                    return {
                        "result": False,
                        "description": "Неверное имя пользователя или пароль"
                    }
                
                token = self._generate_jwt_token(user["id"], user["username"])
                
                logger.info(f"Успешная аутентификация: {username}")
                return {
                    "result": True,
                    "token": token,
                }
        
        except psycopg2.Error as e:
            logger.error(f"Ошибка БД при аутентификации: {e}")
            return {"result": False, "token": f"None"}
        
        except Exception as e:
            logger.critical(f"Ошибка аутентификации: {e}")
            return {"result": False, "token": "None"}
    

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    

    def _generate_jwt_token(self, user_id: int, username: str) -> str:
        payload = {
            "sub": str(user_id),
            "username": username,
        }
        
        return self.jwt_parser.encode_jwt(payload)
    

    def token_validation(self, token: str) -> Dict:
        try:
            verification = self.jwt_parser.verify_jwt(token)
            
            if not verification["result"]:
                logger.debug(f"jwt validation unsuccess. reason: {verification["reason"]}")
                return {
                    "result": False,
                }
            
            user_id = verification["user_id"]
            
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("SELECT id, username FROM users WHERE id = %s"),
                    (user_id,)
                )
                user = cursor.fetchone()
                
                if not user:
                    logger.debug(f"jwt validation unsuccess. reason: {verification["reason"]}")
                    return {
                        "result": False,
                    }
            
            return {
                "result": True,
                "user_id": user["id"],
            }
        
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return {
                "result": False,
            }