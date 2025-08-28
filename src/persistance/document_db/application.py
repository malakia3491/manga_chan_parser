from tinydb import TinyDB

from persistance.document_db.repositories.ParsingAttemptRepository import ParsingAttemptRepository

class UnitOfWork:
    def __init__(self, db_instance: TinyDB):
        self._db = db_instance
        self.parsing_attempts = ParsingAttemptRepository(
           self._db.parsing_attempts
        )
    
    def __enter__(self):
        return self