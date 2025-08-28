import abc
from pathlib import Path

from application.parsing.ComixBee import ComixBee
from domain.cache.IndexNotifiable import indexed
from domain.entities.Address import Address
from persistance.document_db.application import UnitOfWork

class ParsingSourceBase:
    def __init__(
        self,
        name: str,
        domains: list[Address],
        destination: str,
        id: str=None,        
    ):
        self._name = name
        self._domains = domains
        self._destination = Path(destination)
        self._id = id    
    
    @indexed
    @property
    def id(self) -> str:
        return self._id

    @indexed
    @property
    def name(self) -> str:
        return self._name

    @property
    def destination(self) -> str:
        return self._destination

    @property    
    def domains(self) -> list[Address]:
        return self._domains
    
    @abc.abstractmethod
    def build_comix_bee(self) -> ComixBee:
        pass