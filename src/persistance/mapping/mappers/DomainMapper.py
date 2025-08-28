from typing import Type
from domain.entities.Address import Address
from persistance.mapping.MapperBase import MapperBase
from persistance.models.models import Domain

class DomainMapper(MapperBase[Address, Domain]):
    @property
    def from_type(self) -> Type[Address]:
        return Address

    @property
    def to_type(self) -> Type[Domain]:
        return Domain    

    def map_to(self, domain: Address) -> Domain:
        return Domain(
            id=domain.id,
            address=domain.address
        )
    
    def map_from(self, persistence: Domain) -> Address:
        return Address(
            id=persistence.id,
            address=persistence.address,
        )