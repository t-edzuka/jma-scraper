from pathlib import Path

import pandas as pd
from _pytest.fixtures import fixture
from core.html_to_dataframe import pluck_table_from_html, read_html_table

this_dir = Path(__file__).parent


@fixture
def hamamatsu_html() -> str:
    input_path = this_dir / Path("input_examples/hamamatsu_jma.html")
    return input_path.read_text()


@fixture(name="raw_df")
def raw_multi_column_df(hamamatsu_html) -> pd.DataFrame:
    html_table_txt = pluck_table_from_html(hamamatsu_html)
    return read_html_table(html_table_txt, pd.read_html)
