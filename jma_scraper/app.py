import sys
import time
from datetime import date, timedelta

from loguru import logger
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine, select
from sqlmodel.engine.result import ScalarResult

from jma_scraper.core.url_formatter import QueryParamsForJma
from jma_scraper.infrastracture.db_tables import FetchFailed
from jma_scraper.infrastracture.sqlite_starter import (
    DB_LOG,
    DB_PATH,
    create_db_and_tables,
    create_session,
    create_sql_url,
)
from jma_scraper.usecase.hamamatsu.write_scenario_local import write_scenario_local

START_DATE = date(2014, 12, 31)
END_DATE = date(2015, 1, 1)

sql_url = create_sql_url(str(DB_PATH))
sys.stdout = open(DB_LOG, "a")
engine = create_engine(sql_url, echo=True, connect_args={"check_same_thread": False})
started_engine: Engine = create_db_and_tables(engine)
session = create_session(started_engine)


def hamamatsu_10minutes_save_as_csv(
    start_date: date = START_DATE, end_date: date = END_DATE
) -> None:
    assert end_date > start_date
    delta_date = END_DATE - START_DATE
    current_day = END_DATE
    for _ in range(delta_date.days):
        try:
            write_scenario_local(current_day, session=session)
            logger.info("current_day={}", current_day)
        except Exception as e:
            logger.error(str(e))
            continue

        current_day = current_day - timedelta(days=1)
        assert isinstance(current_day, date)
        time.sleep(2)


def retry_failed_fetch(session: Session) -> None:
    logger.info(session)
    with session:
        statement = select(FetchFailed)
        all_failed: ScalarResult[FetchFailed] = session.exec(statement)
        assert all_failed is not None
        urls = [failed.url for failed in all_failed.all()]
    for url in urls:
        date_ = QueryParamsForJma.get_date_from_url(url)
        logger.info("Retry succeeded {}", url)
        write_scenario_local(date_, session)
        time.sleep(1)


if __name__ == "__main__":
    retry_failed_fetch(session=session)

    # hamamatsu_10minutes_save_as_csv()
