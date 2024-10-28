from .value import CsvValue


class CsvRow:
    def __init__(self, values: list[CsvValue]) -> None:
        self.values = values

    def get_all_values(self) -> list[CsvValue]:
        return self.values

    def get_value(self, column_type: str) -> CsvValue:
        for value in self.values:
            if value._column_type != column_type:
                continue
            return value

    def __repr__(self) -> str:
        str_buf = ""
        for value in self.values:
            str_buf += f"{value}"
        return str_buf
