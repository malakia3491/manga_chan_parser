import aiohttp
from fake_useragent import UserAgent

from application.parsing.ComixBee import ComixBee
from application.parsing.parser.MangaChanParser import MangaChanParser
from application.parsing.parsing_source.Base import ParsingSourceBase
from application.parsing.requester.ContentDownloader import ContentDownloader
from application.parsing.requester.DomainChecker import DomainChecker
from application.parsing.requester.RequestDirector import RequestDirector
from application.parsing.requester.Requester import Requester
from application.parsing.requester.UrlBuilders.MangaUrlBuilder import MangaUrlBuilder
from domain.filters.CFilterBuilder import CFilterBuilder

class MangaParsingSource(ParsingSourceBase):
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
        "Referer": "https://im.manga-chan.me/",
    }
    
    def build_comix_bee(self,) -> ComixBee:      
        timeout = aiohttp.ClientTimeout(
            total=60.0,  # Общий таймаут
            connect=30.0,  # Таймаут подключения
            sock_connect=30.0,  # Таймаут установки соединения
            sock_read=30.0  # Таймаут чтения данных
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
            comix_parser=MangaChanParser(),
            url_builder=MangaUrlBuilder(),
            cfilter_builder=CFilterBuilder(),
        )