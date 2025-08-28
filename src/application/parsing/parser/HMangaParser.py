import logging
import re
from typing import Any, Dict
from bs4 import BeautifulSoup

from application.parsing.exceptions import InvalidHTMLPage, ParsingException
from application.parsing.parser.Parser import Parser
from domain.enums import PageType

class HMangaParser(Parser):        
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def parse_collection_page(self, html_content: str) -> list[dict[str, Any]]:
        """
        Метод парсит информацию о манге с переданной в качестве параметра страницы.
        
        Параметры:
        - html_content: str: парсируемая HTML страница
        
        Возвращается list[dict[str, Any]]
        - title: str: название манги
        - url: str: ссылка на мангу
        - series: tuple[str, str]: название серии и ссылка на неё
        - authors: list[tuple[str, str]]: список авторов и их ссылок
        - tags: list[str]: список тегов
        - description: str: описание манги
        """
        self.logger.info(f"Начало парсинга HTML страницы коллекции манги")
        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find('div', id='content')
        
        if not content:
            raise InvalidHTMLPage() 
            
        manga_list = []
        for row in content.find_all('div', class_='content_row'):
            try:
                # Название и ссылка
                title_link = row.find('h2').find('a', class_='title_link')
                title = title_link.get_text(strip=True)
                url = title_link['href']
                
                # Серия
                series_div = row.find('div', class_='manga_row2')
                series_div_h3 =  series_div.find('h3')
                series = {'name': series_div_h3.get_text(strip=True), 'url':series_div_h3.find("a").get("href")} if series_div.find('h3') else None
                
                # Переводчики
                translators_a_tags = series_div.find("div", class_="row3_right").find_all("a")
                translators = []
                for tag_a in translators_a_tags:
                    if tag_a.text:
                        translators.append({'name': tag_a.text, 'url': tag_a.get("href")})
                
                # Авторы
                authors_div = row.find('div', class_='manga_row3').find('div', class_='row3_left')
                authors = [{'name':a.get_text(strip=True), 'url':a.get("href")} for a in authors_div.find_all('a')] if authors_div else []
                authors = [author for author in authors if author['name']]
                
                # Теги
                tags_div = row.find('div', class_='item4')
                tags = [{'name': tag.get_text(strip=True)} for tag in tags_div.find_all('a')] if tags_div else []
                
                # Описание
                tags_block = row.find('div', class_='tags')
                description = ''
                if tags_block:
                    b_tag = tags_block.find('b', string='Описание')
                    if b_tag:
                        description = b_tag.next_sibling.strip()
                                                    
                chapter_number = 1          
                manga_list.append({
                    'title': title,
                    'type': 'Hentai',                    
                    'page_url': url,
                    'authors': authors,
                    'tags': tags,
                    
                    'translators': translators,                                        
                    'series': series,
                    'description': description,
                    'chapter_number': chapter_number
                })
            except AttributeError as ex:
                self.logger.warning(f"Во время парсинга карточки манги была обнаружена ошибка, пропуск записи")
                continue
        self.logger.info(f"Было спаршено со страницы {len(manga_list)} записей")
        return manga_list
    
    def parse_manga_page(self, html_content: str) -> str:
        """
        Метод парсит со страницы манги ссылку на страницу со ссылками на загрузку манги
        
        Параметры:
        - html_content: str: парсируемая HTML страница
        
        Возвращается str
        - download_page_url: str: ссылка на страницу со ссылками на загрузки манги
        """
        self.logger.info(f"Начало поиска на страницы манги ссылки на страницу с загрузками")
        soup = BeautifulSoup(html_content, 'html.parser')      
        try:
            download_page_url = soup.find("div", class_="extaraNavi").find_all("p", class_="extra_off")[1].find("a").get("href")
            self.logger.info(f"Была обнаружена ссылка на страницу {download_page_url}")
            return download_page_url
        except Exception as ex:
            self.logger.warning(f"Ошибка парсинга страницы карточки манги")
            raise ParsingException(page_type=PageType.page, fields=['download_page_url'])
    
    def parse_download_page(self, html_content: str) -> Dict[str, Any]:
        """
        Парсит страницу загрузок (таблица с id='download_table') и возвращает:
        {
            'files': [
                {
                    'file_name': str, 
                    'url': str, 
                    'chapter': Optional[float], 
                    'volume': Optional[int],
                    'part': Optional[int],
                    'segment_type': str  # 'chapter', 'volume', 'part' или 'unknown'
                }
            ]
        }
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        files = []
        
        # Находим таблицу загрузок
        table = soup.find('table', id='download_table')
        if not table:
            return files
        
        # Регулярные выражения для поиска разных типов сегментов
        chapter_re = re.compile(r'(Глава|Chapter|Ch\.?|Гл\.?|Часть|Part|Pt\.?)\s*([\d.]+)', re.IGNORECASE)
        volume_re = re.compile(r'(Том|Volume|Vol\.?|Т\.?)\s*(\d+)', re.IGNORECASE)
        part_re = re.compile(r'(Часть|Part|Pt\.?)\s*(\d+)', re.IGNORECASE)
        
        # Обрабатываем все строки таблицы, кроме заголовка
        rows = table.find_all('tr')[1:]  # Пропускаем заголовок
        for i, row in enumerate(rows, start=1):
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
                
            # Второй столбец содержит информацию о файле
            file_col = cols[1]
            file_text = file_col.get_text(strip=True)
            
            # Извлекаем ссылку для скачивания
            file_link = file_col.find('a')
            if not file_link or not file_link.get('href'):
                continue
                
            # Извлекаем имя файла из текста ссылки
            file_name = file_link.get_text(strip=True)
            url = file_link['href']
            
            # Пытаемся определить тип и номер сегмента
            chapter = None
            
            # По умолчанию для первого файла
            default_chapter = 1.0 if len(rows) == 1 else None
            
            # Пробуем найти главу
            match = chapter_re.search(file_text)
            if match:
                num_str = match.group(2)
                try:
                    chapter = float(num_str) if '.' in num_str else int(num_str)
                except (ValueError, TypeError):
                    chapter = default_chapter
            else:
                # Пробуем найти том
                match = volume_re.search(file_text)
                if match:
                    segment_type = "volume"
                    try:
                        volume = int(match.group(2))
                    except (ValueError, TypeError):
                        volume = default_chapter
                else:
                    # Пробуем найти часть
                    match = part_re.search(file_text)
                    if match:
                        segment_type = "part"
                        try:
                            part = int(match.group(2))
                        except (ValueError, TypeError):
                            part = default_chapter
                    else:
                        # Если ничего не найдено и это единственный файл
                        if len(rows) == 1:
                            segment_type = "chapter"
                            chapter = 1.0
            
            files.append({
                'file_name': file_name,
                'url': url,
                'chapter': chapter,
            })
            self.logger.info(f"Найдено 'file_name': {file_name}, 'url': {url}, 'chapter': {chapter}")    
        self.logger.info(f"Найдено {len(files)} файла(ов) для скачивания")
        return files