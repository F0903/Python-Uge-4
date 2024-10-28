class CsvError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.get_printable_message())

    def __repr__(self) -> str:
        return self.get_printable_message()

    def get_printable_message(self) -> str:
        return f"{self.message}"
