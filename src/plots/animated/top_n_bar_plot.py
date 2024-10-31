from typing import Callable, Iterable
import matplotlib
import matplotlib.container
from .animated_plot import AnimatedPlot
from utils import generate_color_map_from_list


class TopNBarPlot(AnimatedPlot):

    def __init__(
        self,
        data: Iterable[dict[str, str]],
        value_selector: Callable[[dict[str, str]], str],
        top_n: int = 20,
        **figkw,
    ) -> None:
        super().__init__(data, value_selector, **figkw)
        self.X_LIMIT_MARGIN = 100
        self._top_n = top_n

    def _get_item_value(self, key: str):
        value = self._items.get(key)
        if not value:
            value = 0
        return value

    def _get_colormap(self):
        # TODO: Cache the generated colormap
        colormap = generate_color_map_from_list(self._items.keys())
        return colormap

    def _update_highest_count(self, new_highest: int):
        self._highest_count = new_highest
        self._axes.set_xlim((0, new_highest + self.X_LIMIT_MARGIN))

    def _update_item(self, data_point: dict[str, str]) -> str:
        item = self._value_selector(data_point)
        item_value = self._get_item_value(item) + 1

        if item_value > self._highest_count:
            self._update_highest_count(item_value)

        self._items[item] = item_value

    def _create_bar_plot(self) -> matplotlib.container.BarContainer:
        bars = self._axes.barh(
            self._items.keys(),
            self._items.values(),
            color=self._get_colormap(),
            edgecolor="black",
        )

        self._axes.set_title("Most reviewed steam games")
        self._axes.set_yticks([])
        self._axes.xaxis.set_ticks_position("top")

        return bars

    def _get_key_value_at_index(self, index: int) -> tuple[str, str]:
        # Get the key and value for N bar.
        # dict.items() does not support indexing so we have to do it like this
        for j, item in enumerate(self._items.items()):
            key, value = item
            if j >= index:
                return key, value

    # Helpful article
    # https://medium.com/@qiaofengmarco/animate-your-data-visualization-with-matplotlib-animation-3e3c69679c90
    def _update(self, data_point: dict[str, str]):
        # Clear the frame so we can draw from scratch
        self._axes.clear()

        self._update_item(data_point)

        bars = self._create_bar_plot()

        for bar_index, _ in enumerate(bars):
            name, value = self._get_key_value_at_index(bar_index)

            # Draw name on bar
            NAME_MARGIN_RIGHT = 10
            self._axes.text(
                value - NAME_MARGIN_RIGHT,
                bar_index,
                name,
                size=14,
                weight=600,
                ha="right",
                va="center",
            )

            # Draw value next to bar
            self._axes.text(
                value,
                bar_index,
                f"{value:,.0f}",
                size=14,
                ha="left",
                va="center",
            )
