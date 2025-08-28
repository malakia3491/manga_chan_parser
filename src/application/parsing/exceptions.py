
class InvalidHTMLPage(BaseException):
    def __init__(self, message="Given page is not correct"):
        super().__init__(message)
        self.msgfmt = message

class ParsingException(BaseException):
    def __init__(
        self,
        page_type: str,
        fields: list[str]=[],
    ):
        self.page_type = page_type
        if fields:
            field_str = ""
            for i, field in enumerate(fields):
                if i != len(fields) - 1:
                    field_str += field + '\n'
                else: field_str += field
                
            message = f"На странице {page_type} не были спаршены поля: \n {fields}"
        else:
            message = f"Страница типа {page_type} не была спаршена"
        super().__init__(message)
        self.msgfmt = message
        
        
class NoOneAvailableDomen(BaseException):
    def __init__(self, message="Нет доступных доменов указанного ресурса!"):
        super().__init__(message)
        self.msgfmt = message