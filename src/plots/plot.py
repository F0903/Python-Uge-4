from matplotlib import pyplot as plt


class Plot:
    def __init__(self, **figkw) -> None:
        self._fig, self._axes = plt.subplots(**figkw)

    # Must manually manage GUI event loop when using this.
    def show(self):
        self._fig.show()

    @staticmethod
    def show_all():
        plt.show()
