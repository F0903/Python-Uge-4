from abc import abstractmethod
from typing import Iterable
from matplotlib import animation as pltanim
from ..plot import Plot


class AnimatedPlot(Plot):

    def __init__(self, data: Iterable[dict[str, str]], **figkw) -> None:
        super().__init__(**figkw)
        self._data = data

    def setup_animation(self, interval=10):
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
