from collections import OrderedDict
from typing import Callable, Iterable
import matplotlib
import matplotlib.pyplot as plt
from utils import generate_color_map_from_list
from .animated_plot import AnimatedPlot


class TopNBarPlot(AnimatedPlot):

    def __init__(
        self,
        data: Iterable[dict[str, str]],
        key_selector: Callable[[dict[str, str]], str],
        value_selector: Callable[[dict[str, str]], int],
        top_n: int = 20,
        **figkw,
    ) -> None:
        super().__init__(data, **figkw)

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

    def set_title(self, title: str):
        self._title = title

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

    def _create_bar_plot(self) -> matplotlib.container.BarContainer:
        # TODO: optimize, this is incredibly slow

        bar_data = self._current_bar_data = self._get_top_items()
        bar_data.reverse()
        y, x = zip(*bar_data)

        axes = self._axes

        bars = axes.barh(
            y,
            x,
            color=generate_color_map_from_list(y),
            edgecolor="black",
        )

        # Title
        axes.text(
            0,
            1.1,
            self._title,
            transform=axes.transAxes,
            size=24,
            weight=600,
            ha="left",
        )

        # Below title
        axes.text(
            0,
            1.06,
            "Hours played (thousands)",
            transform=axes.transAxes,
            size=12,
            color=self.SECONDARY_COLOR,
        )

        axes.set_frame_on(False)
        axes.set_yticks([])

        axes.xaxis.set_ticks_position("top")
        axes.tick_params(axis="x", colors=self.SECONDARY_COLOR, labelsize=12)
        axes.xaxis.set_major_formatter("{x:,.0f}h")

        # Bottom text
        axes.text(
            0.5,
            -0.05,
            f"Total records: {self._total_records}",
            transform=axes.transAxes,
            size=18,
            weight=500,
            ha="center",
            va="bottom",
        )

        # Adjust size of plot
        plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1)

        return bars

    def _get_key_value_at_index(self, index: int) -> tuple[str, int]:
        # Get the key and value for N bar.
        # dict.items() does not support indexing so we have to do it like this
        for j, item in enumerate(self._current_bar_data):
            key, value = item
            if j >= index:
                return key, value

    def _calc_rough_text_width(self, text: str, factor: int = 1) -> int:
        # These are just pure magic numbers lol
        ASCII_VALUE = 12
        NON_ASCII_VALUE = 18
        total = 0

        for char in text:
            total += ASCII_VALUE if char.isascii() else NON_ASCII_VALUE

        return total * factor

    def _render_bar_text(self, bar_index: int):
        name, value = self._get_key_value_at_index(bar_index)

        scaling_factor = self._highest_count / 1000

        bar_text_margin = self.BAR_TEXT_MARGIN * scaling_factor

        rough_text_width = self._calc_rough_text_width(name, scaling_factor)

        min_width = rough_text_width + bar_text_margin
        put_text_right = value < min_width

        name_text_x = value if put_text_right else value - bar_text_margin
        name_text_ha = "left" if put_text_right else "right"

        # Draw name on bar
        self._axes.text(
            name_text_x,
            bar_index,
            name,
            size=14,
            weight=600,
            ha=name_text_ha,
            va="center",
        )

        value_text_x = (
            name_text_x + min_width + bar_text_margin * 2
            if put_text_right
            else value + bar_text_margin
        )

        # Draw value next to bar
        self._axes.text(
            value_text_x,
            bar_index,
            f"{value:,.0f}h",
            size=14,
            ha="left",
            va="center",
        )

    # Helpful article
    # https://medium.com/@qiaofengmarco/animate-your-data-visualization-with-matplotlib-animation-3e3c69679c90
    def _update(self, data_point: dict[str, str]):
        # Clear the frame so we can draw from scratch
        self._axes.clear()

        self._update_item(data_point)
        bars = self._create_bar_plot()

        for bar_index, _ in enumerate(bars):
            self._render_bar_text(bar_index)
