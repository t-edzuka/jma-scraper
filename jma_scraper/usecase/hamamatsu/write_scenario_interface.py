from datetime import date
from typing import Any

import pandas as pd
from sqlmodel import Session

from jma_scraper.core.html_to_dataframe import (
    flatten_columns,
    format_columns,
    pluck_table_from_html,
    read_html_table,
)

from ...core.location_instances import HAMAMATSU, HAMAMATSU_10Minutes_COLUMNS
from ...core.location_spec import RecordInterval
from ...core.repository import Fetcher, Writer
from ...core.url_formatter import QueryParamsForJma
from ...infrastracture.db_tables import FetchedHtml, FetchFailed


def fetch_and_write_hamamatsu_10_minutes_table(
    fetcher: Fetcher,
    target_date: date,
    http_time_out_sec: float = 2.0,
    *,
    writer: Writer,
    dst: Any = None,
    session: Session,
) -> None:
    q_jma = QueryParamsForJma(
        date=target_date,
        prefecture_no=HAMAMATSU.prefecture_no,
        block_no=HAMAMATSU.location_no,
        record_interval=RecordInterval.from_literal("every_10_minutes"),
    )

    try:
        html_text = fetcher(query_param=q_jma, time_out_sec=http_time_out_sec)
        data: FetchedHtml = FetchedHtml(url=q_jma.query_url, html_content=html_text)
        session.add(data)
        session.commit()
    except Exception as e:
        message = str(e)
        failed = FetchFailed(url=q_jma.query_url, message=message)
        session.add(failed)
        raise

    html_table: str = pluck_table_from_html(html_text)

    df: pd.DataFrame = read_html_table(html_table, pd.read_html)
    df = flatten_columns(df)
    assert list(df.columns) == HAMAMATSU_10Minutes_COLUMNS.original_columns
    df = format_columns(df, HAMAMATSU_10Minutes_COLUMNS.after_columns)
    assert list(df.columns) == HAMAMATSU_10Minutes_COLUMNS.after_columns

    writer.write(df, dst=dst)
    session.close()
