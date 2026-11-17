from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
from flask import abort, current_app

from ..response_cache import file_revision


ARCHIVE_YEAR = 2025


COUNTRIES = {
    "Argentina": "argentina", "Bolivia": "bolivia", "Brazil": "brasil",
    "Chile": "chile", "Colombia": "colombia", "Ecuador": "equador",
    "Guyana": "guiana", "Paraguay": "paraguai", "Peru": "peru",
    "Suriname": "suriname", "Uruguay": "uruguai", "Venezuela": "venezuela",
}
COLUMNS = [
    "latitude", "longitude", "acq_date", "acq_time", "satellite",
    "instrument", "confidence", "frp", "daynight", "type",
]
FILE_PREFIX = {"modis": "modis", "viirs": "viirs-jpss1"}
COUNTRY_ISO3 = {
    "Argentina": "ARG", "Bolivia": "BOL", "Brazil": "BRA", "Chile": "CHL",
    "Colombia": "COL", "Ecuador": "ECU", "Guyana": "GUY", "Paraguay": "PRY",
    "Peru": "PER", "Suriname": "SUR", "Uruguay": "URY", "Venezuela": "VEN",
}

def data_root() -> Path:
    configured = os.environ.get("PREVIA_DATA_DIR")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[3] / "dados" / "parquet"


def parquet_path(sensor: str, country: str, year: int = ARCHIVE_YEAR) -> Path:
    return data_root() / sensor / f"{FILE_PREFIX[sensor]}_{year}_{country}.parquet"


def dataset_revision() -> tuple:
    return tuple(file_revision(parquet_path(sensor, country)) for sensor in FILE_PREFIX for country in COUNTRIES)


def archive_partitions() -> dict[int, set[tuple[str, str]]]:
    years = {}
    root = data_root()
    for sensor, prefix in FILE_PREFIX.items():
        for path in (root / sensor).glob(f"{prefix}_*.parquet"):
            year, _, country = path.stem.removeprefix(f"{prefix}_").partition("_")
            if len(year) == 4 and year[0] != "0" and year.isascii() and year.isdecimal() and country in COUNTRIES and path.is_file():
                years.setdefault(int(year), set()).add((sensor, country))
    return years


def archive_revision() -> tuple:
    paths = archive_partitions()
    return tuple(
        file_revision(parquet_path(sensor, country, year))
        for year, partitions in sorted(paths.items())
        for sensor, country in sorted(partitions)
    )


def read_fire_columns(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.is_file():
        abort(503, description="O arquivo de dados solicitado não está disponível.")
    try:
        return pd.read_parquet(path, columns=columns)
    except Exception:
        current_app.logger.exception("Could not read fire data file %s", path)
        abort(503, description="Não foi possível ler o conjunto de dados.")


def load_file(sensor: str, country: str) -> pd.DataFrame:
    return load_versioned_file(sensor, country, file_revision(parquet_path(sensor, country)))


@lru_cache(maxsize=24)
def load_versioned_file(sensor: str, country: str, revision: tuple) -> pd.DataFrame:
    frame = read_fire_columns(Path(revision[0]), COLUMNS)
    frame["sensor"] = sensor.upper()
    frame["country"] = country
    frame["acq_date"] = pd.to_datetime(frame["acq_date"], errors="coerce", utc=True).dt.normalize()
    valid = frame["latitude"].between(-90, 90) & frame["longitude"].between(-180, 180)
    return frame.loc[valid & frame["acq_date"].notna()]


def filter_dates(frame: pd.DataFrame, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.DataFrame:
    if start is not None:
        frame = frame.loc[frame["acq_date"] >= start]
    if end is not None:
        frame = frame.loc[frame["acq_date"] <= end]
    return frame
