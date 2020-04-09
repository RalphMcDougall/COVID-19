import matplotlib.pyplot as plt
import math


SAMPLE_RATE = 1


class Chart:

    def __init__(self, numRows, numColumns):
        self.fig, self.axs = plt.subplots(numRows, numColumns)
        print(self.axs)

    def makeScatter(self, px, py, store, keys, xscale, yscale, x_label, y_label, title):
        ax = self.axs[px, py]

        maxX = -1
        maxY = -1
        minX = -1
        minY = -1
        for i in range(len(keys)):
            co = keys[i]
            x, y = store.getSmoothedData(co, SAMPLE_RATE)
            if maxX == -1:
                maxX = x[0]
                minX = x[0]
                maxY = y[0]
                minY = y[0]

            maxX = max(maxX, max(x))
            maxY = max(maxY, max(y))
            minX = min(minX, min(x))
            minY = min(minY, min(y))
            ax.scatter(x, y, s=10, label=co)
            ax.plot(x, y)

        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)

        xLog = int(math.log10(maxX))
        yLog = int(math.log10(maxY))
        maxX = int(1 + maxX / (10 ** xLog)) * 10 ** (xLog)
        maxY = int(1 + maxY / (10 ** yLog)) * 10 ** (yLog)

        plt.xlim(minX / 2, maxX)
        plt.ylim(minY / 2, maxY)

        if len(keys) <= 5 and len(keys) >= 2:
            ax.legend()

        ax.grid(True)

    def displayImage(self):
        self.fig.tight_layout()
        plt.show()
