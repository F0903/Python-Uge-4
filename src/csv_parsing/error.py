from .token import CsvToken


class CsvError(Exception):
    def __init__(self, message: str, token: CsvToken) -> None:
        super().__init__()
        self.message = message
        self.token = token

    def __repr__(self) -> str:
        return self.get_printable_message()

    def get_printable_message(self) -> str:
        return f"{self.message}\n\tat line {self.token.line_num}, column {self.token.char_index}"
