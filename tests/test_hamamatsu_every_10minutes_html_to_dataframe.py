import pandas as pd
from pandas import MultiIndex, Index

from jma_scraper.core.html_to_dataframe import pluck_table_from_html, read_html_table, flatten_columns, format_columns
from jma_scraper.usecase.hamamatsu.hamamatsu_every_10_minutes import HAMAMATSU_COLUMNS

original, after = HAMAMATSU_COLUMNS.original_columns, HAMAMATSU_COLUMNS.after_columns


def test_pluck_table_from_html(hamamatsu_html):
    html_table = pluck_table_from_html(hamamatsu_html)
    df = read_html_table(html_table)

    assert isinstance(df.columns, MultiIndex)

    df_flattened = flatten_columns(df)
    assert isinstance(df_flattened.columns, Index)
    assert not isinstance(df_flattened.columns, MultiIndex)

    assert list(df_flattened.columns) == original

    df_formatted = format_columns(df_flattened, after_columns=after)

    assert list(df_formatted.columns) == after

    # NOTE: format_columns cause SIDE EFFECT which mutate original df_flattened
    assert list(df_flattened.columns) == after


