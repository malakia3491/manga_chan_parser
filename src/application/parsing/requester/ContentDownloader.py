import logging
import os
import mimetypes
import aiohttp
import aiofiles
import asyncio
from pathlib import Path
from tqdm.asyncio import tqdm

class ContentDownloader:
    def __init__(
        self,
        destination_path: Path = None,
        max_retries: int = 5,
        retry_delay: float = 10.0
    ):
        self._destination_path = destination_path
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @property
    def destination(self) -> Path:
        return self._destination_path
    
    @destination.setter
    def destination(self, value: Path):
        self._destination_path = value

    @property
    def session(self):
        return self._session

    @session.setter    
    def session(self, session: aiohttp.ClientSession):
        self._session = session
              
    async def download(
        self, 
        url: str, 
        filename: str,
    ) -> str:
        """Скачивает файл с опциональной ручной обработкой редиректов"""
        self.logger.info(f"Скачивается контент {filename} по адресу {url}")
        return await self._download_with_redirects(url, filename)

    async def _download_with_redirects(self, url: str, filename: str) -> str:
        """Скачивание с ручной обработкой редиректов"""
        async with self._session.get(url, allow_redirects=False) as first_response:
            if first_response.status != 302:
                self.logger.info(f"Статус код ответа {first_response.status}. Редиректа не было")
                self.logger.info(f"Выполняется прямая загрузка")
                return await self._download_direct(url, filename)
            else:
                redirect_url = first_response.headers.get('Location')
                if not redirect_url:
                    raise RuntimeError("Redirect location missing")
                
                self.logger.info(f"Редирект на: {redirect_url}")

                return await self._download_direct(redirect_url, filename)
    
    async def _download_direct(self, url: str, filename: str) -> str:
        """Прямое скачивание без обработки редиректов"""
        self.logger.info(f"🚀 Начало загрузки: {filename} по url {url}")
        self.destination.mkdir(parents=True, exist_ok=True)
        base_path = self.destination / filename
        
        for attempt in range(self.max_retries + 1):
            try:
                async with self._session.get(url) as response:
                    response.raise_for_status()
                
                    extension = self._get_file_extension(response)
                    file_path = base_path.with_suffix(extension)
                    total_size = int(response.headers.get('Content-Length', 0))
                    
                    progress_bar = tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=f"{filename[:20]:<20}",
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
                    )
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            progress_bar.update(len(chunk))
                    
                    progress_bar.close()
                    
                    if total_size > 0 and file_path.stat().st_size != total_size:
                        raise RuntimeError(f"Неполная загрузка: {file_path.stat().st_size}/{total_size} байт")
                    
                    self.logger.info(f"✅ Успешно загружено: {filename}")
                    return str(file_path)
            
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(
                        f"⚠️ Ошибка загрузки (попытка {attempt+1}/{self.max_retries}): "
                        f"{type(e).__name__} - {str(e)}"
                    )
                    self.logger.info(f"⏳ Повторная попытка через {wait_time:.1f} сек...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"🔥 Все попытки провалились для {filename}")
                    self.logger.error(f"❌ Ошибка: {type(e).__name__} - {str(e)}", exc_info=False)
                    raise

    def _get_file_extension(self, response: aiohttp.ClientResponse) -> str:
        """Определяет расширение файла на основе заголовков ответа"""
        content_type = response.headers.get('Content-Type', '').split(';')[0].strip()
        if content_type:
            extension = mimetypes.guess_extension(content_type)
            if extension:
                return extension       
        url_path = response.url.path
        if '.' in url_path:
            _, ext = os.path.splitext(url_path)
            if ext:
                return ext
        return '.rar'