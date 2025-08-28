from datetime import datetime
from typing import Any

from domain.entities.documents.HtmlPage import HtmlPage

class ParsingAttempt:
    def __init__(
        self,
        collection_page: HtmlPage=None,
        page: HtmlPage=None,
        download_page: HtmlPage=None, 
        parsed_data: dict[str, Any]=None,
        created_at: datetime=None
    ):
        self.collection_page = collection_page  
        self.page = page  
        self.download_page = download_page 
        self.parsed_data = parsed_data or {}
        self.created_at = created_at or datetime.now()
        
    def to_dict(self) -> dict[str, Any]:
        return {
            'collection_page': self.collection_page.to_dict(),
            'page': self.page.to_dict(),
            'download_page': self.download_page.to_dict(),
            'parsed_data': self.parsed_data,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            collection_page=HtmlPage.from_dict(data['collection_page']),
            page=HtmlPage.from_dict(data['page']),
            download_page=HtmlPage.from_dict(data['download_page']),
            parsed_data=data.get('parsed_data', {}),
            created_at=datetime.fromisoformat(data['created_at'])
        )