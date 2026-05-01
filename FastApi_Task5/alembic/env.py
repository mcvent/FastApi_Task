import asyncio
import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent.parent / "fastapi_app"))

# Импортируем настройки и модели
from src.core.config import settings
from src.infrastructure.postgres.database import Base
from src.infrastructure.postgres.models import User, Category, Location, Comment, Post

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Берём URL из настроек
config.set_main_option("sqlalchemy.url", settings.postgres_url)

POSTGRES_SCHEMA = settings.POSTGRES_SCHEMA
CREATE_SCHEMA_QUERY = f"CREATE SCHEMA IF NOT EXISTS {POSTGRES_SCHEMA};"


def filter_foreign_schemas(name, type_, parent_names):
    return type_ != "schema" or name == POSTGRES_SCHEMA


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=POSTGRES_SCHEMA,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=POSTGRES_SCHEMA,
        include_schemas=True,
        include_name=filter_foreign_schemas,
    )
    with context.begin_transaction():
        context.execute(CREATE_SCHEMA_QUERY)
        context.run_migrations()


async def run_migrations_online():
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        ),
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())