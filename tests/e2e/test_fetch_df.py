import pandas as pd

from jma_scraper.core.html_to_dataframe import fetch_df
from jma_scraper.core.location_instances import HAMAMATSU_10Minutes_COLUMNS
from jma_scraper.infrastracture.http_client import fetch_html


def test_fetch_df(hamamatsu_qp_every_10_minuets):
    df = fetch_df(
        qp=hamamatsu_qp_every_10_minuets,
        after_columns=HAMAMATSU_10Minutes_COLUMNS.after_columns,
        fetcher=fetch_html,
        time_out_sec=2.0,
    )
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == HAMAMATSU_10Minutes_COLUMNS.after_columns
