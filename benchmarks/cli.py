import asyncio
import logging

import typer

from benchmarks.config import SQLALCHEMY_DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()
database = typer.Typer()

app.add_typer(database, name="database", help="Database commands")


@database.command()
def init():
    logger.info("Initializing database schemas...")
    from benchmarks.database.core import engine
    from benchmarks.database.manage import init_database

    asyncio.run(init_database(engine))
    logger.info("Successfully initialized database schemas!")


@database.command()
def drop():
    from sqlalchemy_utils import drop_database

    logger.info("Dropping database...")

    sync_url = SQLALCHEMY_DATABASE_URL.replace("+asyncpg", "+psycopg2")
    drop_database(sync_url)
    logger.info("Successfully dropped database!")


if __name__ == "__main__":
    app()
