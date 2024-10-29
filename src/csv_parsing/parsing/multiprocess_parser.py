from collections.abc import Generator, Iterable
from typing import TextIO
from itertools import batched
import multiprocess as mp
import os
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
        chunk_size=2000,
    ):
        self._lines = lines
        self._bad_line_mode = bad_line_mode
        self._print_error_to = print_error_to
        self._allow_multiline_strings = allow_multiline_strings
        self._chunk_size = chunk_size

    def _parse_chunk(self, chunk_lines: tuple[str]) -> RowChunk:
        # We have to wrap it in an iter, otherwise next() wont work
        line_iter = iter(chunk_lines)
        parser: CsvParser = CsvParser.from_header(
            self._header,
            line_iter,
            self._bad_line_mode,
            self._print_error_to,
            self._allow_multiline_strings,
        )

        chunk = RowChunk()
        for value in parser.parse():
            chunk.push_row(value)
        return chunk

    def _parse_chunks(self) -> Generator[RowChunk]:
        cpus = os.cpu_count()
        chunks = batched(self._lines, self._chunk_size)

        with mp.Pool(cpus) as pool:
            for val in pool.map(self._parse_chunk, chunks):
                yield val

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
