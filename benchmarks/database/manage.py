import logging
from urllib.parse import urlparse

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy_utils import create_database

from benchmarks.config import ALEMBIC_INI_PATH, ALEMBIC_REVISION_PATH
from benchmarks.database.core import Base


def version_schema(script_location: str):
    alembic_cfg = AlembicConfig(ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_command.stamp(alembic_cfg, "head")


async def database_exists(engine: AsyncEngine) -> bool:
    url = urlparse(str(engine.url))
    database_name = url.path[1:]
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
            )
            return result.scalar() is not None
    except Exception:
        return False


async def init_database(engine: AsyncEngine):
    if not await database_exists(engine):
        create_database(
            str(
                engine.url.render_as_string(hide_password=False).replace("+asyncpg", "")
            )
        )

    try:
        core_tables = get_core_tables()
        async with engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    sync_conn, tables=core_tables
                )
            )
            logging.info("Tables creation attempted")

        version_schema(script_location=str(ALEMBIC_REVISION_PATH))

        logging.info("Tables created successfully.")
        return True
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        return False


def get_core_tables():
    """Fetches tables."""
    core_tables = []
    for table_name, table in Base.metadata.tables.items():
        core_tables.append(table)
        logging.info(f"Adding table: {table_name}")
    logging.info(f"Registered tables: {list(Base.metadata.tables.keys())}")
    return core_tables
