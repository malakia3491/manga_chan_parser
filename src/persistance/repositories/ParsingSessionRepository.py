from sqlalchemy.orm import Session

from domain.cache.CacheBase import CacheBase
from domain.entities.ParsingSession import ParsingSession
from persistance.mapping.MappingDirector import MappingDirector
from persistance.models.models import ParsingSession as ParsingSessionModel
from persistance.mapping.mappers.ParsingSessionMapper import ParsingSessionModel
from persistance.repositories.CachedRepository import CachedRepository

class ParsingSessionRepository(CachedRepository[ParsingSession, ParsingSessionModel]):
    def __init__(self, session: Session, cache: CacheBase, mapper: MappingDirector):
        super().__init__(session, cache, ParsingSessionModel, mapper)