import os

from API.ini import Initializator as ApiInitializator
from application.ini import Initializator as AppInitializator
from domain.config.Config import Config
from persistance.ini import Initializator as DbInitializator

class Initializator:
    def __init__(self):
        config = Config(os.path.abspath("src\persistance\conf\ini.conf"))
        self._per_ini = DbInitializator(config=config) 
        self._app_ini = AppInitializator(config=config)
        self._api_ini = ApiInitializator()       
           
    async def initialize(self):
        unit_of_work = await self._per_ini.initialize("src\persistance\db\comics.db")
        comix_service = self._app_ini.initialize(unit_of_work)
        arg_parser = self._api_ini.initialize(comix_service=comix_service)
        return arg_parser