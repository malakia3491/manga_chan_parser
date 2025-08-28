from typing import Dict, Any

from domain.filters.Filter import CFilter

class CFilterPipeline:
    def __init__(self, filters: list[CFilter]):
        """
        :param condition: Лямбда-функция, принимающая комикс и возвращающая bool
        """
        self._filters = filters.copy()
        self._query = self._create(filters)
    
    def _create(self, filters: list) -> CFilter:        
        combined = CFilter(lambda c: True)
        for f in reversed(filters):
            combined = combined & f
        return combined
    
    def apply(self, comix_info: Dict[str, Any]) -> bool:
        return self._query.apply(comix_info)
    
    def apply_many(self, comics_info: list[Dict[str, Any]]) -> list[bool]:
        mask = [True]*len(comics_info)
        for i, comix_info in enumerate(comics_info):
            mask[i] = self.apply(comix_info)
        return mask