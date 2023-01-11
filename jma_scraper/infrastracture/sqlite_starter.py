from typing import Annotated

from infrastracture.localfile import RESOURCE_ROOT
from pydantic import Field, validate_arguments
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

DB_FILE_DIR = RESOURCE_ROOT / "jma_db"
DB_FILE_DIR.mkdir(exist_ok=True)

DB_PATH = DB_FILE_DIR / "jma_app.db"
DB_LOG = DB_FILE_DIR / "jma_app.log"


@validate_arguments
def create_sql_url(
    file_name: Annotated[str, Field(regex=r'^[^.].{0,253}[^/\0*?"<>|][^.]?$')],
) -> str:
    return f"sqlite:///{file_name}"


def create_engine_all(sqlite_url: str) -> Engine:
    return create_engine(sqlite_url, echo=True)


def create_session(engine: Engine) -> Session:
    return Session(engine)


def create_db_and_tables(engine: Engine) -> Engine:
    SQLModel.metadata.create_all(engine)
    return engine
