import math


class DataStore:

    def __init__(self):
        self.countryData = {}
        self.dates = []
        self.countries = []

        self.smoothedData = {}

        self.loadData()

    def loadData(self):
        f = open(
            "csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv", "r")
        lines = f.readlines()
        header = lines[0].split(",")
        dateStartInd = 4
        self.dates = header[dateStartInd:]
        totalDays = len(header) - dateStartInd

        self.countryData["WORLD"] = [
            0 for i in range(totalDays)
        ]
        self.countries.append("WORLD")

        for l in lines[1:]:
            line = l.split(",")
            country = line[1]

            dat = []
            for i in line[len(line) - totalDays:]:
                dat.append(int(float(i)))

            # Initialise the current country in the list of all countries if it isn't already there
            if country not in self.countries:
                self.countries.append(country)
                self.countryData[country] = [
                    0 for i in range(totalDays)]

            # Some countries have multiple regions which need to be added onto the country total
            for i, v in enumerate(dat):
                print(country, i, totalDays)
                self.countryData[country][i] += v
                self.countryData["WORLD"][i] += v

        f.close()

    def getSmoothedData(self, country, sampleRate):
        # Get the data averaged over some number of days
        if country not in self.smoothedData.keys():
            self.smoothedData[country] = {}

        if sampleRate not in self.smoothedData[country].keys():
            xs, ys = [], []
            src = self.countryData[country]

            l = -1
            r = 0
            s = 0

            while r < len(src):
                s += src[r]
                if r == len(src) - 1 or (r - l) == sampleRate:
                    xs.append((l + r) / 2)
                    ys.append(s / (r - l))
                    l = r
                    s = 0
                r += 1

            self.smoothedData[country][sampleRate] = [xs, ys]

        return self.smoothedData[country][sampleRate]
