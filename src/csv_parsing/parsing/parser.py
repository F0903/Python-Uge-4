from collections.abc import Iterable, Generator
from typing import Self, cast, TextIO
from ..lexing.token import CsvToken, CsvValueToken, CsvTokenType
from ..error import CsvError
from ..row import CsvRow
from ..value import CsvValue
from ..lexing.lexer import CsvLexer
from ..bad_line_mode import BadLineMode
from .csv_header import CsvHeader
from .parser_error import CsvParserError
from .base_parser import BaseCsvParser


class CsvParser(BaseCsvParser):
    def __init__(
        self,
        lines: TextIO | Iterable[str],
        bad_line_mode: BadLineMode,
        print_error_to: TextIO | None,
        allow_multiline_strings: bool = False,
        parse_header: bool = True,
    ) -> None:
        self._error_state = False
        self._had_error = False

        self._input = CsvLexer(lines, allow_multiline_strings).lex()
        self._bad_line_mode = bad_line_mode
        self._print_to_file = print_error_to

        self._line_num = 0
        self._current_token = None

        self._advance()  # Priming the pump :)
        if parse_header:
            self._parse_header()

    @staticmethod
    def from_header(
        header: CsvHeader,
        lines: TextIO | Iterable[str],
        bad_line_mode: BadLineMode,
        print_error_to: TextIO | None,
        allow_multiline_strings: bool = False,
    ) -> Self:
        new = CsvParser(
            lines,
            bad_line_mode,
            print_error_to,
            allow_multiline_strings,
            parse_header=False,
        )
        # This feels a little hacky, but whatever right ;-----)
        new._header = header
        return new

    def _parse_header(self):
        comma_index = 0
        header_column_decls = []
        while True:
            token = self._get_current_token()
            match token.type:
                case CsvTokenType.NEWLINE:
                    self._advance_line()
                    break  # The 'header' is only the first line, so we are done

                case CsvTokenType.COMMA:
                    comma_index += 1

                case CsvTokenType.VALUE:
                    # At this point we know that 'token' is a CsvValueToken
                    value_token = cast(CsvValueToken, token)
                    header_column_decls.append(value_token.value)

            self._advance()

        self._header = CsvHeader(header_column_decls)

    def _get_current_token(self) -> CsvToken:
        return self._current_token

    def _get_previous_token(self) -> CsvToken:
        return self._previous_token

    def _advance(self):
        self._previous_token = self._current_token
        self._current_token = next(self._input)

    def _advance_line(self):
        self._advance()
        self._line_num += 1

    def _handle_error(self, error: CsvError):
        self._error_state = True
        self._had_error = True
        match self._bad_line_mode:
            case BadLineMode.ERROR:
                raise error
            case BadLineMode.WARNING:
                print(
                    f"BAD LINE WARNING!\n{error.get_printable_message()}",
                    file=self._print_to_file,
                )

    def _assert_previous_value(self):
        current = self._get_current_token()
        last = self._get_previous_token()

        # If the current and last token was NOT a value token, then error out.
        if (
            current.type == CsvTokenType.COMMA or current.type == CsvTokenType.NEWLINE
        ) and (last.type == CsvTokenType.COMMA or last.type == CsvTokenType.NEWLINE):
            self._handle_error(
                CsvParserError("Empty value!", self._get_current_token())
            )

    def _assert_column_index(self):
        columns_count = self._header.get_column_count()
        if self._column_index >= columns_count:
            self._handle_error(
                CsvParserError("Too many commas in row!", self._get_current_token())
            )

    def _recover_from_error(self):
        self._column_index = 0

        # If we are in an error state, then we advance until we get to a new line.
        while True:
            token = self._get_current_token()
            if token.type == CsvTokenType.NEWLINE:
                self._error_state = False
                self._advance_line()
                return
            self._advance()

    def had_errors(self) -> bool:
        return self._had_error

    def parse(self) -> Generator[CsvRow]:
        # We have already 'primed the pump' in the constructor, so no need to advance here.

        eof = False

        row_values = []
        self._column_index = 0
        while not eof:
            if self._error_state:
                row_values.clear()
                self._recover_from_error()

            token = self._get_current_token()
            match token.type:
                case CsvTokenType.NEWLINE:
                    self._assert_previous_value()

                    row = CsvRow(row_values.copy())
                    row_values.clear()

                    self._column_index = 0
                    self._advance_line()
                    yield row

                case CsvTokenType.COMMA:
                    self._assert_previous_value()

                    self._column_index += 1
                    self._assert_column_index()
                    self._advance()

                case CsvTokenType.VALUE:
                    # At this point we know that 'token' is a CsvValueToken
                    value_token = cast(CsvValueToken, token)

                    try:
                        column_type = self._header.lookup_column_type(
                            self._column_index
                        )
                    except IndexError:
                        self._handle_error(
                            CsvParserError(
                                "Could not get column type, too many commas!",
                                self._get_previous_token(),  # Pass the previous token (which is assumed to be the culprit comma)
                            )
                        )

                    value = CsvValue(column_type, value_token)
                    row_values.append(value)
                    self._advance()

                case CsvTokenType.END_OF_FILE:
                    if len(row_values) != 0:
                        row = CsvRow(row_values.copy())
                        row_values.clear()  # Clearing this will make this yield None on next iter.
                        yield row
                    eof = True
