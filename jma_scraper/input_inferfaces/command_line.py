import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Literal, Optional

from core.location_spec import RecordInterval
from pydantic import validate_arguments
from typer import Option

from jma_scraper.core.html_to_dataframe import fetch_df
from jma_scraper.core.location_instances import (
    HAMAMATSU,
    IWATA,
    SHIZUOKA,
    HAMAMATSU_10Minutes_COLUMNS,
    IWATA_10Minutes_COLUMNS,
    SHIZUOKA_10Minutes_COLUMNS,
)
from jma_scraper.core.location_spec import Columns, Location
from jma_scraper.core.url_formatter import QueryParamsForJma
from jma_scraper.infrastracture.http_client import fetch_html

LOCATION_OK = Literal["hamamatsu", "iwata", "shizuoka"]
location_mapping: Dict[LOCATION_OK, Location] = {
    "hamamatsu": HAMAMATSU,
    "iwata": IWATA,
    "shizuoka": SHIZUOKA,
}

EVERY = Literal["10m"]
interval_mappings = {"10m": RecordInterval.ten_minutes}

LocationAndInterval = Literal["hamamatsu 10m", "iwata 10m", "shizuoka 10m"]

COLUMN_MAPPING: Dict[LocationAndInterval, Columns] = {
    "hamamatsu 10m": HAMAMATSU_10Minutes_COLUMNS,
    "iwata 10m": IWATA_10Minutes_COLUMNS,
    "shizuoka 10m": SHIZUOKA_10Minutes_COLUMNS,
}

pattern = re.compile(r"\d{4}-\d{2}-\d{2}")


def is_string_past_date(date_string: str) -> date:
    """
    >>> is_string_past_date("2022-01-01")
    True
    """
    match = pattern.match(date_string)
    if not match:
        raise ValueError(f"YYYY-MM-DD形式で渡してください. Got: {date_string}")
    try:
        date_ = datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"存在しない日付です. Got: {date_string}") from e

    now = datetime.now()
    is_past = date_ < now
    if not is_past:
        raise ValueError(f"過去の日付でなければなりません: {date_string}")
    return date_


@validate_arguments
def to_csv(
    date_str: str,
    location_name: LOCATION_OK,
    every: EVERY,
    echo: bool,
    save_local: bool,
    dst_path: Optional[Path] = None,
) -> None:
    date_ = is_string_past_date(date_str)
    if location_name != HAMAMATSU.en_name:
        raise ValueError(f"location_name must be in {LOCATION_OK}")

    location: Location = location_mapping[location_name]

    qp = QueryParamsForJma(
        date=date_,
        block_no=location.location_no,
        prefecture_no=location.prefecture_no,
        record_interval=interval_mappings[every],
    )
    url = qp.query_url
    print(f"Fetching this url: {url}")
    cols: Columns = COLUMN_MAPPING[f"{location_name} {every}"]  # type: ignore
    after = cols.after_columns
    df = fetch_df(qp=qp, after_columns=after, fetcher=fetch_html, time_out_sec=2.0)
    if echo:
        df.to_csv(sys.stdout, index=False)

    if not save_local:
        return

    if dst_path is not None:
        print(f"Save to {dst_path.resolve()}")
        df.to_csv(dst_path, index=False)
        return

    dst_path = Path(f"{date_str}_{location_name}__every_{every}.csv")
    print(f"Save to {dst_path.resolve()}")
    df.to_csv(dst_path, index=False)


def to_csv_with_typer(
    date: str = Option(..., help="過去のデータの日付: 2023-01-01"),
    dst_path: Optional[Path] = Option(
        None, help="保存するファイルパス", dir_okay=True, resolve_path=True
    ),
    location_name: str = Option(
        default="hamamatsu",
        help="""
                      allowed input: ["hamamatsu", ]
                      """,
    ),
    every: str = Option(
        default="10m",
        help="""データの取得間隔
                      allowed input: ["10m"]
                      """,
    ),
    save_local: bool = Option(
        default=False,
        help="""ローカルに保存するかどうか.
                      dst_pathを指定しなかった場合: "{YYYY-mm-dd}__{location_name}__every_{every}.csv"
                       YYYY-mm-dd はdateで指定した引数
                      という名前でカレントディレクトリに保存する.
                      """,
    ),
    echo: bool = Option(default=True, help="標準出力に出力するかどうか"),
) -> None:
    """
    気象庁の過去データをコマンドラインから実行してCSV形式で取得,(保存する)
    """
    to_csv(
        date_str=date,
        location_name=location_name,  # type: ignore
        dst_path=dst_path,
        every=every,  # type: ignore
        echo=echo,
        save_local=save_local,
    )
