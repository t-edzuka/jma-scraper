from datetime import date
from enum import StrEnum
from typing import ClassVar, Dict, List, Literal, Union
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, Field, HttpUrl, PastDate

EVERY_XX = (
    "every_10_minutes",
    "every_1_hour",
    "every_1_days",
    "every_5_days",
    "every_10_days",
)
TYPE_EVERY_XX = Literal[
    "every_10_minutes",
    "every_1_hour",
    "every_1_days",
    "every_5_days",
    "every_10_days",
]


class RecordInterval(StrEnum):
    """気象庁URLページの観測データのAggregation間隔に応じたURL値"""

    ten_minutes = "10min_s1"
    one_hour = "hourly_s1"

    one_day = "daily_s1"
    five_day_divide_for_each_month = (
        "mb5daily_s1"  # A period of each month divided from one to every five days.
    )
    ten_day_divide_for_each_mont = (
        "10daily_s1"  # 1-10日, 11-20日, 21-31日のように月を頭から10日ごとに区切った
    )

    @classmethod
    def _name_mappings(cls) -> Dict[str, "RecordInterval"]:
        list_values: List["RecordInterval"] = list(cls)
        return {
            human_readable: enum_value
            for enum_value, human_readable in zip(list_values, EVERY_XX)  # noqa
        }

    @classmethod
    def from_literal(cls, every_xxx: TYPE_EVERY_XX) -> "RecordInterval":
        """
        >>> RecordInterval.from_literal("every_10_minutes")
        <RecordInterval.ten_minutes: '10min_s1'>
        """
        return cls._name_mappings()[every_xxx]


class QueryParamsForJma(BaseModel):
    """
    Query parameters for jma
    """

    JMA_WEBSITE_URL: ClassVar[HttpUrl] = HttpUrl(
        "https://www.data.jma.go.jp/obd/stats/etrn/view", scheme="https"
    )

    date: PastDate = Field(
        ...,
        description="指定した日付, queryパラメータにおけるyear, month, dayに相当, 本日を含まない過去の日",
    )
    prefecture_no: int = Field(
        ...,
        description="""queryパラメータにおける prec_no. おもに県名と対応する. 例: 静岡県: 50
    https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php
    """,
    )
    block_no: int = Field(
        ..., description="queryパラメータにおける block_no. 観測地点と対応する 例: 浜松: 47654"
    )
    record_interval: RecordInterval = Field(
        RecordInterval.ten_minutes, description="データ観測のaggregation単位を選ぶ"
    )

    @property
    def query_url(self) -> HttpUrl:
        return HttpUrl(
            f"{self.JMA_WEBSITE_URL}/{self.record_interval}.php?prec_no={self.prefecture_no}&block_no={self.block_no}&year={self.date.year}&month={self.date.month}&day={self.date.day}",
            scheme="https",
        )

    @classmethod
    def from_url(cls, url: Union[str, HttpUrl]) -> "QueryParamsForJma":
        date_ = cls.get_date_from_url(url)
        prefecture_no = cls.get_prefecture_no_from_url(url)
        block_url = cls.get_block_no_from_url(url)
        rec_interval = cls.get_record_interval_from_url(url)
        return cls(
            date=date_,
            prefecture_no=prefecture_no,
            block_no=block_url,
            record_interval=RecordInterval(rec_interval),
        )

    @staticmethod
    def _get_query_params(url: str) -> Dict[str, List[str]]:
        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query)

    @classmethod
    def get_date_from_url(cls, url: str) -> PastDate:
        """URL文字列から日付を表す数値部分を取得して、datetime.date型で返す。
        >>> input_url = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47654&year=2017&month=1&day=1"
        >>> QueryParamsForJma.get_date_from_url(input_url)
        datetime.date(2017, 1, 1)

        :param:
            url (str): URLにクエリパラメータ: year, month, dayをそれぞれ1つずつのみ持つ文字列型,

        :return:
            datetime.date: 日付を表すdatetime.date型。

        :raises:
            ValueError: URL文字列から取得した日付が存在しない場合に発生する。
            KeyError: URL文字列に不正なクエリパラメータを持つ場合に発生する。
        """
        query_params = cls._get_query_params(url)
        year = int(query_params["year"][0])
        month = int(query_params["month"][0])
        day = int(query_params["day"][0])
        return date(year, month, day)

    @classmethod
    def get_prefecture_no_from_url(cls, url: str) -> int:
        """
        >>> input_url = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47654&year=2017&month=1&day=1"
        >>> QueryParamsForJma.get_prefecture_no_from_url(input_url)
        50
        """
        query_params = cls._get_query_params(url)
        return int(query_params["prec_no"][0])

    @classmethod
    def get_block_no_from_url(cls, url: str) -> int:
        """
        >>> input_url = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47654&year=2017&month=1&day=1"
        >>> QueryParamsForJma.get_block_no_from_url(input_url)
        47654
        """
        query_params = cls._get_query_params(url)
        return int(query_params["block_no"][0])

    @staticmethod
    def get_record_interval_from_url(url: str) -> str:
        """
        >>> input_url = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47654&year=2017&month=1&day=1"
        >>> result = QueryParamsForJma.get_record_interval_from_url(input_url)
        >>> result
        '10min_s1'
        >>> assert result == RecordInterval.ten_minutes
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        return path.split("/")[-1].split(".")[0]
