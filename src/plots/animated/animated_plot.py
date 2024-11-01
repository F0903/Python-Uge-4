from abc import abstractmethod
from typing import Iterable
from matplotlib import animation as pltanim
from ..plot import Plot


class AnimatedPlot(Plot):

    def __init__(self, data: Iterable[dict[str, str]], blit=False, **figkw) -> None:
        super().__init__(**figkw)
        self._data = data
        self._blit = blit

    def setup_animation(self, interval=10):
        self._anim = pltanim.FuncAnimation(
            self._fig,
            self._draw_dynamic,
            init_func=self._draw_static if self._blit else None,
            frames=self._data,
            blit=self._blit,
            interval=interval,
            cache_frame_data=False,
        )

    @abstractmethod
    def _draw_static(self):
        pass

    @abstractmethod
    def _draw_dynamic(self, data_point: dict[str, str]):
        pass
