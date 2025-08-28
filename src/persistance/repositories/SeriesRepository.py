from typing import Optional
from sqlalchemy.orm import Session

from domain.cache.CacheBase import CacheBase
from domain.entities.Series import Series
from persistance.mapping.MappingDirector import MappingDirector
from persistance.models.models import Series as SeriesModel
from persistance.mapping.mappers.SeriesMapper import SeriesMapper
from persistance.repositories.CachedRepository import CachedRepository

class SeriesRepository(CachedRepository[Series, SeriesModel]):
    def __init__(self, session: Session, cache: CacheBase, mapper: MappingDirector):
        super().__init__(session, cache, SeriesModel, mapper)