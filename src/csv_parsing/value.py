from .lexing.token import CsvValueToken


class CsvValue:
    def __init__(self, column_type: str, token: CsvValueToken) -> None:
        self._column_type = column_type
        self._token = token

    def get_column_type(self) -> str:
        return self._column_type

    def get_value(self) -> str:
        return self._token.value

    def debug_get_token(self) -> CsvValueToken:
        return self._token

    def __repr__(self) -> str:
        return f"[{self._column_type} = {self.get_value()}]"
