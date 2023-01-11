from pathlib import Path

from pytest import fixture
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from jma_scraper.infrastracture.db_tables import FetchedHtml


@fixture
def html_table_example() -> str:
    text_path = (
            Path(__file__).parent
            / "input_examples"
            / "hamamatsu_every_10min_only_table.html"
    )
    return text_path.read_text()


@fixture(name="session")
def in_memory_session():
    engine = create_engine(
        "sqlite://",  # in memory database
        echo=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_fetched_html_tables(html_table_example):
    table_content = FetchedHtml(
        url="https://example.com",  # type: ignore
        html_content=html_table_example,
    )

    assert len(table_content.id) == 26
    assert table_content.url == "https://example.com"
    assert table_content.html_content == html_table_example


def test_fetched_html_recorded_to_sqlite_table(session, html_table_example):
    with session:
        data = FetchedHtml(
            url="https://example.com",  # type:ignore
            html_content=html_table_example,
        )
        session.add(data)
        session.commit()
        got_data = session.get(FetchedHtml, data.id)
        assert got_data is not None
        assert isinstance(got_data, FetchedHtml)
        assert got_data.html_content == html_table_example
