from logging.config import fileConfig
from dotenv import load_dotenv
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

project_root = Path(__file__).resolve().parents[4]
dotenv_path = f"{project_root}/.env"
dotenv_local_path = f"{project_root}/alembic_migrations/.env"

try:
    load_dotenv(dotenv_path)
    load_dotenv(dotenv_local_path)
except Exception:
    raise RuntimeError(f".env not found at {dotenv_path}")

from src.services.db.database import Base, DataBase
from eyemath_models import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", DataBase().engine_config + "?async_fallback=True")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
