import abc

class UrlBuilder:
    def __init__(
        self,
        base_domain: str=None
    ):
        self._base = base_domain
        
    @property
    def base(self) -> str:
        return f"https://{self._base}"
    
    
    @base.setter
    def base(self, value: str):
        self._base = value
        
    def build_url(self, path: str) -> str:
        if not self._base:
            raise ValueError("Base domain is not set")
        
        if self.base in path:
            return path
        else: return self.base + "/" + path.lstrip('/')
    
    @abc.abstractmethod
    def get_collection_page_url(
        self,
        page_number: int
    ) -> str:
        if not self.base: raise Exception() 
        return f"https://{self._base}/manga/newest/?offset={(page_number-1) * 20}"