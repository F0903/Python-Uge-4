from matplotlib import pyplot as plt


class Plot:
    def __init__(self, **figkw) -> None:
        plot = plt.subplots(**figkw)
        self._fig: plt.Figure = plot[0]
        self._axes: plt.Axes = plot[1]

    # Must manually manage GUI event loop when using this.
    def show(self):
        self._fig.show()

    @staticmethod
    def show_all():
        plt.show()
