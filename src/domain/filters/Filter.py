from typing import Callable, Dict, Any

class CFilter:
    def __init__(self, condition: Callable[[Dict[str, Any]], bool], name="Unnamed filter"):
        """
        :param condition: Лямбда-функция, принимающая комикс и возвращающая bool
        """
        self._condition = condition
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    def apply(self, comix_info: Dict[str, Any]) -> bool:  
        """Проверяет, удовлетворяет ли комикс условию фильтра"""
        try:
            return self._condition(comix_info)
        except KeyError as e:
            return False
        except Exception as e:
            return False
    
    def __and__(self, other: 'CFilter') -> 'CFilter':
        """Комбинирует фильтры через логическое И"""
        return CFilter(lambda c: self.apply(c) and other.apply(c))
    
    def __or__(self, other: 'CFilter') -> 'CFilter':
        """Комбинирует фильтры через логическое ИЛИ"""
        return CFilter(lambda c: self.apply(c) or other.apply(c))
    
    def __invert__(self) -> 'CFilter':
        """Инвертирует фильтр"""
        return CFilter(lambda c: not self.apply(c))