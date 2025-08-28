from typing import Type
from domain.entities.Tag import Tag
from persistance.models.models import Tag as TagModel
from persistance.mapping.MapperBase import MapperBase

class TagMapper(MapperBase[Tag, TagModel]):
    @property
    def from_type(self) -> Type[Tag]:
        return Tag

    @property
    def to_type(self) -> Type[TagModel]:
        return TagModel  
    
    def map_to(self, domain: Tag) -> TagModel:
        return TagModel(
            id=domain.id,
            name=domain.name
        )
    
    def map_from(self, persistence: TagModel) -> Tag:
        return Tag(
            id=persistence.id,
            name=persistence.name
        )
