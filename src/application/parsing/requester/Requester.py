import asyncio
import logging
import aiohttp
import random

from typing import Optional, Tuple, List

class Requester:
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
    
    def __init__(
        self,
        delay_range: Tuple[float, float] = (1.0, 4.0),
        retries: int = 5,
        backoff_factor: float = 0.7,
        use_proxy: bool = False,
        proxy_pool: Optional[List[str]] = None
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.delay_range = delay_range
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.use_proxy = use_proxy
        self.proxy_pool = proxy_pool or []
        self._session = None
        self._last_request_time = 0

    @property
    def session(self):
        return self._session

    @session.setter    
    def session(self, session: aiohttp.ClientSession):
        self._session = session
    
    async def _get_proxy(self) -> Optional[str]:
        return random.choice(self.proxy_pool) if self.use_proxy and self.proxy_pool else None

    async def _request(self, method: str, url: str) -> str:
        if not self.session: 
            self.logger.exception("Сессия не была установлена!")
            raise ValueError()
        
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - self._last_request_time
        
        if elapsed < random.uniform(*self.delay_range):
            delay = random.uniform(*self.delay_range) - elapsed
            await asyncio.sleep(max(0, delay))
        
        proxy = await self._get_proxy()
        for attempt in range(self.retries):
            try:
                async with self._session.request(
                    method, url, proxy=proxy, allow_redirects=True
                ) as response:
                    response.raise_for_status()
                    self._last_request_time = asyncio.get_event_loop().time()
                    return await response.text()
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.backoff_factor * (2 ** attempt))
                    continue
                self.logger.critical(f"Ответ не был получен спустя {self.retries} попыток обращения к {url}")
                raise ConnectionError(f"Request failed after {self.retries} attempts") from e

    async def get(self, url: str) -> str:
        self.logger.info(f"Обращение к url {url}")
        response = await self._request("GET", url)
        self.logger.info(f"Успешное получение ответа по GET запросу к {url}")
        return response
    
    async def head(self, url: str) -> None:
        """Выполняет HEAD-запрос для проверки доступности"""
        self.logger.info(f"HEAD запрос к {url}")
        response = await self._request("HEAD", url)
        self.logger.info(f"Успешный HEAD для {url}")
        return response
