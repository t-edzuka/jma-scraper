from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Location:
    prefecture_no: int
    location_no: int
    name: str
    en_name: str


HAMAMATSU = Location(prefecture_no=50, location_no=47654, name="浜松", en_name="hamamatsu")



