from datetime import datetime
from typing import Any
import uuid
from domain.cache.IndexNotifiable import indexed

class ParsingSession:
    def __init__(
        self,
        source_id: str,
        parsing_date: datetime=datetime.now(),
        id: str=None
    ):
        self._parsing_date = parsing_date
        self.source_id = source_id
        self._id = id or uuid.uuid4()
    
    @indexed
    @property        
    def id(self) -> str:
        return self._id
    
    @property
    def parsing_date(self) -> datetime:
        return self._parsing_date
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'ParsingSession':
        return ParsingSession(
            parsing_date=data['parsing_date'],
            id=data.get('id')
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            'parsing_date': self.parsing_date,
            'id': self.id
        }