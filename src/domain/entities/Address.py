import uuid
from typing import Any

from domain.cache.IndexNotifiable import indexed

class Address:
    def __init__(
        self,
        address: str,
        id: str=None
    ):
        self._address = address
        self._id = id or uuid.uuid4()
         
    @indexed
    @property
    def id(self):
        return self._id    
 
    @indexed
    @property
    def address(self):
        return self._address
    
    @staticmethod
    def from_dict(dict: dict[str, Any]) -> 'Address':
        return Address(
            address=dict['address'],
            id=dict['id'] if 'id' in dict else None 
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.address,
            'id': self.id
        }