from typing import Any, List, Protocol, Sequence, TypeAlias

import pandas as pd
from bs4 import BeautifulSoup
from core.repository import Fetcher
from core.url_formatter import QueryParamsForJma
from infrastracture.http_client import fetch_html
from pandas import MultiIndex

HTML_TABLE_ID_SPEC = "tablefix1"  # 気象庁ホームページの仕様で tableタグにこのidが付与されているところが観測データのBody

HtmlText: TypeAlias = str


def pluck_table_from_html(fetched_html: str) -> HtmlText:
    soup = BeautifulSoup(fetched_html, features="html.parser")
    table_content = soup.find(id=HTML_TABLE_ID_SPEC)
    if table_content is None:
        raise ValueError(
            f"The HTML content should contain 'id={HTML_TABLE_ID_SPEC}', but cannot be found."
        )
    return table_content.__str__()


class TableReader(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> List[pd.DataFrame]:
        ...


def read_html_table(
    html_str: HtmlText, table_reader: TableReader = pd.read_html, **kwargs: Any
) -> pd.DataFrame:
    dfs = table_reader(html_str, **kwargs)

    if len(dfs) >= 2:
        raise ValueError(f"The expected tables should be just ONE, but got {len(dfs)}")
    return dfs[0]


FlattenDf: TypeAlias = pd.DataFrame


def flatten_columns(html_table_df: pd.DataFrame) -> FlattenDf:
    """関連のあるマルチカラムインデックスをアンダースコアでつなぐ"""
    if not isinstance(html_table_df.columns, MultiIndex):
        raise ValueError(
            f"Input dataframe should be Multi-columns indexes. Got {html_table_df.columns}"
        )

    html_table_df.columns = ["_".join(col) for col in html_table_df.columns.values]
    return html_table_df


FormattedDf: TypeAlias = pd.DataFrame


def format_columns(
    flattened_df: FlattenDf, after_columns: Sequence[str]
) -> FormattedDf:
    """

    :param flattened_df: マルチインデックスでないflatなカラムの pd.DataFrame
    :param after_columns: flattened_dfと同サイズのカラムで構成されるList, Tuple など
    :return: pd.DataFrame 注意: 元のflattened_dfに副作用を起こして返す.
    """
    if isinstance(flattened_df.columns, pd.MultiIndex):
        raise ValueError(
            "Input dataframe must be the flattened columns, but got Multiples, check dataframe contents"
        )
    if len(flattened_df.columns) != len(after_columns):
        raise ValueError(
            f"Column length should be the same original={len(flattened_df.columns)}, after={len(after_columns)}"
        )
    flattened_df.columns = after_columns
    return flattened_df


def fetch_df(
    qp: QueryParamsForJma,
    after_columns: Sequence[str],
    fetcher: Fetcher = fetch_html,
    time_out_sec: float = 2.0,
) -> FormattedDf:
    html_txt = fetcher(qp, time_out_sec=time_out_sec)
    html_table_only = pluck_table_from_html(html_txt)
    df = read_html_table(html_table_only, pd.read_html)
    df = flatten_columns(df)
    df = format_columns(df, after_columns=after_columns)
    return df
