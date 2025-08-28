import uuid
from typing import Any

from domain.cache.IndexNotifiable import indexed

class Author:
    def __init__(
        self,
        name: str,
        id: str=None
    ):
        self._name = name
        self._id = id or uuid.uuid4()

    @indexed
    @property        
    def id(self) -> str:
        return self._id
    
    @indexed
    @property        
    def name(self) -> str:
        return self._name
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'Author':
        return Author(
            name=data['name'],
            id=data.get('id')
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'id': self.id
        }