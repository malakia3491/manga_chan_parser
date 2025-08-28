from typing import Optional
from sqlalchemy.orm import Session

from domain.cache.CacheBase import CacheBase
from domain.entities.Tag import Tag
from persistance.mapping.MappingDirector import MappingDirector
from persistance.mapping.mappers.TagMapper import TagMapper
from persistance.repositories.CachedRepository import CachedRepository
from persistance.models.models import Tag as TagModel

class TagRepository(CachedRepository[Tag, TagModel]):
    def __init__(self, session: Session, cache: CacheBase, mapper: MappingDirector):
        super().__init__(session, cache, TagModel, mapper)