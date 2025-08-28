from sqlalchemy.orm import Session

from application.parsing.parsing_source.Base import ParsingSourceBase
from domain.cache.CacheBase import CacheBase
from persistance.mapping.MappingDirector import MappingDirector
from persistance.repositories.CachedRepository import CachedRepository
from persistance.models.models import Source as SourceModel

class SourceRepository(CachedRepository[ParsingSourceBase, SourceModel]):
    def __init__(self, session: Session, cache: CacheBase,  mapper: MappingDirector):
        super().__init__(session, cache, SourceModel, mapper)