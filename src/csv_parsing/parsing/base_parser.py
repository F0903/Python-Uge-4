from abc import abstractmethod
from collections.abc import Generator
from ..row import CsvRow


class BaseCsvParser:
    @abstractmethod
    def had_errors(self) -> bool:
        pass

    @abstractmethod
    def parse(self) -> Generator[CsvRow]:
        pass
