import abc
from typing import Any

class Parser:        

    @abc.abstractmethod
    def parse_collection_page(self, html_content: str) -> list[dict[str, Any]]:
        pass

    @abc.abstractmethod
    def parse_manga_page(self, html_content: str) -> str:
        pass
    
    @abc.abstractmethod
    def parse_download_page(self, html_content: str) -> list[dict[str, str]]:
        pass