from jma_scraper.core.location_spec import (
    Columns,
    FewColumns10Minutes,
    FewColumns10MinutesFormatted,
    Location,
    LocationColumnType,
    MainColumns10Minutes,
    MainColumns10MinutesFormatted,
)

# --- location information
HAMAMATSU = Location(
    prefecture_no=50,
    location_no=47654,
    name="浜松",
    en_name="hamamatsu",
    col_type=LocationColumnType.main,
)
IWATA = Location(
    prefecture_no=50,
    location_no=1244,
    name="磐田",
    en_name="iwata",
    col_type=LocationColumnType.few,
)
SHIZUOKA = Location(
    prefecture_no=50,
    location_no=47656,
    name="静岡",
    en_name="shizuoka",
    col_type=LocationColumnType.main,
)

# --- location with record intervals
main_col_10_min_list = list(MainColumns10Minutes)
main_col_10_min_list_fmt = list(MainColumns10MinutesFormatted)
few_col_10min_list = list(FewColumns10Minutes)
few_col_10min_list_fmt = list(FewColumns10MinutesFormatted)

HAMAMATSU_10Minutes_COLUMNS = Columns(
    original_columns=main_col_10_min_list, after_columns=main_col_10_min_list_fmt
)
SHIZUOKA_10Minutes_COLUMNS = Columns(
    original_columns=main_col_10_min_list, after_columns=main_col_10_min_list_fmt
)

IWATA_10Minutes_COLUMNS = Columns(
    original_columns=few_col_10min_list, after_columns=few_col_10min_list_fmt
)
