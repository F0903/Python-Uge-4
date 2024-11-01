from csv_parsing.parsing.parser import CsvParser, BadLineMode
from csv_parsing.utils import row_to_dict
from csv_parsing.parsing.multiprocess_parser import MultiProcessCsvParser
from plots import Plot
from plots.animated import TopNBarPlot
import matplotlib
import signal
import sys

if __name__ == "__main__":
    # Make matplotlib figure close on CTRL+C in terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    args = sys.argv
    if len(args) < 2:
        raise Exception("You need to specify a file to parse!")

    file_path = args[1]

    # NOTE: all_reviews.csv is huge and starts with several thousand lines of the same game.
    # I recommend reading the weighted_score_above_08.csv file
    file = open(file_path, encoding="utf-8")

    parser = CsvParser(
        file,
        BadLineMode.ERROR,
        print_error_to=None,
        allow_multiline_strings=True,
    )

    # Add fonts including fonts for Chinese which is not included by default (-10000000 social credits)
    matplotlib.rcParams["font.family"] = ["Verdana", "Microsoft JhengHei", "sans-serif"]

    # Map the CsvRows from the parser generator to dicts are easier for us to use here.
    data = map(row_to_dict, parser.parse())
    plot = (
        TopNBarPlot(
            data,
            lambda item: item["game"],
            # Get the playtime in thousands
            lambda item: int(item["author_playtime_forever"]) / 1000,
            figsize=(12, 9),
        )
        .set_xticks_title("Hours played (thousands)")
        .set_title("Top 20 games by hours played per Steam review")
    )
    plot.setup_animation(interval=10)
    Plot.show_all()
