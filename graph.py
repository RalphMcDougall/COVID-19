import matplotlib.pyplot as plt
import math

from datetime import date

KNOWN_COLOURS = {
    "South Africa": "#007749",
    "WORLD": "#000000",
    "US":   "#B22234",
    "France": "#0055A4",
    "Italy": "#008C45",
    "Spain": "#F1BF00",
    "United Kingdom": "#012169",
    "Brazil": "#009C3B"
    # "Russia": "#0039A6"
}


class Chart:

    def __init__(self, numRows, numColumns, title):
        print("Creating chart with", numRows,
              "rows and", numColumns, "columns")
        self.title = title
        self.fig, self.axs = plt.subplots(
            numRows, numColumns, figsize=(numColumns * 4, numRows * 4), num=title)

        # self.fig.suptitle(self.title)

    def makeScatter(self, px, py, dat, keys, xscale, yscale, x_label, y_label, title):
        ax = self.axs[px, py]

        maxX = -1
        maxY = -1
        minX = -1
        minY = -1
        for country in keys:
            x, y = [], []
            for i in dat[country]:
                x.append(i[0])
                y.append(i[1])
            if maxX == -1:
                maxX = x[0]
                minX = x[0]
                maxY = y[0]
                minY = y[0]

            maxX = max(maxX, max(x))
            maxY = max(maxY, max(y))
            minX = min(minX, min(x))
            minY = min(minY, min(y))
            if country in KNOWN_COLOURS.keys():
                ax.scatter(x, y, s=10, label=country, c=KNOWN_COLOURS[country])
                ax.plot(x, y, c=KNOWN_COLOURS[country])
            else:
                ax.scatter(x, y, s=10, label=country)
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
        self.fig.show()

    def saveImage(self):
        self.fig.tight_layout()
        today = date.today()
        d = today.strftime("%d-%m-%Y")
        path = "reports/" + d + "_" + self.title
        self.fig.savefig(path)

        return path + ".png"
