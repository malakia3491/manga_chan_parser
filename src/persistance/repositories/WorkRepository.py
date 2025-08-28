from sqlalchemy.orm import Session

from domain.cache.CacheBase import CacheBase
from domain.entities.Work import Work
from persistance.mapping.MappingDirector import MappingDirector
from persistance.models.models import Work as WorkModel
from persistance.repositories.CachedRepository import CachedRepository

class WorkRepository(CachedRepository[Work, WorkModel]):
    def __init__(self, session: Session, cache: CacheBase, mapper: MappingDirector):
        super().__init__(session, cache, WorkModel, mapper)