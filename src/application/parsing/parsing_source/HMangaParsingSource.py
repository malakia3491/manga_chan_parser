import aiohttp

from application.parsing.ComixBee import ComixBee
from application.parsing.parser.HMangaParser import HMangaParser
from application.parsing.parsing_source.Base import ParsingSourceBase
from application.parsing.requester.ContentDownloader import ContentDownloader
from application.parsing.requester.DomainChecker import DomainChecker
from application.parsing.requester.RequestDirector import RequestDirector
from application.parsing.requester.Requester import Requester
from application.parsing.requester.UrlBuilders.HMangaUrlBuilder import HMangaUrlBuilder
from domain.filters.CFilterBuilder import CFilterBuilder

class HMangaParsingSource(ParsingSourceBase):
    def __init__(
        self,
        name: str,
        domains: list[str],
        destination: str,
        id: str=None,        
    ):
        super().__init__(
            name=name,
            domains=domains,
            destination=destination,
            id=id
        )       
        self._setup()
    
    def _setup(self):
        self.DEFAULT_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Dest": "document",
        "Cache-Control": "max-age=0",    
    }
    
    def build_comix_bee(self,) -> ComixBee:      
        timeout = aiohttp.ClientTimeout(
            total=120.0,
            connect=60.0,  
            sock_connect=60.0, 
            sock_read=60.0  
        )
        requester = Requester()
        request_director = RequestDirector(
            domains=self.domains,
            requester=requester,
            domain_checker=DomainChecker(requester=requester, timeout=60),
            downloader=ContentDownloader(destination_path=self.destination),
            headers=self.DEFAULT_HEADERS,
            timeout=timeout
        )        
        return ComixBee(
            request_director=request_director,
            comix_parser=HMangaParser(),
            url_builder=HMangaUrlBuilder(),
            cfilter_builder=CFilterBuilder(),
        )