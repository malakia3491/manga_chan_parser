from sqlalchemy.orm import Session

from domain.cache.CacheBase import CacheBase
from domain.entities.Author import Author
from persistance.mapping.MappingDirector import MappingDirector
from persistance.models.models import Author as AuthorModel
from persistance.mapping.mappers.AuthorMapper import AuthorMapper
from persistance.repositories.CachedRepository import CachedRepository

class AuthorRepository(CachedRepository[Author, AuthorModel]):
    def __init__(self, session: Session, cache: CacheBase, mapper: MappingDirector):
        super().__init__(session, cache, AuthorModel, mapper)