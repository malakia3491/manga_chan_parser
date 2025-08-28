from typing import Type
from application.parsing.parsing_source.sources import ParsingSourceBase, MangaParsingSource, HMangaParsingSource
from persistance.mapping.mappers.DomainMapper import DomainMapper
from persistance.mapping.mappers.ParsingSessionMapper import ParsingSessionMapper
from persistance.models.models import Source as SourceModel
from persistance.mapping.MapperBase import MapperBase

class SourceMapper(MapperBase[ParsingSourceBase, SourceModel]):
    def __init__(
        self,
        domain_mapper: DomainMapper,
        parsing_session_mapper: ParsingSessionMapper
    ):
        self._domain_mapper = domain_mapper
        self._parsing_session_mapper = parsing_session_mapper
    
    @property
    def from_type(self) -> Type[ParsingSourceBase]:
        return ParsingSourceBase

    @property
    def to_type(self) -> Type[SourceModel]:
        return SourceModel  
    
    def map_to(self, domain: ParsingSourceBase) -> SourceModel:
        return SourceModel(
            code=domain.id,
            name=domain.name,
            domains=[self._domain_mapper.map_to(domain) for domain in domain.domains],
        )
    
    def map_from(self, persistence: SourceModel) -> ParsingSourceBase:
        if persistence.id == 0:
            source = HMangaParsingSource(
                id=persistence.id,
                name=persistence.name,
                destination=persistence.destination,
                domains=[self._domain_mapper.map_from(domain) for domain in persistence.domains],
            )
        elif persistence.id == 1:
            source = MangaParsingSource(
                id=persistence.id,
                name=persistence.name,
                destination=persistence.destination,
                domains=[self._domain_mapper.map_from(domain) for domain in persistence.domains],
            )        
        return source