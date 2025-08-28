from typing import Type
from persistance.mapping.MapperBase import MapperBase
from persistance.models.models import Author as AuthorModel
from domain.entities.Author import Author

class AuthorMapper(MapperBase[Author, AuthorModel]):
    @property
    def from_type(self) -> Type[Author]:
        return Author

    @property
    def to_type(self) -> Type[AuthorModel]:
        return AuthorModel
    
    def map_to(self, domain: Author) -> AuthorModel:
        return AuthorModel(
            id=domain.id,
            name=domain.name,
        )
    
    def map_from(self, persistence: AuthorModel) -> Author:
        return Author(
            id=persistence.id,
            name=persistence.name,
        )