import abc
from abc import ABC
from datetime import date
from typing import Any, Protocol, runtime_checkable

from jma_scraper.core.location_spec import TYPE_EVERY_XX
from pydantic import BaseModel, Field

from jma_scraper.core.url_formatter import QueryParamsForJma


class WriterSrcValues(BaseModel):
    """
    >>> WriterSrcValues(date=date(2022, 1, 1), location_name='hamamatsu', every_xx='every_10_minutes')
    WriterSrcValues(date=datetime.date(2022, 1, 1), location_name='hamamatsu', every_xx='every_10_minutes')
    """

    date: date
    location_name: str = Field(..., regex=r"^[a-z]+")
    every_xx: TYPE_EVERY_XX

    def format(self) -> str:
        """
        >>> wsn = WriterSrcValues(date=date(2022, 1, 1), location_name='hamamatsu', every_xx='every_10_minutes')
        >>> wsn.format()
        '2022-01-01__hamamatsu__every_10_minutes'
        """
        return f"{self.date.isoformat()}__{self.location_name}__{self.every_xx}"


@runtime_checkable
class Fetcher(Protocol):
    def __call__(
        self, query_param: QueryParamsForJma, time_out_sec: float = 2.0
    ) -> str:
        ...


class Writer(ABC):
    def __init__(self, src_values: WriterSrcValues, *args: Any, **kwargs: Any):
        self.src_name = src_values

    @abc.abstractmethod
    def write(self, src: Any, dst: Any) -> None:
        ...
