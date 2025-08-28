from typing import Type, Dict, Tuple, Callable, Any

from persistance.mapping.MapperBase import MapperBase

class MappingDirector:
    def __init__(self, mappers: list[MapperBase]):
        self._mapping_dict: Dict[Tuple[Type, Type], Tuple[MapperBase, Callable]] = {}
        
        for mapper in mappers:
            from_type = mapper.from_type
            to_type = mapper.to_type
            
            self._mapping_dict[from_type] = (mapper, mapper.map_to)
            self._mapping_dict[to_type] = (mapper, mapper.map_from)

    def map(self, obj: Any, map_to_type: Type) -> Any:
        map_from_type = type(obj)
        key = map_from_type
        
        if key not in self._mapping_dict:
            raise ValueError(f"No mapper found for {map_from_type} -> {map_to_type}")
        
        _, method = self._mapping_dict[key]
        
        if not isinstance(obj, map_from_type):
            raise TypeError(f"Object must be instance of {map_from_type}, got {type(obj)}")
        
        return method(obj)