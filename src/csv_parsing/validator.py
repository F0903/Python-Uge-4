import re
from collections.abc import Iterable
from typing import TextIO
from .row import CsvRow
from .value import CsvValue
from .error import CsvError
from .token import CsvToken
from .bad_line_mode import BadLineMode


class CsvValidatorError(CsvError):
    def __init__(self, message: str, token: CsvToken) -> None:
        super().__init__(message, token)


class CsvTypeValidator:
    def __init__(
        self,
        type_pattern_map: dict[str, re.Pattern],
        bad_line_mode: BadLineMode,
        print_error_to: TextIO | None,
    ) -> None:
        self.error_state = False
        self.had_error = False

        self.type_pattern_map = type_pattern_map
        self.bad_line_mode = bad_line_mode
        self.print_to_file = print_error_to

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

    def _check_value(self, value: CsvValue) -> bool:
        value_type = value.get_column_type()
        try:
            pattern = self.type_pattern_map[value_type]
            value_str = value.get_value()

            if not pattern.match(value_str):
                self._handle_error(
                    CsvValidatorError(
                        f"Wrong type format! Value was '{value.get_value()}' expected regex format is '{pattern.pattern}'",
                        value.debug_get_token(),
                    )
                )
                return False

            return True
        except KeyError:
            self._handle_error(
                CsvValidatorError(
                    f"Unknown column type! '{value_type}'", value.debug_get_token()
                )
            )

    def had_errors(self) -> bool:
        return self.had_error

    def validate(self, rows: Iterable[CsvRow | None]) -> Iterable[CsvRow | None]:
        for row in rows:
            if row == None:
                yield None  # We reached the end.

            values = row.get_all_values()
            # Make sure ALL values pass the tests.
            if all(map(self._check_value, values)):
                yield row
