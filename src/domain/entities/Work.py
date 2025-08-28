from typing import Optional
import uuid

from domain.cache.IndexNotifiable import indexed
from domain.entities.User import User
from domain.entities.Chapter import Chapter
from domain.entities.Author import Author
from domain.entities.Series import Series
from domain.entities.Tag import Tag
from domain.enums import WorkType, parse_work_type

class Work:
    def __init__(
        self,
        title: str,
        type: WorkType,
        page_url: str,
        authors: list[Author],
        translators: list[User],
        tags: list[Tag],
        chapters: list[Chapter],
        series: Series=None,
        description: str="",
        id: str=None,
    ):
        self.title = title
        self._type = type
        self.page_url = page_url
        self.authors = authors
        self.tags = tags
        self.chapters = chapters
        self.translators = translators
        self.series = series
        self.description = description
        self._id = id or uuid.uuid4()
        
    @indexed
    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: Optional[str]) -> None:
        self._id = value
        
    @property
    def type(self) -> str:
        return self._type.value or self._type
         
    @type.setter
    def type(self, value: WorkType):
        self._type = value
        
    def find_chapter_number(self, number: int):
        for chapter in self.chapters:
            if chapter.number == number:
                return chapter
        return None
    
    def to_dict(self, include_related: bool = True) -> dict:
        """Сериализация Work в словарь с контролем глубины"""
        data = {
            "id": str(self.id) if self.id else None,
            "title": self.title,
            "_type": self._type.value if hasattr(self._type, 'value') else str(self._type),
            "page_url": self.page_url,
            "description": self.description,
            "chapters": [ch.to_dict(include_related=False) for ch in self.chapters]
        }
        
        if include_related:
            data.update({
                "authors": [auth.to_dict() for auth in self.authors],
                "translators": [tr.to_dict() for tr in self.translators],
                "tags": [tag.to_dict() for tag in self.tags],
                "series": self.series.to_dict() if self.series else None
            })
        else:
            data.update({
                "author_ids": [str(auth.id) for auth in self.authors],
                "translator_ids": [str(tr.id) for tr in self.translators],
                "tag_ids": [str(tag.id) for tag in self.tags]
            })
            
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Work':
        authors = [Author.from_dict(auth_data) for auth_data in data.get('authors', [])]
        translators = [User.from_dict(user_data) for user_data in data.get('translators', [])]
        tags = [Tag.from_dict(tag_data) for tag_data in data.get('tags', [])]
        chapters = [Chapter.from_dict(ch_data) for ch_data in data.get('chapters', [])]
        
        series_data = data.get('series')
        series = Series.from_dict(series_data) if series_data else None
        
        work_type = parse_work_type(data['type'])
        work_type = WorkType(data['type']) if not work_type else data['type']
        
        return cls(
            title=data['title'],
            _type=work_type,
            page_url=data['page_url'],
            authors=authors,
            translators=translators,
            tags=tags,
            chapters=chapters,
            series=series,
            description=data.get('description', ''),
            id=data.get('id')
        )