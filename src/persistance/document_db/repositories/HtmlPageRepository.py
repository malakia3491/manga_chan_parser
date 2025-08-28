from tinydb import Query
from tinydb.table import Table

from domain.entities.documents.HtmlPage import HtmlPage

class HtmlPageRepository:
    def __init__(self, table: Table):
        self.table = table
        self.query = Query()
        
    def insert(self, page: HtmlPage) -> int:
        """Возвращает doc_id созданного документа"""
        return self.table.insert(page.to_dict())
    
    def get_by_id(self, doc_id: int) -> HtmlPage:
        doc = self.table.get(doc_id=doc_id)
        if doc:
            return HtmlPage.from_dict(doc) if doc else None
        return None
    
    def get_by_url(self, url: str) -> HtmlPage:
        doc = self.table.get(self.query.url == url)
        return HtmlPage.from_dict(doc) if doc else None
    
    def get_all(self) -> list[HtmlPage]:
        return [HtmlPage.from_dict(doc) for doc in self.table.all()]
    
    def update(self, doc_id: int, page: HtmlPage):
        self.table.update(page.to_dict(), doc_ids=[doc_id])
    
    def delete(self, doc_id: int):
        self.table.remove(doc_ids=[doc_id])