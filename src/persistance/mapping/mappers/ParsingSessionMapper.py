from typing import Type
from domain.entities.ParsingSession import ParsingSession
from persistance.models.models import ParsingSession as ParsingSessionModel
from persistance.mapping.MapperBase import MapperBase

class ParsingSessionMapper(MapperBase[ParsingSession, ParsingSessionModel]):
    @property
    def from_type(self) -> Type[ParsingSession]:
        return ParsingSession

    @property
    def to_type(self) -> Type[ParsingSessionModel]:
        return ParsingSessionModel    
    
    def map_to(self, domain: ParsingSession) -> ParsingSessionModel:
        return ParsingSessionModel(
            id=domain.id,
            parsing_date=domain.parsing_date,
            source_id=domain.source_id
        )
    
    def map_from(self, persistence: ParsingSessionModel) -> ParsingSession:
        return ParsingSession(
            id=persistence.id,
            source_id=persistence.source_id,
            parsing_date=persistence.parsing_date,
        )