from typing import Type

from domain.enums import WorkType
from persistance.mapping.MapperBase import MapperBase
from persistance.mapping.mappers.AuthorMapper import AuthorMapper
from persistance.mapping.mappers.ChapterMapper import ChapterMapper
from persistance.mapping.mappers.SeriesMapper import SeriesMapper
from persistance.mapping.mappers.TagMapper import TagMapper
from persistance.mapping.mappers.UserMapper import UserMapper
from persistance.models.models import Work as WorkModel
from domain.entities.Work import Work

class WorkMapper(MapperBase[Work, WorkModel]):
    def __init__(
        self,
        series_mapper: SeriesMapper,
        author_mapper: AuthorMapper,
        user_mapper: UserMapper,
        tag_mapper: TagMapper,
        chapter_mapper: ChapterMapper,
    ):
        self._series_mapper = series_mapper
        self._author_mapper = author_mapper
        self._tag_mapper = tag_mapper
        self._chapter_mapper = chapter_mapper
        self._user_mapper = user_mapper
        
    @property
    def from_type(self) -> Type[Work]:
        return Work

    @property
    def to_type(self) -> Type[WorkModel]:
        return WorkModel
    
    def map_to(self, domain: Work) -> WorkModel:
        work_model = WorkModel(
            id=domain.id,
            type=domain.type.value,
            title=domain.title,
            description=domain.description,
            page_url=domain.page_url,
            series_id=domain.series.id,
            authors=[self._author_mapper.map_to(author) for author in domain.authors],
            tags=[self._tag_mapper.map_to(tag) for tag in domain.tags],
        )
        
        chapters = []
        for chapter_domain in domain.chapters:
            chapter_model = self._chapter_mapper.map_to(chapter_domain)
            chapter_model.work = work_model
            chapters.append(chapter_model)
        
        work_model.chapters = chapters
        return work_model
    
    def map_from(self, persistence: WorkModel) -> Work:
        return Work(
            id=persistence.id,
            type=WorkType(value=persistence.type),
            title=persistence.title,
            description=persistence.description,
            page_url=persistence.page_url,
            series=self._series_mapper.map_from(persistence.series),
            translators=[self._user_mapper.map_from(work_translator.user) for work_translator in persistence.work_translators],
            authors=[self._author_mapper.map_from(work_author.author) for work_author in persistence.work_authors],
            tags=[self._tag_mapper.map_from(work_tag.tag) for work_tag in persistence.work_tags],
            chapters=[self._chapter_mapper.map_from(chapter) for chapter in persistence.chapters],
        )