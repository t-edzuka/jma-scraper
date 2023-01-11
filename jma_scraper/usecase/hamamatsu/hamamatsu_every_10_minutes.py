from pathlib import Path
from typing import Dict, List

import pandas as pd
from pydantic.dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class HamamatsuColumns:
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
        self.to_df().to_csv(dst_path)


HAMAMATSU_COLUMNS = HamamatsuColumns()
