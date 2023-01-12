from datetime import date

from core.location_spec import RecordInterval
from core.location_instances import HAMAMATSU
from core.url_formatter import QueryParamsForJma


def test_location_hamamatsu_spec():
    """浜松のページに実際に外部接続してテストする"""
    from jma_scraper.infrastracture.http_client import fetch_html
    qp = QueryParamsForJma(date=date(2022, 1, 1),
                           prefecture_no=HAMAMATSU.prefecture_no,
                           block_no=HAMAMATSU.location_no,
                           record_interval=RecordInterval.from_literal("every_10_minutes"))
    html = fetch_html(qp)
    assert "浜松" in html
    assert "2022年1月1日" in html
    assert "１０分ごとの値" in html
