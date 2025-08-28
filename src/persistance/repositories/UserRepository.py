from sqlalchemy.orm import Session

from domain.cache.CacheBase import CacheBase
from domain.entities.User import User
from persistance.mapping.MappingDirector import MappingDirector
from persistance.repositories.CachedRepository import CachedRepository
from persistance.models.models import User as UserModel

class UserRepository(CachedRepository[User, UserModel]):
    def __init__(self, session: Session, cache: CacheBase,  mapper: MappingDirector):
        super().__init__(session, cache, UserModel, mapper)