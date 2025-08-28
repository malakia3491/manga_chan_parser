import logging

from domain.cache.InMemoryCache import InMemoryCache
from persistance.repositories.AuthorRepository import AuthorRepository
from persistance.repositories.WorkRepository import WorkRepository
from persistance.repositories.ParsingSessionRepository import ParsingSessionRepository
from persistance.repositories.SeriesRepository import SeriesRepository
from persistance.repositories.SourceRepository import SourceRepository
from persistance.repositories.TagRepository import TagRepository
from persistance.repositories.UserRepository import UserRepository

class UnitOfWork:
    def __init__(self, session_factory, mapping_director):
        self.session_factory = session_factory
        self.mapping_director = mapping_director
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def __aenter__(self):
        self.logger.info(f"Инициализация репозиториев")
        self.session = self.session_factory()
        
        self.comics_cache = InMemoryCache()
        self.series_cache = InMemoryCache()
        self.sources_cache = InMemoryCache()
        self.tags_cache = InMemoryCache()
        self.authors_cache = InMemoryCache()
        self.users_cache = InMemoryCache()      
        self.parsing_sessions_cache = InMemoryCache()  
        
        self.comics = WorkRepository(self.session, self.comics_cache, self.mapping_director)
        self.series = SeriesRepository(self.session, self.series_cache, self.mapping_director)
        self.sources = SourceRepository(self.session, self.sources_cache, self.mapping_director)
        self.tags = TagRepository(self.session, self.tags_cache, self.mapping_director)
        self.authors = AuthorRepository(self.session, self.authors_cache, self.mapping_director)
        self.users = UserRepository(self.session, self.users_cache, self.mapping_director)
        self.parsing_sessions = ParsingSessionRepository(self.session, self.parsing_sessions_cache, self.mapping_director)
        self.logger.info(f"Инициализация репозиториев завершена")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.session.close()
        
    async def commit(self):
        self.logger.info(f"Синхронизация репозиториев с БД")
        await self.authors.commit()
        await self.users.commit()        
        await self.tags.commit()
        await self.series.commit()
        await self.sources.commit()
        await self.parsing_sessions.commit()               
        await self.comics.commit()
            
        await self.session.commit()
        self.logger.info(f"Синхронизация репозиториев с БД завершена")
        
    async def rollback(self):
        await self.session.rollback()
        
        await self.comics.rollback()
        await self.series.rollback()
        await self.sources.rollback()
        await self.parsing_sessions.rollback()
        await self.tags.rollback()
        await self.authors.rollback()
        await self.users.rollback()