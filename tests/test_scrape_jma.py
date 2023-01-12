# from pydantic.dataclasses import dataclass
from datetime import date

import pytest
from bs4 import BeautifulSoup
from core.location_spec import RecordInterval

from jma_scraper.core.url_formatter import QueryParamsForJma


def test_table_tag_has_id_called_tablefix1(hamamatsu_html):
    assert hamamatsu_html.find('<table id="tablefix1">')


def test_bs4_can_extract_tablefix1_contents(hamamatsu_html):
    soup = BeautifulSoup(hamamatsu_html, features="html.parser")
    table_content = soup.find(id="tablefix1")
    assert table_content is not None

    first_row = table_content.find_all("tr")[2]
    first_cells = first_row.find_all("td")
    assert len(first_cells) == 11


@pytest.mark.parametrize("date_", [date(2022, 1, 1)])
@pytest.mark.parametrize("prefecture_no", [50])
@pytest.mark.parametrize("block_no", [47654])
@pytest.mark.parametrize(
    "record_interval, expected",
    [
        [
            RecordInterval.ten_minutes,
            "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47654&year=2022&month=1&day=1",
        ],
        [
            RecordInterval.one_hour,
            "https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php?prec_no=50&block_no=47654&year=2022&month=1&day=1",
        ],
        [
            RecordInterval.one_day,
            "https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no=50&block_no=47654&year=2022&month=1&day=1",
        ],
        [
            RecordInterval.five_day_divide_for_each_month,
            "https://www.data.jma.go.jp/obd/stats/etrn/view/mb5daily_s1.php?prec_no=50&block_no=47654&year=2022&month=1&day=1",
        ],
        [
            RecordInterval.ten_day_divide_for_each_mont,
            "https://www.data.jma.go.jp/obd/stats/etrn/view/10daily_s1.php?prec_no=50&block_no=47654&year=2022&month=1&day=1",
        ],
    ],
)
def test_query_url_is_expected(
    date_: date,
    prefecture_no: int,
    block_no: int,
    record_interval: RecordInterval,
    expected,
):
    q_param_for_jma = QueryParamsForJma(
        date=date_,
        prefecture_no=prefecture_no,
        block_no=block_no,
        record_interval=record_interval,
    )
    assert q_param_for_jma.query_url == expected


def test_get_date_from_url():
    # 正常系
    url = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47654&year=2017&month=1&day=1"
    expected = date(2017, 1, 1)
    assert QueryParamsForJma.get_date_from_url(url) == expected

    # 異常系 (存在しない日付)
    url = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47654&year=2017&month=2&day=29"
    with pytest.raises(ValueError):
        QueryParamsForJma.get_date_from_url(url)

    # 異常系 (不正なクエリパラメータ)
    url = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=50&block_no=47654&year=2017"
    with pytest.raises(KeyError):
        QueryParamsForJma.get_date_from_url(url)
