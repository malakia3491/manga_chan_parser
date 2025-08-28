import os
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ArgumentError
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from domain.config.Config import Config
from persistance.document_db.application import UnitOfWork as DocumentUnitOfWork
from persistance.Application import UnitOfWork
from persistance.mapping.MappingDirector import MappingDirector
from persistance.mapping.mappers.AuthorMapper import AuthorMapper
from persistance.mapping.mappers.WorkMapper import WorkMapper
from persistance.mapping.mappers.ChapterMapper import ChapterMapper
from persistance.mapping.mappers.DomainMapper import DomainMapper
from persistance.mapping.mappers.ParsingSessionMapper import ParsingSessionMapper
from persistance.mapping.mappers.SeriesMapper import SeriesMapper
from persistance.mapping.mappers.SourceMapper import SourceMapper
from persistance.mapping.mappers.TagMapper import TagMapper
from persistance.mapping.mappers.UserMapper import UserMapper
from persistance.models.BaseModel import Base

class Initializator:
    def __init__(self, config: Config):
        self._config = config  
        self._is_initialized = False
    
    async def create_session_fabric(self, path: str = ""):
        """
        path: либо пустая строка (использовать значение из конфигурации),
              либо путь к файлу БД (например "src/persistance/db/comics.db"),
              либо уже сформированная строка подключения (например "sqlite+aiosqlite:///C:/...").
        Возвращает factory для AsyncSession.
        """
        raw = path if path else self._config.get_db_connection()

        if isinstance(raw, str) and not raw.startswith("sqlite"):
            db_path = Path(raw)
            db_path = db_path.expanduser().resolve()
            db_path.parent.mkdir(parents=True, exist_ok=True)

            sql_connection = self._config.get_db_path()+db_path.as_posix()
        else:
            sql_connection = raw

        try:
            engine = create_async_engine(sql_connection, echo=False)
        except ArgumentError as ae:
            raise RuntimeError(f"Невалидная строка подключения к БД: {sql_connection}") from ae
        except Exception as e:
            raise

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

            initial_file_path = self._config.get_db_initial_file()
            if initial_file_path and os.path.exists(initial_file_path):
                with open(initial_file_path, 'r', encoding='utf-8') as sql_file:
                    sql_script = sql_file.read()

                commands = [
                    cmd.strip()
                    for cmd in sql_script.split(';')
                    if cmd.strip() and not cmd.strip().startswith('--')
                ]

                for command in commands:
                    await conn.execute(text(command))

        AsyncSessionLocalFabric = sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False
        )

        self._is_initialized = True
        return AsyncSessionLocalFabric
    
    async def initialize(self, db_path: str="") -> UnitOfWork:
        parsing_session_mapper = ParsingSessionMapper()
        domain_mapper = DomainMapper()
        tag_mapper = TagMapper()
        series_mapper = SeriesMapper()
        user_mapper = UserMapper()
        author_mapper = AuthorMapper()
        chapter_mapper = ChapterMapper(
            user_mapper=user_mapper,
            parsing_session_mapper=parsing_session_mapper,
        )
        mappers = [
            parsing_session_mapper,
            domain_mapper,
            tag_mapper,
            series_mapper,
            user_mapper,
            author_mapper,
            SourceMapper(
                domain_mapper=domain_mapper,
                parsing_session_mapper=parsing_session_mapper
            ),
            WorkMapper(
                series_mapper=series_mapper,
                author_mapper=author_mapper,
                tag_mapper=tag_mapper,         
                chapter_mapper=chapter_mapper,
                user_mapper=user_mapper
            ),            
        ]  
        mapping_director = MappingDirector(mappers)        
        session_factory = await self.create_session_fabric(path=db_path)
        return UnitOfWork(session_factory, mapping_director)
    
    def _document_db_initialize(self) -> TinyDB:
        db_path = self._config.get_ddb_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        db = TinyDB(
            db_path, 
            storage=CachingMiddleware(JSONStorage),
            indent=4 
        )
        self.html_pages = db.table('html_pages')
        self.parsing_attempts = db.table('parsing_attempts')
        return db
    
    def document_db_initialize(self) -> DocumentUnitOfWork:
        db = self._document_db_initialize()
        return DocumentUnitOfWork(db)