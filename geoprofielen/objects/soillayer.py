__author__ = "Breinbaas | Rob van Putten"
__copyright__ = "Copyright 2020"
__credits__ = ["Rob van Putten"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Rob van Putten"
__email__ = "breinbaasnl@gmail.com"
__status__ = "Development"

from pydantic import BaseModel

class SoilLayer(BaseModel):
    z_top: float
    z_bottom: float
    soilcode: str

    @property
    def height(self):
        return self.z_top - self.z_bottom