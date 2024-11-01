from collections import OrderedDict
from typing import Callable, Iterable, Self
import matplotlib.pyplot as plt
from utils import generate_color_map_from_list
from .animated_plot import AnimatedPlot


class BlitText:
    def __init__(self, text: plt.Text):
        self._changed = False
        self._text = text

    def set_x(self, x: int):
        self._text.set_x(x)
        self._changed = True

    def set_y(self, y: int):
        self._text.set_y(y)
        self._changed = True

    def set_text(self, text: str):
        self._text.set_text(text)
        self._changed = True

    def set_visible(self, value: bool):
        self._text.set_visible(value)
        self._changed = True

    def has_changed(self) -> bool:
        return self._changed

    def reset_changed(self):
        self._changed = False

    def get_artist(self) -> plt.Artist:
        return self._text

    def get_if_changed(self) -> list[plt.Artist]:
        artists = []
        if self._changed:
            artists.append(self._text)
        return artists


class BarTextPair:
    def __init__(self, name_text: BlitText, value_text: BlitText):
        self._name_text = name_text
        self._value_text = value_text

    def get_artists(self) -> list[plt.Artist]:
        artists = [self._name_text.get_artist(), self._value_text.get_artist()]
        return artists

    def get_changed_artists(self) -> list[plt.Artist]:
        artists = self._name_text.get_if_changed() + self._value_text.get_if_changed()
        return artists

    def has_name(self, name: str) -> bool:
        return self._name_text.get_text() == name

    def get_name_text(self) -> BlitText:
        return self._name_text

    def get_value_text(self) -> BlitText:
        return self._value_text

    def reset_changed(self):
        self._name_text.reset_changed()
        self._value_text.reset_changed()

    def __eq__(self, value: str):
        return self.has_name(value)


class Bar:
    def __init__(self, bar: plt.Rectangle, text_pair: BarTextPair):
        self._bar = bar
        self._changed = False
        self._bar_text_pair = text_pair

    def get_artists(self) -> list[plt.Artist]:
        return [self._bar] + self._bar_text_pair.get_artists()

    def get_changed_artists(self) -> list[plt.Artist]:
        artist_list = []
        if self._changed:
            artist_list.append(self._bar)

        artist_list += self._bar_text_pair.get_changed_artists()

        self.reset_changed()

        return artist_list

    def set_color(self, color: str):
        self._bar.set_color(color)
        self._changed = True

    def set_visible(self, value: bool):
        self._bar.set_visible(value)
        self._changed = True

    def set_width(self, width: float):
        self._bar.set_width(width)
        self._changed = True

    def get_text(self) -> BarTextPair:
        return self._bar_text_pair

    def reset_changed(self):
        self._changed = False
        self._bar_text_pair.reset_changed()


class TopNBarPlot(AnimatedPlot):

    def __init__(
        self,
        data: Iterable[dict[str, str]],
        key_selector: Callable[[dict[str, str]], str],
        value_selector: Callable[[dict[str, str]], int],
        top_n: int = 20,
        **figkw,
    ) -> None:
        super().__init__(data, blit=True, **figkw)

        self.SECONDARY_COLOR = "#666666"
        self.X_LIMIT_MARGIN_PERCENT = 0.1
        self.BAR_TEXT_MARGIN = 10

        self._title = ""

        self._key_selector = key_selector
        self._value_selector = value_selector

        self._items = OrderedDict()
        self._highest_count = 0
        self._top_n = top_n

        self._total_records = 0

        self._bars: list[Bar] = []
        self._bar_texts: list[BarTextPair] = []

    def set_title(self, title: str) -> Self:
        self._title = title
        return self

    def set_xticks_title(self, value: str) -> Self:
        self._xticks_title = value
        return self

    def _update_highest_count(self, new_highest: int):
        self._highest_count = new_highest
        self._axes.set_xlim(
            (
                0,
                new_highest + (new_highest * self.X_LIMIT_MARGIN_PERCENT),
            )
        )

    def _update_item(self, data_point: dict[str, str]):
        self._total_records += 1

        item_key = self._key_selector(data_point)
        item_value = self._value_selector(data_point)

        self._items.setdefault(item_key, 0)

        old_value = self._items[item_key]
        new_value = old_value + item_value
        self._items[item_key] = new_value

        if new_value > self._highest_count:
            self._update_highest_count(new_value)

    def _get_top_items(self) -> list[tuple[str, int]]:
        # Sort the dictionary items by value descending and get the first N items.
        sorted_items = sorted(self._items.items(), key=lambda x: x[1], reverse=True)
        top_n_items = sorted_items[: self._top_n]
        return top_n_items

    def _get_key_value_at_index(self, index: int) -> tuple[str, int]:
        # Get the key and value for N bar.
        # dict.items() does not support indexing so we have to do it like this
        for j, item in enumerate(self._current_bar_data):
            key, value = item
            if j >= index:
                return key, value

    def _draw_static(self):
        # This sometimes gets called multiple times for some reason
        # so ensure we don't add more than we need
        if len(self._bars) >= self._top_n:
            return [x for xs in self._bars for x in xs.get_artists()]

        # Initialize bar with our max amount of bars
        y = ["" for _ in range(0, self._top_n)]
        x = [0 for _ in range(0, self._top_n)]
        bar_container = self._bar_container = self._axes.barh(y, x)

        for bar in bar_container:
            bar: plt.Rectangle = bar
            bar.set_visible(False)

            # We don't care about the values at this point
            label_text = self._axes.text(
                0, 0, "", ha="right", va="center", size=14, visible=False
            )
            value_text = self._axes.text(
                0, 0, "", ha="left", va="center", size=14, visible=False
            )

            new_bar = Bar(bar, BarTextPair(BlitText(label_text), BlitText(value_text)))
            self._bars.append(new_bar)

        # Add static title and subtitle
        self._axes.text(
            0,
            1.1,
            self._title,
            transform=self._axes.transAxes,
            size=24,
            weight=600,
            ha="left",
        )
        self._axes.text(
            0,
            1.06,
            self._xticks_title,
            transform=self._axes.transAxes,
            size=12,
            color=self.SECONDARY_COLOR,
        )

        self._records_text = BlitText(
            self._axes.text(
                0,
                0,
                f"Total records: {self._total_records}",
                transform=self._axes.transAxes,
                size=18,
                weight=500,
                ha="center",
                va="bottom",
            )
        )

        # Axes configuration
        self._axes.set_frame_on(False)
        self._axes.set_yticks([])
        self._axes.xaxis.set_ticks_position("top")
        self._axes.tick_params(axis="x", colors=self.SECONDARY_COLOR, labelsize=12)
        self._axes.xaxis.set_major_formatter("{x:,.0f}h")

        # Adjust size of plot
        plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1)

        return [x for xs in self._bars for x in xs.get_artists()]

    def _update_bars(self):
        top_items = self._get_top_items()

        # Update bar heights and text
        for i, (bar, item) in enumerate(zip(self._bars, top_items)):
            item_name, item_value = item

            bar.set_visible(True)
            bar.set_width(item_value)
            bar.set_color(generate_color_map_from_list([item_name])[0])

            # Update text next to each bar
            bar_text = bar.get_text()

            bar_name_text = bar_text.get_name_text()
            bar_name_text.set_visible(True)
            bar_name_text.set_text(item_name)
            bar_name_text.set_x(item_value)
            bar_name_text.set_y(i)

            bar_value_text = bar_text.get_value_text()
            bar_name_text.set_visible(True)
            bar_value_text.set_text(f"{item_value:,.0f}h")
            bar_value_text.set_x(item_value)
            bar_value_text.set_y(i)

    def _draw_dynamic(self, data_point):
        self._update_item(data_point)
        self._update_bars()

        self._records_text.set_text(f"Total records: {self._total_records}")

        artists = [
            x for xs in self._bars for x in xs.get_changed_artists()
        ] + self._records_text.get_if_changed()
        return artists
