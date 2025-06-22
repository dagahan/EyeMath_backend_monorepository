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
from src.core.utils import FileSystemTools


class Authorizer:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.jwt_parser = JwtParser()
        self.db_config = self._load_db_config()
        

    def _load_db_config(self) -> dict:
        """Загрузка конфигурации БД из настроек"""
        return {
            'dbname': EnvTools.load_env_var("POSTGRES_DB_NAME"),
            'user': EnvTools.load_env_var("POSTGRES_USER"),
            'password': EnvTools.load_env_var("POSTGRES_PASSWORD"),
            'host': EnvTools.load_env_var("POSTGRES_HOST"),
            'port': EnvTools.load_env_var("POSTGRES_APP_PORT")
        }
    

    def _get_db_connection(self):
        return psycopg2.connect(**self.db_config, cursor_factory=DictCursor)
    

    def _validate_user_data(self, username: str, password: str, email: str) -> dict:
        """Валидация входных данных пользователя"""
        errors = {}
        
        # Проверка имени пользователя
        if not 3 <= len(username) <= 30:
            errors['username'] = "Имя пользователя должно быть от 3 до 30 символов"
        elif not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors['username'] = "Имя пользователя может содержать только буквы, цифры и подчеркивания"
        
        # Проверка пароля
        if len(password) < 8:
            errors['password'] = "Пароль должен содержать минимум 8 символов"
        elif not any(char.isdigit() for char in password):
            errors['password'] = "Пароль должен содержать хотя бы одну цифру"
        elif not any(char.isupper() for char in password):
            errors['password'] = "Пароль должен содержать хотя бы одну заглавную букву"
        
        # Проверка email
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            errors['email'] = "Некорректный формат email"
        return errors
    

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля с использованием bcrypt"""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    
    
    def authorize_user(self, username: str, password: str, email: str) -> dict:
        """Регистрация нового пользователя"""
        try:
            # Валидация входных данных
            validation_errors = self._validate_user_data(username, password, email)
            if validation_errors:
                return {
                    "result": False,
                    "description": "; ".join(validation_errors.values())
                }
            
            # Хеширование пароля
            hashed_password = self._hash_password(password)
            
            # Подключение к БД и сохранение пользователя
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Проверка уникальности username и email
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
                    
                    # Создание нового пользователя
                    cursor.execute(
                        sql.SQL("""
                            INSERT INTO users (username, email, password_hash, created_at)
                            VALUES (%s, %s, %s, NOW())
                            RETURNING id
                        """), 
                        (username, email, hashed_password)
                    )
                    
                    user_id = cursor.fetchone()[0]
                    conn.commit()
                    
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