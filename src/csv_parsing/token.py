from enum import Enum


class CsvTokenType(Enum):
    COMMA = 0
    NEWLINE = 1
    VALUE = 2
    END_OF_FILE = 3


class CsvToken:
    def __init__(self, type: CsvTokenType, line_num: int, char_index: int) -> None:
        self.type = type
        self.line_num = line_num
        self.char_index = char_index

    def __repr__(self) -> str:
        return f"Node: {self.type}"


class CsvValueToken(CsvToken):
    def __init__(self, value: str, line_num: int, char_index: int) -> None:
        super().__init__(CsvTokenType.VALUE, line_num, char_index)
        self.value = value

    def __repr__(self) -> str:
        return f"Value Node: {self.value}"
