from datetime import date
from typing import ClassVar, Dict, List, Union
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, Field, HttpUrl, PastDate

from jma_scraper.core.location_spec import Location, LocationColumnType, RecordInterval


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

    location_col_type: LocationColumnType = Field(
        default=LocationColumnType.main, description="観測地点によってカラム名が変わる"
    )

    @classmethod
    def from_location_spec(
        cls, location: Location, past_date: PastDate, record_interval: RecordInterval
    ) -> "QueryParamsForJma":
        return cls(
            date=past_date,
            prefecture_no=location.prefecture_no,
            block_no=location.location_no,
            record_interval=record_interval,
            location_col_type=location.col_type,
        )

    @property
    def query_url(self) -> HttpUrl:
        return HttpUrl(
            f"{self.JMA_WEBSITE_URL}/{self.record_interval.with_location_col_type(self.location_col_type)}.php?prec_no={self.prefecture_no}&block_no={self.block_no}&year={self.date.year}&month={self.date.month}&day={self.date.day}",
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
        '10min'
        >>> assert result == RecordInterval.ten_minutes
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        return path.split("/")[-1].split(".")[0].split("_")[0]
