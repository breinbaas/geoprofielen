from pydantic import BaseModel
import numpy as np

from .coordconvertor import RDWGS84Converter

class PointRD(BaseModel):
    x: float = np.nan
    y: float = np.nan
    lat: float = np.nan
    lon: float = np.nan
    _coordconvertor = RDWGS84Converter()

    def to_rd(self) -> None:
        self.x, self.y = self._coordconvertor.from_wgs84(self.lat, self.lon)