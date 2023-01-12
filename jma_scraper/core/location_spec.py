from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Dict, List, Literal

import pandas as pd


class LocationColumnType(StrEnum):
    main = "s1"
    few = "a1"


@dataclass(eq=True, frozen=True)
class Location:
    prefecture_no: int
    location_no: int
    name: str
    en_name: str

    col_type: LocationColumnType


class MainColumns10Minutes(StrEnum):
    hour_minutes = "時分_時分"
    h_pa = "気圧(hPa)_現地"
    h_pa_sea = "気圧(hPa)_海面"
    rain_amount = "降水量 (mm)_降水量 (mm)"
    temperature = "気温 (℃)_気温 (℃)"
    humidity = "相対湿度 (％)_相対湿度 (％)"
    ave_wind_speed = "風向・風速(m/s)_平均"
    ave_wind_direction = "風向・風速(m/s)_風向"
    max_wind_speed = "風向・風速(m/s)_最大瞬間"
    max_wind_direction = "風向・風速(m/s)_風向.1"
    sunshine_duration = "日照 時間 (分)_日照 時間 (分)"


class MainColumns10MinutesFormatted(StrEnum):
    hour_minutes = "時分"
    h_pa = "現地_気圧(hPa)"
    h_pa_sea = "海面_気圧(hPa)"
    rain_amount = "降水量(mm)"
    temperature = "気温(ºC)"
    humidity = "相対湿度(%)"
    ave_wind_speed = "平均_風速(m/s)"
    ave_wind_direction = "平均_風向"
    max_wind_speed = "最大瞬間_風速(m/s)"
    max_wind_direction = "最大瞬間_風向"
    sunshine_duration = "日照時間(min)"


class FewColumns10Minutes(StrEnum):
    hour_minutes = "時分_時分_時分"
    rain_amount = "降水量 (mm)_降水量 (mm)_降水量 (mm)"
    temperature = "気温 (℃)_気温 (℃)_気温 (℃)"
    humidity = "相対湿度 (％)_相対湿度 (％)_相対湿度 (％)"
    ave_wind_speed = "風向・風速_平均_風速(m/s)"
    ave_wind_direction = "風向・風速_平均_風向"
    max_wind_speed = "風向・風速_最大瞬間_風速(m/s)"
    max_wind_direction = "風向・風速_最大瞬間_風向"
    sunshine_duration = "日照 時間 (min)_日照 時間 (min)_日照 時間 (min)"


class FewColumns10MinutesFormatted(StrEnum):
    hour_minutes = "時分"
    rain_amount = "降水量(mm)"
    temperature = "気温(ºC)"
    humidity = "相対湿度(%)"
    ave_wind_speed = "平均_風速(m/s)"
    ave_wind_direction = "平均_風向"
    max_wind_speed = "最大瞬間_風速(m/s)"
    max_wind_direction = "最大瞬間_風向"
    sunshine_duration = "日照時間(min)"


COLUMNS_MAPPINGS = dict(
    zip(MainColumns10Minutes, MainColumns10MinutesFormatted, strict=True)
)


@dataclass(eq=True, frozen=True)
class Columns:
    original_columns: List[str] = (
        "時分_時分",
        "気圧(hPa)_現地",
        "気圧(hPa)_海面",
        "降水量 (mm)_降水量 (mm)",
        "気温 (℃)_気温 (℃)",
        "相対湿度 (％)_相対湿度 (％)",
        "風向・風速(m/s)_平均",
        "風向・風速(m/s)_風向",
        "風向・風速(m/s)_最大瞬間",
        "風向・風速(m/s)_風向.1",
        "日照 時間 (分)_日照 時間 (分)",
    )  # type: ignore
    after_columns: List[str] = (
        "時分",
        "現地_気圧(hPa)",
        "海面_気圧(hPa)",
        "降水量(mm)",
        "気温(ºC)",
        "相対湿度(%)",
        "平均_風速(m/s)",
        "平均_風速(m/s)_風向",
        "最大瞬間_風速(m/s)",
        "最大瞬間_風速(m/s)_風向",
        "日照時間(min)",
    )  # type: ignore

    def _to_list_dict(self) -> List[Dict[str, str]]:
        ls: List[Dict[str, str]] = []
        for org, aft in zip(self.original_columns, self.after_columns):  # noqa
            ls = [*ls, {"original": org, "after": aft}]
        return ls

    def to_df(self) -> pd.DataFrame:
        ls_d = self._to_list_dict()
        return pd.DataFrame.from_records(ls_d)

    def to_csv(self, dst_path: Path) -> None:
        self.to_df().to_csv(dst_path, index=False)


class RecordInterval(StrEnum):
    """気象庁URLページの観測データのAggregation間隔に応じたURL値"""

    ten_minutes = "10min"
    one_hour = "hourly"

    one_day = "daily"
    five_day_divide_for_each_month = (
        "mb5daily"  # A period of each month divided from one to every five days.
    )
    ten_day_divide_for_each_mont = "10daily"  # 1-10日, 11-20日, 21-31日のように月を頭から10日ごとに区切った

    @classmethod
    def _name_mappings(cls) -> Dict[str, "RecordInterval"]:
        list_values: List["RecordInterval"] = list(cls)
        return {
            human_readable: enum_value
            for enum_value, human_readable in zip(list_values, EVERY_XX)  # noqa
        }

    @classmethod
    def from_literal(cls, every_xxx: "TYPE_EVERY_XX") -> "RecordInterval":
        """
        >>> RecordInterval.from_literal("every_10_minutes")
        <RecordInterval.ten_minutes: '10min_'>
        """
        return cls._name_mappings()[every_xxx]

    def with_location_col_type(self, location_column_type: "LocationColumnType") -> str:
        """
        >>> lc_main = LocationColumnType.main
        >>> RecordInterval.ten_minutes.with_location_col_type(lc_main)
        '10min_s1'
        """
        return f"{self.value}_{location_column_type}"


EVERY_XX = (
    "every_10_minutes",
    "every_1_hour",
    "every_1_days",
    "every_5_days",
    "every_10_days",
)
TYPE_EVERY_XX = Literal[
    "every_10_minutes",
    "every_1_hour",
    "every_1_days",
    "every_5_days",
    "every_10_days",
]
