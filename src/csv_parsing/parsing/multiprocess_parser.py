from collections.abc import Generator, Iterable
from typing import TextIO
from itertools import batched
import concurrent.futures as fut
from csv_parsing.bad_line_mode import BadLineMode
from csv_parsing.parsing.csv_header import CsvHeader
from .base_parser import BaseCsvParser, CsvRow
from .parser import CsvParser


class RowChunk:
    def __init__(self) -> None:
        self._rows = []

    def push_row(self, row: CsvRow):
        self._rows.append(row)

    def stream_rows(self) -> Generator[CsvRow]:
        for value in self._rows:
            yield value


class MultiProcessCsvParser(BaseCsvParser):
    def __init__(
        self,
        lines: TextIO | Iterable[str],
        bad_line_mode,
        print_error_to,
        allow_multiline_strings=False,
        chunk_size=20000,
    ):
        self._lines = lines
        self._bad_line_mode = bad_line_mode
        self._print_error_to = print_error_to
        self._allow_multiline_strings = allow_multiline_strings
        self._chunk_size = chunk_size

    @staticmethod
    def _parse_chunk(
        header: CsvHeader,
        bad_line_mode: BadLineMode,
        print_error_to,
        allow_multiline_strings: bool,
        chunk_lines: tuple[str],
    ) -> RowChunk:
        # We have to wrap it in an iter, otherwise next() wont work
        line_iter = iter(chunk_lines)
        parser: CsvParser = CsvParser.from_header(
            header,
            line_iter,
            bad_line_mode,
            print_error_to,
            allow_multiline_strings,
        )

        chunk = RowChunk()
        for value in parser.parse():
            chunk.push_row(value)
        return chunk

    def _parse_chunks(self) -> Generator[RowChunk]:
        chunks = batched(self._lines, self._chunk_size)
        with fut.ProcessPoolExecutor() as pool:
            futures: list[fut.Future] = []
            for chunk in chunks:
                future = pool.submit(
                    MultiProcessCsvParser._parse_chunk,
                    self._header,
                    self._bad_line_mode,
                    self._print_error_to,
                    self._allow_multiline_strings,
                    chunk,
                )
                futures.append(future)
            for future in futures:
                if future.done():
                    yield future.result()

    # NOTE: For the vast majority of cases the normal CsvParser is better suited
    def parse(self) -> Generator[CsvRow]:
        # This is a little hacky, but we construct the first parser here,
        # then since the constructor parses the header, we get the header
        # afterwards for usage in the chunked parsers
        header_line = next(self._lines)
        header_parser = CsvParser(
            iter([header_line]), self._bad_line_mode, self._print_error_to
        )
        self._header = header_parser._header

        # Yield the result of the first parser
        for chunk in self._parse_chunks():
            for row in chunk.stream_rows():
                yield row
