import uuid
import logging
from typing import Annotated, Any, AsyncGenerator, Optional

from application.parsing.exceptions import ParsingException
from application.parsing.parser.Parser import Parser
from application.parsing.requester.RequestDirector import RequestDirector
from application.parsing.requester.UrlBuilders.UrlBuilder import UrlBuilder
from domain.filters.CFilterBuilder import CFilterBuilder
from domain.filters.CFilterPipeline import CFilterPipeline

class ComixBee:
    def __init__(
        self,
        request_director: RequestDirector,
        comix_parser: Parser,
        url_builder: UrlBuilder,       
        cfilter_builder: CFilterBuilder,
    ):
        self._request_director = request_director
        self._comix_parser = comix_parser       
        self._url_builder = url_builder       
        self._cfilter_builder = cfilter_builder
        self.logger = logging.getLogger(self.__class__.__name__)    
        
    async def parse(
        self,
        start_page: Annotated[Optional[int], "Номер стартовой страницы"]=0,
        end_page: Annotated[Optional[int], "Номер конечной страницы"]=None,
        filter_pipeline = CFilterBuilder
    ) -> AsyncGenerator[Any, Any]:
        await self._request_director.initialize()
        self._url_builder.base = self._request_director.base
        for page_number in range(start_page, end_page+1):
            await self._request_director.open()
            try:
                self.logger.info(f"Производится парсинг страницы {page_number}")
                source_url = self._url_builder.get_collection_page_url(page_number) 
                response_content = await self._request_director.get(source_url)
                cards = self._comix_parser.parse_collection_page(response_content)
                self.logger.info(f"Обнаружено карточек манги {len(cards)}")
                filtered_cards = self._filter_manga_list(filter_pipeline, cards)
                self.logger.info(f"Отфильтровано карточек {len(cards) - len(filtered_cards)}")
                self.logger.info(f"Парсинг карточек со страницы страницы {page_number} завершён")
                yield filtered_cards            
            except ParsingException as ex:
                continue
            except Exception as ex:
                await self._request_director.close()
                raise ex
            
    async def parse_card(self, cards: dict[str, Any]) -> AsyncGenerator[Any, Any]:
        for card in cards:
            try:
                response_text = await self._request_director.get(self._url_builder.build_url(card["page_url"]))
                card['download_page_url'] = self._comix_parser.parse_manga_page(response_text)
                response_text = await self._request_director.get(self._url_builder.build_url(card["download_page_url"]))
                files = self._comix_parser.parse_download_page(response_text)
                files = await self._download_card_files(files)
                card['files'] = files                         
                yield card
            except ParsingException as ex:
                raise ex  
                                    
    def _filter_manga_list(
        self,
        filter_pipeline: CFilterPipeline,
        cards: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        mask = filter_pipeline.apply_many(cards)
        return [value for value, mask in zip(cards, mask) if mask]
    
    async def _download_card_files(self, files: list[dict[str, str]]):
        for file in files:
            try:
                file['save_path'] = await self._request_director.download(file['url'], str(uuid.uuid4()))
            except Exception:
                self.logger.warning(f"Ошибка при скачивании файла для ссылки {file['url']}", exc_info=False)
                self.logger.warning("Пропуск загрузки карточки", exc_info=False)
                file['save_path'] = ''
                continue
        return files        