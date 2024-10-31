from abc import abstractmethod
from collections import OrderedDict
from typing import Iterable, Callable
from matplotlib import animation as pltanim
from ..plot import Plot


class AnimatedPlot(Plot):

    def __init__(
        self,
        data: Iterable[dict[str, str]],
        value_selector: Callable[[dict[str, str]], str],
        **figkw
    ) -> None:
        super().__init__(**figkw)
        self._data = data
        self._value_selector = value_selector

        self._items = OrderedDict()
        self._highest_count = 0

    def setup_anim(self, interval=10):
        self._anim = pltanim.FuncAnimation(
            self._fig,
            self._update,
            frames=self._data,
            blit=False,
            interval=interval,
            cache_frame_data=False,
        )

    @abstractmethod
    def _update(self, data_point: dict[str, str]):
        pass
