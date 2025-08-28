import aiohttp
from typing import Dict
from fake_useragent import UserAgent

from application.parsing.exceptions import NoOneAvailableDomen
from application.parsing.requester.ContentDownloader import ContentDownloader
from application.parsing.requester.DomainChecker import DomainChecker
from application.parsing.requester.Requester import Requester
from domain.entities.Address import Address

DEFAULT_HEADERS = {
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

class RequestDirector:
    def __init__(
        self,
        requester: Requester,
        domain_checker: DomainChecker,
        downloader: ContentDownloader,
        domains: list[Address],
        headers: dict[str, str],
        timeout
    ):
        self._domains = [domain.address for domain in domains]
        self._requester = requester
        self._domain_checker = domain_checker
        self._downloader = downloader
        self._session: aiohttp.ClientSession = None
        self._user_agent = UserAgent()
        self._headers = headers or DEFAULT_HEADERS
        self.timeout = timeout

    async def initialize(self):
        await self.open()
        domain = await self.get_available_domain(self._domains)        
        if not domain:
            raise NoOneAvailableDomen()              
        self.base = domain                
    
    def _generate_headers(self) -> Dict[str, str]:
        return {
            **self._headers,
            "User-Agent": self._user_agent.random
        }
     
    def _update_sesson(self, session: aiohttp.ClientSession):
        self._requester.session = session
        self._downloader.session = session
        
    async def open(self):
        if self._session:
            await self.close()
        self._session = aiohttp.ClientSession(
            headers=self._generate_headers(),
            timeout=self.timeout
        ) 
        self._update_sesson(self._session)
    
    async def close(self):
        if not self._session:
            raise ValueError()
        await self._session.close()
        self._session = None            
        self._update_sesson(self._session)
        
    async def get(self, url: str):
        return await self._requester.get(url)
    
    async def head(self, url: str):
        return await self._requester.head(url)
    
    async def download(self, url: str, filename: str):
        return await self._downloader.download(url=url, filename=filename)
    
    async def get_available_domain(self, domains: list[str]):
        return await self._domain_checker.get_available_domain(domains)