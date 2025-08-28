from datetime import datetime
from typing import Any, Optional

from domain.filters.Filter import CFilter
from domain.filters.CFilterPipeline import CFilterPipeline

class CFilterBuilder:
    def build(
        self,   
        start_date: Optional[datetime]=None,
        end_date: Optional[datetime]=None, 
        author_names:Optional[list[str]]=[],       
        translator_names: Optional[list[str]]=[],    
        uploader_names: Optional[list[str]]=[],  
        include_tags: Optional[list[str]]=[],   
        except_tags: Optional[list[str]]=[],
    )-> CFilterPipeline:
        cfilters: list[CFilter] = []        
        if start_date and end_date:
            cfilters.append(self._create_period_cfilter('upload_date', start_date, end_date, "Upload date period filter"))      
        if author_names:
            cfilters.append(self._create_in_cfilter('authors', author_names, "Author filter", any))    
        if translator_names:
            cfilters.append(self._create_in_cfilter('translators', translator_names, "Translator filter", any))    
        if uploader_names:
            cfilters.append(self._create_in_cfilter('uploader', uploader_names, "Uploader filter", any))   
        if include_tags:
            cfilters.append(self._create_not_in_cfilter('tags', include_tags, "Except tag filter", all))    
        if except_tags:
            cfilters.append(self._create_in_cfilter('tags', include_tags, "Include tag filter", all))
              
        return CFilterPipeline(cfilters)
        
    def _create_period_cfilter(
        self,
        field: str,
        start: Any,
        end: Any,
        name: str = "Unnamed filter",
    ) -> CFilter:
        condition = lambda data: start <= data[field] and data[field] <= end 
        return CFilter(condition, name)
   
    def _create_in_cfilter(
        self,
        field: str,
        collection: list,
        method,
        name: str = "Unnamed filter",        
    ) -> CFilter:
        condition = lambda data: method(value in collection for value in data[field])
        return CFilter(condition, name)
    
    def _create_not_in_cfilter(
        self,
        field: str,
        collection: list,
        method,
        name: str = "Unnamed filter",        
    ) -> CFilter:
        condition = lambda data: method(value not in collection for value in data[field])
        return CFilter(condition, name)   
    
    def _create_check_cfilter(
        self,
        field: Any,
        right: Any,
        name: str = "Unnamed filter",
    ) -> CFilter:
        return CFilter(lambda data: data[field] == right, name)