import datetime
import io
import sys
from datetime import datetime
from pathlib import Path

import pytest

from jma_scraper.input_inferfaces.command_line import (
    check_input_interval_arg,
    check_location_name,
    is_string_past_date,
    to_csv,
)


def test_is_string_past_date():
    past_date = "2022-01-01"
    assert is_string_past_date(past_date) == datetime(2022, 1, 1, 0, 0)

    future_date = "2030-01-01"
    with pytest.raises(ValueError, match="過去の日付でなければなりません"):
        is_string_past_date(future_date)

    non_existing_date = "2021-02-29"
    with pytest.raises(ValueError, match="存在しない日付です"):
        is_string_past_date(non_existing_date)

    invalid_date_string = "2022/01/01"
    with pytest.raises(ValueError, match="YYYY-MM-DD形式で渡してください"):
        is_string_past_date(invalid_date_string)


def test_to_csv():
    date_str = "2022-01-01"
    echo = False
    save_local = False
    dst_path = None
    to_csv(
        date_str,
        location_name="shizuoka",
        every="10m",
        echo=False,
        save_local=False,
        dst_path=None,
    )

    # check location_name
    invalid_location_name = "invalid_location"
    with pytest.raises(ValueError, match="location_name must be one of"):
        check_location_name(invalid_location_name)

    # check interval
    invalid_interval = "invalid_interval"
    with pytest.raises(ValueError, match="Allowed input is one of"):
        check_input_interval_arg(invalid_interval)

    # check invalid date
    invalid_date = "2022-01-32"
    with pytest.raises(ValueError, match="存在しない日付"):
        to_csv(invalid_date, "shizuoka", "10m", echo, save_local, dst_path)

    # check echo
    echo = True
    save_local = False
    captured_output = io.StringIO()
    sys.stdout = captured_output
    to_csv(date_str, "iwata", "10m", echo, save_local, dst_path)
    captured_str = captured_output.getvalue()
    assert "year=2022&month=1&day=1" in captured_str
    assert "iwata" in captured_str
    sys.stdout = sys.__stdout__

    # check save_local
    echo = False
    save_local = True
    dst_path = Path("test.csv")
    to_csv(date_str, "hamamatsu", "10m", echo, save_local, dst_path)
    assert dst_path.exists()
    dst_path.unlink(missing_ok=True)
