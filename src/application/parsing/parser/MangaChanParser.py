import re
import logging

from bs4 import BeautifulSoup
from typing import Any, List, Dict, Optional

from application.parsing.exceptions import InvalidHTMLPage, ParsingException
from application.parsing.parser.Parser import Parser
from domain.enums import PageType

CHAPTER_RE = re.compile(r'ch(\d+(?:\.\d+)?)', flags=re.IGNORECASE)

class MangaChanParser(Parser):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_collection_page(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Парсит страницу каталога и возвращает список карточек манги.

        Возвращаемая структура (каждая запись):
        {
            'title': str,
            'type': Optional[str],
            'authors': List[{'name': str, 'url': Optional[str]}],
            'tags': List[str],
            'page_url': str
        }
        """
        self.logger.info("Начало парсинга страницы каталога манги")
        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find(id='content')
        if not content:
            raise InvalidHTMLPage()

        result: List[Dict[str, Any]] = []

        # Каждая карточка — div.content_row (как в присланном файле). :contentReference[oaicite:3]{index=3}
        for row in content.find_all('div', class_='content_row'):
            try:
                # Title + page url
                h2 = row.find('h2')
                if not h2:
                    continue
                a = h2.find('a', class_='title_link') or h2.find('a')
                if not a:
                    continue
                title = a.get_text(strip=True)
                page_url = a.get('href', '').strip()

                # Тип (в блоке manga_row1 есть ссылка на /type/...)
                type_tag = row.select_one('.manga_row1 a[href^="/type/"]')
                mtype = type_tag.get_text(strip=True) if type_tag else None

                # Авторы — в .manga_row2 .row3_left a
                authors: List[Dict[str, Optional[str]]] = []
                authors_container = row.select_one('.manga_row2 .row3_left')
                if authors_container:
                    for aa in authors_container.find_all('a'):
                        name = aa.get_text(strip=True)
                        href = aa.get('href')
                        if name:
                            authors.append({'name': name, 'url': href})

                # Теги — обычно в блоке .item4 .genre (список ссылок)
                tags: List[str] = []
                tags_container = row.select_one('.manga_row3 .item4') or row.select_one('.genre')
                if tags_container:
                    for t in tags_container.find_all('a'):
                        txt = t.get_text(strip=True)
                        if txt:
                            tags.append({'name': txt})

                result.append({
                    'title': title,
                    'type': mtype,
                    'authors': authors,
                    'tags': tags,
                    'page_url': page_url
                })
            except Exception as exc:
                self.logger.warning(f"Ошибка при парсинге карточки: {exc}. Пропускаю запись.")
                continue

        self.logger.info(f"Спаршено карточек: {len(result)}")
        return result

    def parse_manga_page(self, html_content: str) -> str:
        """
        Возвращает URL страницы загрузок или поднимает ParsingException.
        """
        self.logger.info("Поиск ссылки на страницу 'Скачать' в карточке манги")
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            nav = soup.find("div", class_="extaraNavi")
            if not nav:
                raise ValueError("content not found")

            link_p = None
            for p in nav.find_all('p'):
                if 'Скачать' in p.get_text():
                    link_p = p
                    break
            if not link_p:
                raise ValueError("Download link paragraph not found")

            a = link_p.find('a')
            if a and a.get('href'):
                return a.get('href').strip()
            raise ValueError("href for download page not found")
        except Exception as exc:
            self.logger.warning(f"Не удалось найти ссылку на страницу скачивания: {exc}")
            raise ParsingException(page_type=PageType.page, fields=['download_page_url'])

    def parse_download_page(self, html_content: str) -> Dict[str, Any]:
        """
        Парсит страницу загрузок (таблица с id='download_table') и возвращает:
        {
            'files': [
                {'file_name': str, 'url': str, 'chapter': Optional[float_or_str]}
            ]
        }
        """
        self.logger.info("Парсинг страницы загрузок")
        soup = BeautifulSoup(html_content, 'html.parser')

        table = soup.find(id='download_table')
        if not table:
            self.logger.warning("download_table не найден")
            raise ParsingException(page_type=PageType.page)

        files: List[Dict[str, Any]] = []
        rows = table.find_all('tr')
        for row in rows[1:]:
            link_cell = row.find('td', attrs={'width': True}) or row.find('td')
            if not link_cell:
                continue
            a = link_cell.find('a')
            if not a:
                continue
            file_name = a.get_text(strip=True)
            url = a.get('href', '').strip()
            chapter = None
            m = CHAPTER_RE.search(file_name)
            if m:
                chapter_str = m.group(1)
                try:
                    if '.' in chapter_str:
                        chapter = float(chapter_str)
                    else:
                        chapter = int(chapter_str)
                except Exception:
                    chapter = chapter_str
            files.append({'file_name': file_name, 'url': url, 'chapter': chapter})
            self.logger.info(f"Найдено 'file_name': {file_name}, 'url': {url}, 'chapter': {chapter}")    
        self.logger.info(f"Найдено {len(files)} файла(ов) для скачивания")
        return files
