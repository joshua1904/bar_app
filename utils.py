import dataclasses
import datetime

WEIGHT_DIFF = 30

STATUS_COLORS = {"fullBeer": "green", "emptyBeer": "red", "notUsed": "grey", "notConnected": "black"}

@dataclasses.dataclass
class INFO:
    percentage_of_beer: float
    info_color: str | None
    name: str
    serial: str

@dataclasses.dataclass
class Settings:
    min_weight: int
    max_weight: int
    min_time_diff: int
    tolerance: int


def _get_info_color(percentage_of_beer: float, new_beer_state: bool, last_seen: datetime, time_stamp: datetime, min_time_diff: int, tolerance: int, min_weight: int):
    if not new_beer_state:
        return STATUS_COLORS["notConnected"]
    if percentage_of_beer + WEIGHT_DIFF < 0:
        return STATUS_COLORS["notUsed"]
    if time_stamp + datetime.timedelta(seconds=min_time_diff) < last_seen:
        return STATUS_COLORS["notUsed"]
    if percentage_of_beer < tolerance:
        return STATUS_COLORS["emptyBeer"]
    return STATUS_COLORS["fullBeer"]


def _is_new_beer_state(last_seen: datetime, min_time_diff: int) -> bool:
    if last_seen + datetime.timedelta(seconds=min_time_diff) < datetime.datetime.now():
        return False
    return True


def get_info(min_time_diff: int, min_weight: int, max_weight: int, time_stamp: str, value: int, last_seen: str, tolerance: int, name: str, serial: str) -> INFO:
    time_stamp = datetime.datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S.%f")
    last_seen = datetime.datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S.%f")
    percentage_of_beer = int((value - min_weight) / (max_weight - min_weight) * 100)
    new_beer_state = _is_new_beer_state(last_seen, min_time_diff)
    info_color = _get_info_color(percentage_of_beer, new_beer_state, last_seen, time_stamp, min_time_diff, tolerance, min_weight)
    if percentage_of_beer < 0:
        percentage_of_beer = 0
    if not name:
        name = serial
    return INFO(percentage_of_beer, info_color, name, serial)

def get_settings_from_tuple(settings: tuple[int, int, int, int, int]) -> Settings:
    _, min_weight, max_weight, min_time_diff, tolerance = settings
    return Settings(min_weight, max_weight, min_time_diff, tolerance)