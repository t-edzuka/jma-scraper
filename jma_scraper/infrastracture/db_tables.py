from datetime import datetime

from pydantic import HttpUrl
from sqlmodel import SQLModel, Field
from ulid import ULID


class HasId(SQLModel):
    id: str = Field(default_factory=lambda: ULID().__str__(), primary_key=True)


class FetchedHtml(HasId, table=True):
    recorded_at:datetime =  Field(default_factory=datetime.now)
    url: HttpUrl = Field(...)
    html_content: str = Field(...)


class FetchFailed(HasId, table=True):
    recorded_at:datetime =  Field(default_factory=datetime.now)
    url: HttpUrl = Field(...)
    message: str = Field(...)


class LocalFileSaved(HasId, table=True):
    recorded_at: datetime = Field(default_factory=datetime.now)
    file_path: str = Field(...)


class R2UploadSucceeded(HasId, table=True):
    recorded_at: datetime =  Field(default_factory=datetime.now)
    url: HttpUrl = Field(...)


class R2UploadFailed(HasId, table=True):
    recorded_at:datetime =  Field(default_factory=datetime.now)
    url: HttpUrl = Field(...)
    message: str = Field(...)
