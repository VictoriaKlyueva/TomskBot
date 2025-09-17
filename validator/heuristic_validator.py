import re

from validator.constants import *


class HeuristicValidator:
    def __init__(self):
        pass

    @staticmethod
    def detect_injection(text: str) -> (bool, str):
        """
        Проверяет, содержит ли текст признаки промпт-инъекции.
        Возвращает пару: True и паттерн, если инъекция обнаружена, иначе False и None.
        """
        for pattern in COMPILED_PATTERNS:
            if pattern.search(text):
                return True, pattern.pattern
        return False, None

    @staticmethod
    def get_detected_pattern(text: str) -> str:
        """
        Возвращает первый найденный шаблон, который сработал.
        Для логирования и отладки.
        """
        for pattern in COMPILED_PATTERNS:
            if pattern.search(text):
                return pattern.pattern
        return ""
