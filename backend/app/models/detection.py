from dataclasses import asdict, dataclass
from math import isfinite

import pandas as pd


@dataclass(frozen=True, slots=True)
class Detection:
    latitude: float
    longitude: float
    date: str | None
    time: int | None
    country: str
    sensor: str
    satellite: str | None
    confidence: str | None
    frp_mw: float | None
    daynight: str | None
    type: int | None
    intensity: str

    @classmethod
    def from_archive_row(cls, row: dict) -> "Detection":
        date = row["acq_date"]
        frp = pd.to_numeric(row["frp"], errors="coerce")
        confidence = row["confidence"]
        sensor = row["sensor"]
        if sensor == "VIIRS":
            intensity = {"H": "high", "N": "medium", "L": "low"}.get(str(confidence).upper(), "medium")
        else:
            value = pd.to_numeric(confidence, errors="coerce")
            intensity = "low"
            if pd.notna(value):
                if value >= 80:
                    intensity = "high"
                elif value >= 50:
                    intensity = "medium"

        return cls(
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            date=date.strftime("%Y-%m-%d") if pd.notna(date) else None,
            time=int(row["acq_time"]) if pd.notna(row["acq_time"]) else None,
            country=row["country"],
            sensor=sensor,
            satellite=str(row["satellite"]) if pd.notna(row["satellite"]) else None,
            confidence=str(confidence) if pd.notna(confidence) else None,
            frp_mw=float(frp) if pd.notna(frp) and isfinite(frp) else None,
            daynight=str(row["daynight"]) if pd.notna(row["daynight"]) else None,
            type=int(row["type"]) if pd.notna(row["type"]) else None,
            intensity=intensity,
        )

    def to_payload(self) -> dict:
        return {**asdict(self), "coordinates": [self.longitude, self.latitude]}
