from collections import OrderedDict
from csv_parsing.parsing.parser import CsvParser, BadLineMode
from csv_parsing.utils import row_to_dict
from csv_parsing.parsing.multiprocess_parser import MultiProcessCsvParser
import matplotlib.animation as pltanim
import matplotlib.pyplot as plt

if __name__ == "__main__":
    file = open("./data/weighted_score_above_08.csv", encoding="utf-8")

    parser = CsvParser(
        file,
        BadLineMode.ERROR,
        print_error_to=None,
        allow_multiline_strings=True,
        # Since the data is streamed we don't know the amount of lines beforehand
        # so this chunk size needs to be a best guess on how best to divide the load per logical processor
    )

    # Initialize the plot
    fig = plt.figure(figsize=(10, 6))

    plt.title("Review Count Per Steam Game")
    plt.xlabel("Game")
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Review Count")

    Y_LIMIT_MARGIN = 100
    plt.ylim((0, Y_LIMIT_MARGIN))

    # Data generator instance
    data = map(row_to_dict, parser.parse())

    # PLAN:
    # We go through each returned CSV row from our generator, add the game to a dict of game -> review_count.
    # Then we check if the game fits in our dict of top 20 most reviewed games.
    # Then we plot the top 20 games in descending order.

    top20_most_reviewed_games = OrderedDict()
    highest_count = 0

    # Helpful article
    # https://medium.com/@qiaofengmarco/animate-your-data-visualization-with-matplotlib-animation-3e3c69679c90
    def update(row_dict: dict[str, str]):
        # Python moment
        global bars, highest_count

        game = row_dict["game"]

        reconstruct = False

        game_review_total = top20_most_reviewed_games.get(game)
        if not game_review_total:  # We have no record of the game
            game_review_total = 0
            reconstruct = True

        game_review_total += 1

        if game_review_total > highest_count:
            highest_count = game_review_total
            plt.ylim((0, highest_count + Y_LIMIT_MARGIN))

        top20_most_reviewed_games[game] = game_review_total

        if reconstruct:
            # We need to remake the plot from scratch each time we encounter a new game.
            bars = plt.barh(
                top20_most_reviewed_games.keys(), top20_most_reviewed_games.values()
            )
            plt.tight_layout()
        else:
            # Set bar heights to
            for i, bar in enumerate(bars):
                # Get the review count of the game corresponding to the current bar index.
                review_count = 0
                for j, item in enumerate(top20_most_reviewed_games.items()):
                    review_count = item[1]
                    if j >= i:
                        break

                bar.set_height(review_count)

        return bars

    anim = pltanim.FuncAnimation(
        fig, update, frames=data, blit=False, interval=10, cache_frame_data=False
    )
    plt.show()
