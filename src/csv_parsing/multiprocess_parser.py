from collections.abc import Iterable
from typing import override, TextIO
from csv_parsing.parser import CsvParser, CsvRow
from itertools import batched, starmap, chain, islice
import multiprocessing as mp
import os
import math


class MultiProcessParser(CsvParser):
    def __init__(
        self,
        lines: TextIO | Iterable[str],
        bad_line_mode,
        print_error_to,
        allow_multiline_strings=False,
    ):
        self._lines = lines

        self._bad_line_mode = bad_line_mode
        self._print_error_to = print_error_to
        self._allow_multiline_strings = allow_multiline_strings

    def _parse_chunk(self, chunk: Iterable[str]) -> Iterable[CsvRow]:
        parser: CsvParser = CsvParser.from_header(
            self._header,
            chunk,
            self._bad_line_mode,
            self._print_error_to,
            self._allow_multiline_strings,
        )
        return parser.parse()

    def _parse_chunks(self) -> Iterable[CsvRow]:
        self._last_index = 0
        cpus = os.cpu_count()
        with mp.Pool(cpus) as pool:
            current_index = self._last_index
            self._last_index += 10000
            # TODO
            chunk_lines = islice(current_index, current_index + 10000)
            for val in pool.starmap(self._parse_chunk, self._lines):
                yield val

    def parse(self):
        # This is a little hacky, but we construct the first parser here,
        # then since the constructor parses the header, we get the header
        # afterwards for usage in the chunked parsers
        first_line = next(self._lines)
        first_parser = CsvParser(
            iter([first_line]), self._bad_line_mode, self._print_error_to
        )
        self._header = first_parser._header

        # Yield the result of the first parser
        for val in chain(first_parser.parse(), self._parse_chunks()):
            yield val
