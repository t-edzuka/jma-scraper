from datetime import date
from pathlib import Path

import pandas as pd
from _pytest.fixtures import fixture

from jma_scraper.core.html_to_dataframe import pluck_table_from_html, read_html_table
from jma_scraper.core.location_instances import HAMAMATSU
from jma_scraper.core.location_spec import RecordInterval
from jma_scraper.core.url_formatter import QueryParamsForJma

this_dir = Path(__file__).parent


@fixture
def hamamatsu_html() -> str:
    input_path = this_dir / Path("input_examples/hamamatsu_jma.html")
    return input_path.read_text()


@fixture(name="raw_df")
def raw_multi_column_df(hamamatsu_html) -> pd.DataFrame:
    html_table_txt = pluck_table_from_html(hamamatsu_html)
    return read_html_table(html_table_txt, pd.read_html)


@fixture
def hamamatsu_qp_every_10_minuets():
    return QueryParamsForJma.from_location_spec(
        HAMAMATSU, date(2021, 1, 1), RecordInterval.from_literal("every_10_minutes")
    )
