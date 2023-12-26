from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(init=True, repr=True, eq=True)
class WeatherModel:
    w_date: Optional[datetime] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    condition: Optional[str] = None
    avg_temp: Optional[float] = None
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    wind_vel: Optional[float] = None
