from datetime import date
from pathlib import Path

from sqlmodel import Session

from jma_scraper.core.location_spec import HAMAMATSU
from jma_scraper.core.repository import WriterSrcValues
from jma_scraper.infrastracture.db_tables import LocalFileSaved
from jma_scraper.infrastracture.http_client import fetch_html
from jma_scraper.infrastracture.localfile import DfLocalCsvWriter
from jma_scraper.usecase.hamamatsu.write_scenario_interface import (
    fetch_and_write_hamamatsu_10_minutes_table,
)


def write_scenario_local(
    date_: date, session: Session, dst: Path | None = None
) -> None:
    src_values = WriterSrcValues(
        date=date_, location_name=HAMAMATSU.en_name, every_xx="every_10_minutes"
    )

    writer = DfLocalCsvWriter(src_values)
    if dst is None:
        dst = writer.create_csv_full_path()

    try:
        fetch_and_write_hamamatsu_10_minutes_table(
            fetcher=fetch_html,
            target_date=date_,
            writer=writer,
            dst=dst,
            session=session,
        )
        data = LocalFileSaved(file_path=str(dst))
        session.add(data)
        session.commit()

    except Exception:
        raise
