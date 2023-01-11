from pathlib import Path
from typing import Any, Iterator, Union

import pandas as pd

from jma_scraper.core.repository import Writer, WriterSrcValues

RESOURCE_ROOT = Path(__file__).parents[2] / "__data__"  # プロジェクトのルートに__data__ディレクトリ
RESOURCE_ROOT.mkdir(exist_ok=True)

JMA_CSV_DIR = RESOURCE_ROOT / "jma_csv" # __data__/jma_csv
JMA_CSV_DIR.mkdir(exist_ok=True)

JMA_CSV_FILES: Iterator[Path] = JMA_CSV_DIR.glob("*.csv")


class DfLocalCsvWriter(Writer):
    def __init__(self, src_values: WriterSrcValues):
        super().__init__(src_values)
        self.src_values = src_values

    def write(self, src: pd.DataFrame, dst: Union[Path, None] = None) -> None:
        if dst is None:
            dst = self.create_csv_full_path()
        src.to_csv(dst, index=False)

    def create_csv_full_path(self) -> Path:
        return JMA_CSV_DIR / f"{self.src_values.format()}.csv"
