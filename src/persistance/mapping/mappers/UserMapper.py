from typing import Type
from domain.entities.User import User
from persistance.models.models import User as UserModel
from persistance.mapping.MapperBase import MapperBase

class UserMapper(MapperBase[User, UserModel]):   
    @property
    def from_type(self) -> Type[User]:
        return User

    @property
    def to_type(self) -> Type[UserModel]:
        return UserModel 
    
    def map_to(self, domain: User) -> UserModel:
        return UserModel(
            id=domain.id,
            name=domain.name
        )
    
    def map_from(self, persistence: UserModel) -> User:
        return User(
            id=persistence.id,
            name=persistence.name
        )