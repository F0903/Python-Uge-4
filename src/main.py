from csv_parsing.parser import CsvParser, BadLineMode
from csv_parsing.utils import row_to_dict
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import islice

file = open("./data/weighted_score_above_08.csv", encoding="utf-8")
parser = CsvParser(
    file, BadLineMode.ERROR, print_error_to=None, allow_multiline_strings=True
)

data = map(row_to_dict, parser.parse())
top10K = islice(data, 10000)

df = pd.DataFrame(top10K)

games_review_count = (
    df.groupby("game").size().reset_index(name="total_game_review_count")
)

top_10_most_reviewed = games_review_count.sort_values(
    "total_game_review_count", ascending=False
).head(10)

print(top_10_most_reviewed)

sns.barplot(
    top_10_most_reviewed,
    x="game",
    y="total_game_review_count",
)
plt.xticks(rotation=25)
plt.tight_layout()
plt.show()
