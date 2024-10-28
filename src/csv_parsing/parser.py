from collections.abc import Iterable
from typing import cast, TextIO, override
from .token import CsvToken, CsvValueToken, CsvTokenType
from .error import CsvError
from .row import CsvRow
from .value import CsvValue
from .lexer import CsvLexer
from .bad_line_mode import BadLineMode


class CsvParserError(CsvError):
    def __init__(self, message: str, token: CsvToken) -> None:
        super().__init__(message)
        self.token = token

    @override
    def get_printable_message(self) -> str:
        return f"{self.message}\n\tat line {self.token.line_num}, column {self.token.char_index}"


class CsvHeader:
    def __init__(self, column_decls: list[str]) -> None:
        self.column_decls = column_decls

    def lookup_column_type(self, comma_index: int) -> str:
        return self.column_decls[comma_index]

    def get_column_count(self) -> int:
        return len(self.column_decls)


class CsvParser:
    def __init__(
        self,
        lines: Iterable[str],
        bad_line_mode: BadLineMode,
        print_error_to: TextIO | None,
        allow_multiline_strings: bool = False,
    ) -> None:
        self.error_state = False
        self.had_error = False

        self.input = CsvLexer(lines, allow_multiline_strings).lex()
        self.bad_line_mode = bad_line_mode
        self.print_to_file = print_error_to

        self.line_num = 0
        self.current_token = None
        self._parse_header()

    def _parse_header(self):
        self._advance()  # Priming the pump :)
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

        self.header = CsvHeader(header_column_decls)

    def _get_current_token(self) -> CsvToken:
        return self.current_token

    def _get_previous_token(self) -> CsvToken:
        return self.previous_token

    def _advance(self):
        self.previous_token = self.current_token
        self.current_token = next(self.input)

    def _advance_line(self):
        self._advance()
        self.line_num += 1

    def _handle_error(self, error: CsvError):
        self.error_state = True
        self.had_error = True
        match self.bad_line_mode:
            case BadLineMode.ERROR:
                raise error
            case BadLineMode.WARNING:
                print(
                    f"BAD LINE WARNING!\n{error.get_printable_message()}",
                    file=self.print_to_file,
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
        columns_count = self.header.get_column_count()
        if self.column_index >= columns_count:
            self._handle_error(
                CsvParserError("Too many commas in row!", self._get_current_token())
            )

    def _recover_from_error(self):
        self.column_index = 0

        # If we are in an error state, then we advance until we get to a new line.
        while True:
            token = self._get_current_token()
            if token.type == CsvTokenType.NEWLINE:
                self.error_state = False
                self._advance_line()
                return
            self._advance()

    def had_errors(self) -> bool:
        return self.had_error

    def parse(self) -> Iterable[CsvRow | None]:
        # We have already 'primed the pump' in _parse_header() so no need to here

        row_values = []
        self.column_index = 0
        while True:
            if self.error_state:
                row_values.clear()
                self._recover_from_error()

            token = self._get_current_token()
            match token.type:
                case CsvTokenType.NEWLINE:
                    self._assert_previous_value()

                    row = CsvRow(row_values.copy())
                    row_values.clear()

                    self.column_index = 0
                    self._advance_line()
                    yield row
                case CsvTokenType.COMMA:
                    self._assert_previous_value()

                    self.column_index += 1
                    self._assert_column_index()
                    self._advance()
                case CsvTokenType.VALUE:
                    # At this point we know that 'token' is a CsvValueToken
                    value_token = cast(CsvValueToken, token)

                    try:
                        column_type = self.header.lookup_column_type(self.column_index)
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
                    yield None
