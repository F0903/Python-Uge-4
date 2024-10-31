from csv_parsing.parsing.parser import CsvParser, BadLineMode
from csv_parsing.utils import row_to_dict
from csv_parsing.parsing.multiprocess_parser import MultiProcessCsvParser
from plots import Plot
from plots.animated import TopNBarPlot

if __name__ == "__main__":
    file = open("./data/weighted_score_above_08.csv", encoding="utf-8")

    parser = CsvParser(
        file,
        BadLineMode.ERROR,
        print_error_to=None,
        allow_multiline_strings=True,
    )

    # Map the CsvRows from the parser generator to dicts are easier for us to use here.
    data = map(row_to_dict, parser.parse())
    plot = TopNBarPlot(data, lambda item: item["game"])
    plot.setup_anim()
    Plot.show_all()
