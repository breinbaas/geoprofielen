from pydantic import BaseModel
from typing import List

from .pointrd import PointRD

class DijkTraject(BaseModel):
    id: str = ""
    naam: str = ""
    referentielijn: List[PointRD] = []

    