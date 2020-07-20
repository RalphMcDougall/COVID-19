import matplotlib.pyplot as plt
import math

from datetime import date

import constants
import run

KNOWN_COLOURS = {
    "South Africa": "#007749",
    "WORLD": "#000000",
    "US":   "#B22234",
    "France": "#0055A4",
    "Italy": "#008C45",
    "Spain": "#F1BF00",
    "United Kingdom": "#012169",
    "Brazil": "#009C3B",
    "Austria": "#ED2939",
    "India": "#FF9933",
    "Russia": "#0032A0"
}


class Chart:

    def __init__(self, numRows, numColumns, title):
        self.title = title.replace(" ", "_")
        self.numRows = numRows
        self.numCols = numColumns
        self.imgPath = ""
        self.fig, self.axs = plt.subplots(
            numRows, numColumns, figsize=(numColumns * 4, numRows * 4), num=title)

        # self.fig.suptitle(self.title)

    def makeScatter(self, px, py, dat, keys, xscale, yscale, x_label, y_label, title):
        if self.numRows == 1 and self.numCols == 1:
            ax = self.axs
        else:
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

        if len(keys) <= 6 and len(keys) >= 2:
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
        self.imgPath = path + ".png"

        return path + ".png"


class CountryProfile(Chart):

    def __init__(self, country, dataset):
        super().__init__(2, 2, country)
        self.country = country

        self.makeScatter(0, 0, dataset["sinceSignificant"], [country], "linear", "log", "Days since surpassing " + str(
            constants.MIN_SIGNIFICANT_NUMBER) + " infections", "Number of infections", "Total infections")

        if country in ["United Kingdom", "Spain"]:
            # These countries don't record the number of recoveries, so the number of active cases is not accurate
            self.makeScatter(0, 1, dataset["deathsSinceSignificant"], [country], "linear", "log", "Days since surpassing " + str(
                constants.MIN_SIGNIFICANT_NUMBER) + " deaths", "Number of deaths", "Total deaths")
        else:
            self.makeScatter(0, 1, dataset["startActiveDat"], [country], "linear", "log",
                             "Days since first infection", "Number of infections", "Active cases")

        self.makeScatter(1, 0, dataset["smoothedIncRateSignificant"], [country], "linear", "linear", "Days since surpassing " + str(
            constants.MIN_SIGNIFICANT_NUMBER) + " infections", "Daily growth rate (%)", "Daily growth rate")

        self.makeScatter(1, 1, dataset["incVsValSignificant"], [country], "linear", "linear",
                         "Number of infections", "New infections per day", "Increase vs Value")

    def getProfileAnalysis(self, dataset):
        res = ""

        res += "<section>\n"
        res += "<h2> " + self.country + " Analysis</h2>\n"
        res += "<p><img src=\"cid:{0}\"</p>\n".format(self.imgPath)
        res += run.displayTrend([self.country], dataset)
        res += "</section>\n"

        return res
