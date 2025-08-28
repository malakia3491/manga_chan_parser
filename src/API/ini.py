from API.argparsing.ArgParser import ArgParser
from API.controllers.ComixParsingController import ComixParsingController
from application.services.ComixService import ComixService

class Initializator:
    def initialize(
        self,
        comix_service: ComixService
    ) -> ArgParser:
        parsing_controller = ComixParsingController(comix_service=comix_service)
        arg_parser = ArgParser(controller=parsing_controller)
        return arg_parser