from application.parsing.requester.ContentDownloader import ContentDownloader
from application.services.ComixService import ComixService
from domain.config.Config import Config
from domain.filters.CFilterBuilder import CFilterBuilder
from persistance.Application import UnitOfWork

class Initializator:
    def __init__(self, config: Config):
        self._config = config
    
    def initialize(self, unit_ofwork: UnitOfWork):
        cfilter_builder = CFilterBuilder()
        parsing_service = ComixService(
            unit_of_work=unit_ofwork,
            cfilter_builder=cfilter_builder
        )
        return parsing_service