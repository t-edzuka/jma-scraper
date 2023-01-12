# これはサンプルの Python スクリプトです。
import typer

from jma_scraper.input_inferfaces.command_line import to_csv_with_typer


if __name__ == "__main__":
    typer.run(to_csv_with_typer)
