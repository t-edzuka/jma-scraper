from typing import Union

import httpx
from pydantic import HttpUrl

from jma_scraper.core.url_formatter import QueryParamsForJma


def fetch_html(query_param: QueryParamsForJma, time_out_sec: float = 2.0) -> str:
    """気象庁のサイトから過去の気象データを取得してhtmlテキストを返す
    >>> q_jma = QueryParamsForJma(date=date(2022, 1, 1), prefecture_no=50, block_no=47654, record_interval=RecordInterval.five_day_divide_for_each_month) # doctest: +SKIP
    >>> html_text = fetch_html(q_jma.query_url, timeout=2.0) # doctest: +SKIP
    """
    response = httpx.get(query_param.query_url, timeout=time_out_sec)

    if response.is_error:
        response.raise_for_status()

    content_type = response.headers.get("content-type")

    if content_type != "text/html":
        raise ValueError(f"The content type should be text/html, got {content_type}")

    return response.text


def fetch_html_from_url(url: Union[str, HttpUrl], time_out_sec: float = 2.0) -> str:
    qp = QueryParamsForJma.from_url(url)
    return fetch_html(qp, time_out_sec=time_out_sec)
