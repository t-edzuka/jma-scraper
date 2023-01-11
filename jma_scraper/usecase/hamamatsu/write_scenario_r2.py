import sys
from datetime import date, datetime
from pathlib import Path
from typing import Union

from botocore.exceptions import EndpointConnectionError
from pydantic import HttpUrl
from sqlmodel import Session, create_engine

from jma_scraper.core.location_spec import HAMAMATSU
from jma_scraper.core.repository import WriterSrcValues
from jma_scraper.infrastracture.db_tables import R2UploadFailed, R2UploadSucceeded
from jma_scraper.infrastracture.localfile import JMA_CSV_DIR, RESOURCE_ROOT
from jma_scraper.infrastracture.r2 import LocalToR2Writer, R2Conf
from jma_scraper.infrastracture.sqlite_starter import (
    DB_FILE_DIR,
    create_db_and_tables,
    create_session,
    create_sql_url,
)


def write_from_local_to_r2(
    date_: date,
    r2_conf: R2Conf,
    src: Path,
    dst: Union[str, None] = None,
    *,
    session: Session,
) -> None:
    src_values = WriterSrcValues(
        date=date_, location_name=HAMAMATSU.en_name, every_xx="every_10_minutes"
    )
    if dst is None:
        dst = f"{RESOURCE_ROOT.name}/{JMA_CSV_DIR.name}/{src_values.format()}.csv"
        assert "__data__/jma_csv/2022-01-01__hamamatsu__every_10_minutes.csv" == dst
    r2_writer = LocalToR2Writer(src_values, r2_conf)
    dst_url = HttpUrl(r2_conf.create_dst_url(dst), scheme="https")
    try:
        r2_writer.write(src, dst)
        print(dst_url)

        data = R2UploadSucceeded(url=dst_url)
        session.add(data)
        session.commit()
    except EndpointConnectionError as e:
        message = f"{str(e)} url connection failed"
        succeeded = R2UploadFailed(url=dst_url, message=message)
        session.add(succeeded)
        session.commit()
    except Exception as e:
        message = str(e)
        failed = R2UploadFailed(url=dst_url, message=message)
        session.add(failed)
        session.commit()
    session.close()


if __name__ == "__main__":
    db_log_file = (
        DB_FILE_DIR / f"{datetime.now().strftime('%Y-%m-%d__%H%M%S')}_sqlite.log"
    )
    sys.stdout = open(db_log_file, "a")
    sqlite_url = create_sql_url(f'{RESOURCE_ROOT / "jma_db" / "jma_app.db"}')
    engine = create_engine(sqlite_url, echo=True)
    create_db_and_tables(engine)

    session = create_session(engine)
    write_from_local_to_r2(
        date(2022, 1, 1),
        r2_conf=R2Conf(),
        src=JMA_CSV_DIR / "2022-01-01__hamamatsu__every_10_minutes.csv",
        session=session,
    )
