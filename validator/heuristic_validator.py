import re

class Validator:
    def __init__(self):
        pass

    @staticmethod
    def detect_injection(text: str) -> bool:
        """
        Проверяет, содержит ли текст признаки промпт-инъекции.
        Возвращает True, если инъекция обнаружена.
        """
        for pattern in COMPILED_PATTERNS:
            if pattern.search(text):
                return True
        return False

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
