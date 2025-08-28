from datetime import datetime
import logging
from typing import Annotated, Optional

from application.parsing.exceptions import NoOneAvailableDomen
from application.services.ComixService import ComixService

class ComixParsingController:
    def __init__(
        self,
        comix_service: ComixService
    ):
        self._comix_service = comix_service
        self.logger = logging.getLogger(self.__class__.__name__)
      
    async def parse(
        self,
        source: Annotated[Optional[int], "Источник манги для парсинга"]=0,
        start_page: Annotated[Optional[int], "Номер стартовой страницы"]=0,
        end_page: Annotated[Optional[int], "Номер конечной страницы"]=None,
        start_date: Annotated[Optional[datetime], "Начало периода дат загрузки"]=None,
        end_date: Annotated[Optional[datetime], "Конец периода дат загрузки"]=None,
        author_names: Annotated[Optional[list[str]], "Авторы манги"]=[],
        translator_names: Annotated[Optional[list[str]], "Переводчики манги"]=[],
        uploader_names: Annotated[Optional[list[str]], "Загрузчики манги"]=[],
        include_tags: Annotated[Optional[list[str]], "Обязательные теги"]=[],
        except_tags: Annotated[Optional[list[str]], "Исключить мангу с тегами"]=[],
    ) -> dict:
        """
        Скачивание манги с указанными фильтрами и параметрами
        
        Параметры:
        - source: Optional[list[int]: Источник манги для парсинга, default=[0]
        - start_page: Optional[int]: Номер стартовой страницы , default=0,
        - end_page: Optional[int]: Номер конечной страницы, default=None,
        - start_date: Optional[datetime]: Начало периода, default=None,
        - end_date: Optional[datetime]: Конец периода, default=None,
        - author_names: Optional[list[str]]: Авторы манги, default=[],
        - translator_names: Optional[list[str]]: Переводчики манги, default=[],
        - uploader_names: Optional[list[str]]: Загрузчики манги, default=[],
        - include_tags: Optional[list[str]]: Обязательные теги, default=[],
        - except_tags: Optional[list[str]]: Исключить мангу с тегами, default=[],
        """
        self.logger.info(f"Инициализация процесса парсинга с заданными параметрами")
        try:
            result = await self._comix_service.parse(
                source = source,
                start_page = int(start_page),
                end_page = int(end_page),
                start_date = start_date,
                end_date = end_date,
                author_names = author_names,
                translator_names = translator_names,
                uploader_names = uploader_names,
                include_tags = include_tags,
                except_tags = except_tags,
            )
            
            self.logger.info(f"Завершение процесса парсинга с заданными параметрами")
            return result
        except NoOneAvailableDomen:
            self.logger.critical("Парсинг был досрочно завершён из-за отсутствия доступных доменов", exc_info=False)
        except Exception as ex:
            self.logger.critical(f"Парсинг был досрочно завершён из-за ошибки", exc_info=False)