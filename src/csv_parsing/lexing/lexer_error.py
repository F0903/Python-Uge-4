from typing import override
from ..error import CsvError


class CsvLexerError(CsvError):
    def __init__(self, message: str, position: int) -> None:
        self._position = position
        super().__init__(message)

    @override
    def get_printable_message(self) -> str:
        return f"{self.message}\n\tat position {self._position}"
