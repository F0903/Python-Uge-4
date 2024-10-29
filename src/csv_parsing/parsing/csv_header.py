class CsvHeader:
    def __init__(self, column_decls: list[str]) -> None:
        self.column_decls = column_decls

    def lookup_column_type(self, comma_index: int) -> str:
        return self.column_decls[comma_index]

    def get_column_count(self) -> int:
        return len(self.column_decls)
