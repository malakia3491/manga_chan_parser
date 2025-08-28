from typing import Type
from domain.entities.Series import Series
from persistance.models.models import Series as SeriesModel
from persistance.mapping.MapperBase import MapperBase

class SeriesMapper(MapperBase[Series, SeriesModel]):
    @property
    def from_type(self) -> Type[Series]:
        return Series

    @property
    def to_type(self) -> Type[SeriesModel]:
        return SeriesModel    
    
    def map_to(self, domain: Series) -> SeriesModel:
        return SeriesModel(
            id=domain.id,
            name=domain.name
        )
    
    def map_from(self, persistence: SeriesModel) -> Series:
        return Series(
            id=persistence.id,
            name=persistence.name
        )