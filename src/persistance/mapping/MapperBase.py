import abc
from typing import Generic, Type, TypeVar

T = TypeVar('T', bound=object)
T1 = TypeVar('T1', bound=object)

class MapperBase(Generic[T, T1], abc.ABC):
    @property
    def from_type(self) -> Type[T]:
        T

    @property
    def to_type(self) -> Type[T1]:
        T1

    @abc.abstractmethod
    def map_to(self, mapping_obj: T) -> T1:
        pass

    @abc.abstractmethod 
    def map_from(self, mapping_obj: T1) -> T:
        pass