import enum

class PageType(enum.Enum):
    collection_page = "Страница с коллекцией карточек"
    page = "Страница манги"
    download_page = "Страница со сслыками на загрузку"
    
class WorkType(enum.Enum):
    comix = "Comix"
    manga = "Manga"
    hentai = "Hentai"
    manhwa = "Manhwa"
    manhua = "Manhua"
    rumanga = "Rumanga"
    
translate = {
    'Комикс': "Comix",
    'Манга': "Manga",
    'ХентайМанга': "Hentai",
    'Манхва': "Manhwa",
    'Маньхуа': "Manhua",
    'Руманга': "Rumanga"
}   
    
    
def parse_work_type(type_value: str):
    if type_value in translate:
        return translate[type_value]
    return None