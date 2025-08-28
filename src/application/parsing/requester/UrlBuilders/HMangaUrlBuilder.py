
from application.parsing.requester.UrlBuilders.UrlBuilder import UrlBuilder

class HMangaUrlBuilder(UrlBuilder):
    def __init__(
        self,
        base_domain: str=None
    ):
        super().__init__(base_domain)
        
        
    def get_collection_page_url(
        self,
        page_number: int
    ) -> str:
        if not self.base: raise Exception() 
        return f"https://{self._base}/manga/newest/?offset={(page_number-1) * 20}"