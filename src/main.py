from csv_parsing.parser import CsvParser, BadLineMode
from csv_parsing.utils import row_to_dict
from csv_parsing.multiprocess_parser import MultiProcessParser
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import islice

if __name__ == "__main__":
    file = open("./data/weighted_score_above_08.csv", encoding="utf-8")

    test_parser = MultiProcessParser(file, BadLineMode.ERROR, print_error_to=None)
    for val in test_parser.parse():
        print(val)

    parser = CsvParser(
        file, BadLineMode.ERROR, print_error_to=None, allow_multiline_strings=True
    )

    data = map(row_to_dict, parser.parse())

    df = pd.DataFrame(data)

    games_review_count = (
        df.groupby("game").size().reset_index(name="total_game_review_count")
    )

    most_reviewed = games_review_count.sort_values(
        "total_game_review_count", ascending=False
    ).head(20)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        most_reviewed,
        x="game",
        y="total_game_review_count",
    )
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.show()
