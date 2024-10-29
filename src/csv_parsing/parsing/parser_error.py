from typing import override
from ..error import CsvError
from ..lexing.token import CsvToken


class CsvParserError(CsvError):
    def __init__(self, message: str, token: CsvToken) -> None:
        super().__init__(message)
        self.token = token

    @override
    def get_printable_message(self) -> str:
        return f"{self.message}\n\tat line {self.token.line_num}, column {self.token.char_index}"
