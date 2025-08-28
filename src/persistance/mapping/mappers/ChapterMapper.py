from typing import Type
from domain.entities.Chapter import Chapter
from persistance.mapping.mappers.ParsingSessionMapper import ParsingSessionMapper
from persistance.mapping.mappers.UserMapper import UserMapper
from persistance.models.models import Chapter as ChapterModel
from persistance.mapping.MapperBase import MapperBase

class ChapterMapper(MapperBase[Chapter, ChapterModel]):
    def __init__(
        self,
        user_mapper: UserMapper,
        parsing_session_mapper: ParsingSessionMapper,
    ):
        self._user_mapper = user_mapper
        self._parsing_session_mapper = parsing_session_mapper
        
    @property
    def from_type(self) -> Type[Chapter]:
        return Chapter

    @property
    def to_type(self) -> Type[ChapterModel]:
        return ChapterModel    
    
    def map_to(self, domain: Chapter) -> ChapterModel:
        return ChapterModel(
            id=domain.id,
            number=domain.number,
            content_path=domain.content_path,
            download_url=domain.download_url,
            parsing_session_id=domain.parsing_session.id,
        )
    
    def map_from(self, persistence: ChapterModel) -> Chapter:
        return Chapter(
            id=persistence.id,
            number=persistence.number,
            content_path=persistence.content_path,
            download_url=persistence.download_url,
            parsing_session=self._parsing_session_mapper.map_from(persistence.parsing_session),
        )
