import os
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from application.parsing.ComixBee import ComixBee
from application.parsing.exceptions import NoOneAvailableDomen, ParsingException
from application.parsing.requester.ContentDownloader import ContentDownloader
from domain.entities.Chapter import Chapter
from domain.entities.ParsingSession import ParsingSession
from domain.entities.Work import Work
from domain.filters.CFilterBuilder import CFilterBuilder
from persistance.Application import UnitOfWork

class ComixService:
    """
    Сервис парсинга и сохранения комиксов/манги.
    Разделяет логику: подготовка фильтра -> обход страниц -> проверка наличия в БД -> докачка контента -> сохранение новых работ.
    """
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        cfilter_builder: CFilterBuilder
    ):
        self._unit_of_work = unit_of_work
        self._cfilter_builder = cfilter_builder
        self.logger = logging.getLogger(self.__class__.__name__)

    async def parse(
        self,
        source: Optional[int] = 0,
        start_page: Optional[int] = 0,
        end_page: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        author_names: Optional[List[str]] = None,
        translator_names: Optional[List[str]] = None,
        uploader_names: Optional[List[str]] = None,
        include_tags: Optional[List[str]] = None,
        except_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Основной метод запуска парсинга.

        Возвращает словарь с краткой статистикой по результату.
        """
        author_names = author_names or []
        translator_names = translator_names or []
        uploader_names = uploader_names or []
        include_tags = include_tags or []
        except_tags = except_tags or []

        self.logger.info("Старт парсинга источника %s", source)

        filter_pipeline = self._cfilter_builder.build(
            start_date=start_date,
            end_date=end_date,
            author_names=author_names,
            translator_names=translator_names,
            uploader_names=uploader_names,
            include_tags=include_tags,
            except_tags=except_tags,
        )

        async with self._unit_of_work:
            parsing_source = await self._unit_of_work.sources.get(source)
            comix_bee = parsing_source.build_comix_bee()

            parsing_session = ParsingSession(parsing_source.id)
            self._unit_of_work.parsing_sessions.add(parsing_session)

            total_saved = 0
            total_processed = 0

            try:
                async for parsed_cards_from_collection_page in comix_bee.parse(
                    start_page=start_page,
                    end_page=end_page,
                    filter_pipeline=filter_pipeline
                ):
                    total_processed += len(parsed_cards_from_collection_page)
                    cards_to_download_content = await self._filter_existing_and_missing_content(parsed_cards_from_collection_page)

                    if not cards_to_download_content:
                        self.logger.info("Нет новых карточек для обработки на этой странице.")
                        continue

                    saved_count = await self._process_and_save_cards(cards_to_download_content, parsing_session, comix_bee)
                    total_saved += saved_count

                    await self._unit_of_work.commit()

            except ParsingException as ex:
                self.logger.warning("Произошла ошибка парсинга страницы типа '%s'.", ex.page_type, exc_info=False)
            except NoOneAvailableDomen:
                self.logger.critical("Нет доступных доменов указанного ресурса!", exc_info=False)
                raise
            except Exception as ex:
                self.logger.critical("Критическая ошибка во время парсинга: %s", ex, exc_info=False)
                raise
            finally:
                try:
                    await self._unit_of_work.commit()
                    await comix_bee._request_director.close()
                    self.logger.info(
                        "Парсинг завершён. Обработано карточек: %s, сохранено новых записей: %s, источник: %s",
                        total_processed, total_saved, parsing_source.name
                    )
                except Exception:
                    self.logger.exception("Ошибка при финальном коммите.", exc_info=False)

            return {
                "processed_cards": total_processed,
                "saved_works": total_saved,
                "source": parsing_source.name
            }

    async def _filter_existing_and_missing_content(self, parsed_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Для каждой карточки проверяет есть ли запись в БД.
        Если запись есть — проверяет, что все главы имеют content_path. Если какого-то контента нет — пытается докачать из download_url.
        Если докачка неуспешна — карточка добавляется в список для повторной полной обработки (парсинга карточки).
        Возвращает список карточек, которые нужно полностью парсить (cards_to_download_content).
        """
        cards_to_download_content: List[Dict[str, Any]] = []

        for card in parsed_cards:
            try:
                title = card.get('title')
                if not title:
                    self.logger.warning("Пропущена карточка без title: %s", card)
                    continue

                comix_in_db = await self._unit_of_work.comics.get_by_field('title', title)
                if not comix_in_db:
                    cards_to_download_content.append(card)
                    continue

                need_full_parse = False
                for chapter in comix_in_db.chapters:
                    if not chapter.content_path or not os.path.exists(chapter.content_path):
                        if not chapter.download_url:
                            self.logger.warning("У %s отсутствует content_path и download_url для главы %s. Помечаю карточку на повторную обработку.", title, getattr(chapter, 'number', '?'))
                            need_full_parse = True
                            self.logger.warning("Помеячаю карточку на повторную обработку")
                            break
                if need_full_parse:
                    cards_to_download_content.append(card)
                else:
                    self.logger.info("Карточка '%s' уже сохранена и все файлы в порядке.", title)

            except Exception:
                self.logger.exception("Ошибка при проверке существующей карточки: %s", card['title'], exc_info=False)
                cards_to_download_content.append(card)
        return cards_to_download_content

    async def _process_and_save_cards(self, cards: List[Dict[str, Any]], parsing_session: ParsingSession, comix_bee: ComixBee) -> int:
        """
        Парсит по каждой карточке полную информацию (через comix_bee.parse_card),
        скачивает файлы, создаёт Work и добавляет в UnitOfWork.
        Возвращает количество успешно добавленных Works.
        """
        saved = 0

        try:
            async for parsed_card in comix_bee.parse_card(cards):
                try:
                    parsed_card['parsing_session'] = parsing_session

                    work = await self._create_work_from_parsed_card(parsed_card, parsing_session)
                    self._unit_of_work.comics.add(work)
                    saved += 1
                except Exception:
                    self.logger.exception("Ошибка обработки одной карточки: %s", parsed_card, exc_info=False)
                    continue

        except Exception:
            self.logger.exception("Критическая ошибка при разборе карточек через comix_bee.parse_card", exc_info=False)

        return saved

    async def _create_work_from_parsed_card(self, parsed_card: Dict[str, Any], parsing_session: ParsingSession) -> Work:
        """
        Преобразует parsed_card -> Work, скачивает файлы глав и возвращает инстанс Work (не сохраняет в БД).
        """
        work = Work.from_dict(parsed_card)

        if getattr(work, 'series', None):
            work.series = await self._unit_of_work.series.get_by_field_or_create('name', work.series)
        if getattr(work, 'authors', None):
            work.authors = [await self._unit_of_work.authors.get_by_field_or_create('name', author) for author in work.authors]
        if getattr(work, 'tags', None):
            work.tags = [await self._unit_of_work.tags.get_by_field_or_create('name', tag) for tag in work.tags]

        chapters: List[Chapter] = []
        files: list[dict[str, Any]] = parsed_card.get('files', [])
        for file in files:
            chapter = Chapter(
                parsing_session=parsing_session,
                content_path=file['save_path'],
                download_url=file['url'],
                number=file.get('chapter')
            )
            chapters.append(chapter)

        work.chapters = chapters
        return work