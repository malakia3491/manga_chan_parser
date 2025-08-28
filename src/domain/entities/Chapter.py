import uuid
from typing import Optional

from domain.cache.IndexNotifiable import indexed
from domain.entities.ParsingSession import ParsingSession

class Chapter:
    def __init__(
        self,
        parsing_session: ParsingSession,
        content_path: str,
        download_url: str,
        number: int=1,
        id: str= None        
    ):
        self._id = id or uuid.uuid4()
        self.parsing_session = parsing_session
        self.content_path = content_path
        self.download_url = download_url
        self.number = number
        
    @indexed
    @property
    def id(self) -> Optional[str]:
        return self._id
    
    def to_dict(self, include_related: bool = True) -> dict:
        """Сериализация Chapter в словарь с контролем глубины"""
        data = {
            "id": str(self.id),
            "content_path": self.content_path,
            "download_url": self.download_url,
            "number": self.number,
            "parsing_session_id": str(self.parsing_session.id)
        }
        
        if include_related:
            data["parsing_session"] = self.parsing_session.to_dict()
            
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Chapter':

        session_data = data.get('parsing_session')
        if not session_data:
            raise ValueError("Parsing session data is required")
            
        parsing_session = ParsingSession.from_dict(session_data)
        
        return cls(
            parsing_session=parsing_session,
            content_path=data['content_path'],
            download_url=data['download_url'],
            number=data.get('number', 1),
            id=data.get('id')
        )