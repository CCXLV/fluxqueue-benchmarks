from pathlib import Path

from starlette.config import Config
from starlette.datastructures import Secret

BASE_DIR = Path(__file__).resolve().parent

env_file = BASE_DIR.parent / ".env"

config = Config(env_file) if env_file.exists() else Config()

DOCS_URL = "https://fluxqueue.ccxlv.dev"
LOGO_URL = DOCS_URL + "/images/logo.svg"

# Postgres
POSTGRES_USER = config("POSTGRES_USER", cast=Secret)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_HOST = config("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = config("POSTGRES_PORT", default="5432")
POSTGRES_DB = config("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

ALEMBIC_REVISION_PATH = BASE_DIR / "database" / "revisions"

ALEMBIC_INI_PATH = BASE_DIR / ".." / "alembic.ini"
