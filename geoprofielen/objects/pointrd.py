__author__ = "Breinbaas | Rob van Putten"
__copyright__ = "Copyright 2020"
__credits__ = ["Rob van Putten"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Rob van Putten"
__email__ = "breinbaasnl@gmail.com"
__status__ = "Development"

from pydantic import BaseModel
import numpy as np

from .coordconvertor import RDWGS84Converter

class PointRD(BaseModel):
    chainage: int = 0
    x: float = np.nan
    y: float = np.nan
    lat: float = np.nan
    lon: float = np.nan
    _coordconvertor = RDWGS84Converter()

    def to_rd(self) -> None:
        self.x, self.y = self._coordconvertor.from_wgs84(self.lat, self.lon)

    def to_wgs84(self) -> None:
        self.lat, self.lon = self._coordconvertor.from_rd(self.x, self.y)