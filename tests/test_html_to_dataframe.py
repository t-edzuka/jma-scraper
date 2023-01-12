import pandas as pd

from jma_scraper.core.html_to_dataframe import (
    pluck_table_from_html,
    read_html_table,
)


def test_html_txt_can_convert_to_dataframe(hamamatsu_html):
    html_table_txt = pluck_table_from_html(hamamatsu_html)
    df = read_html_table(html_table_txt, pd.read_html)
    assert type(df) == pd.DataFrame
    assert isinstance(df.columns, pd.MultiIndex)

