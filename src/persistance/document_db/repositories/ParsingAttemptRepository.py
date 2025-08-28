from typing import Any
from tinydb import Query
from tinydb.table import Table

from domain.entities.documents.ParsingAttempt import ParsingAttempt
from persistance.document_db.repositories.HtmlPageRepository import HtmlPageRepository

class ParsingAttemptRepository:
    def __init__(
        self,
        table: Table,
        html_page_repository: HtmlPageRepository 
    ):
        self.table = table
        self._html_page_repository = html_page_repository
        self.query = Query()
        
    def insert(self, attempt: ParsingAttempt) -> int:
        attempt_dict = attempt.to_dict()
        attempt_dict['collection_page_id'] = self._html_page_repository.insert(attempt.collection_page) if attempt.collection_page else None 
        attempt_dict['page_id'] = self._html_page_repository.insert(attempt.page) if attempt.page else None
        attempt_dict['download_page_id'] = self._html_page_repository.insert(attempt.download_page) if attempt.download_page else None
        attempt_dict.pop('collection_page')
        attempt_dict.pop('page')
        attempt_dict.pop('download_page')
        return self.table.insert(attempt_dict)
    
    def get_by_id(self, doc_id: int) -> ParsingAttempt:
        doc = self.table.get(doc_id=doc_id)
        doc = self._get_pages_by_id(doc)
        return ParsingAttempt.from_dict(doc) if doc else None
    
    def get_by_domain(self, domain: str) -> list[ParsingAttempt]:
        docs = self.table.search(self.query.domain == domain)
        docs = [self._get_pages_by_id(doc) for doc in docs]
        return [ParsingAttempt.from_dict(doc) for doc in docs]
    
    def get_all(self) -> list[ParsingAttempt]:
        docs = self.table.all()
        docs = [self._get_pages_by_id(doc) for doc in docs]
        return [ParsingAttempt.from_dict(doc) for doc in docs]
    
    def update_parsed_data(self, doc_id: int, parsed_data: dict):
        self.table.update({'parsed_data': parsed_data}, doc_ids=[doc_id])
    
    def delete(self, doc_id: int):
        self.table.remove(doc_ids=[doc_id])
        
    def _get_pages_by_id(self, doc: dict[str, Any]):
        doc['collection_page'] = self._html_page_repository.get_by_id(doc['collection_page_id'])
        doc['page'] = self._html_page_repository.get_by_id(doc['page_id'])
        doc['download_page'] =  self._html_page_repository.get_by_id(doc['download_page_id'])
        return doc