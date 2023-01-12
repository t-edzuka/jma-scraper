from datetime import date

from jma_scraper.core.html_to_dataframe import pluck_table_from_html, read_html_table, flatten_columns, format_columns
from jma_scraper.core.location_instances import IWATA, IWATA_10Minutes_COLUMNS
from jma_scraper.core.location_spec import RecordInterval, FewColumns10Minutes, FewColumns10MinutesFormatted
from jma_scraper.core.url_formatter import QueryParamsForJma
from infrastracture.http_client import fetch_html


def test_iwata():
    qp = QueryParamsForJma.from_location_spec(IWATA, date(2021, 1, 1),
                                              RecordInterval.from_literal("every_10_minutes"))
    txt = fetch_html(qp)
    tbl_txt = pluck_table_from_html(txt)
    df = read_html_table(tbl_txt)
    print(qp.query_url)
    df = flatten_columns(df)
    assert list(df.columns) == list(FewColumns10Minutes)
    df = format_columns(df, IWATA_10Minutes_COLUMNS.after_columns)
    assert list(df.columns) == list(FewColumns10MinutesFormatted)
