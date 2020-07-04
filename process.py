import math
import numpy as np

ALL_COUNTRIES = []


def loadInfectionDataFromFile():
    # Return a dictionary of the number of cases that every country had on a given date
    print("Loading infections from file")
    f = open(
        "csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv", "r")
    lines = f.readlines()
    header = lines[0].split(",")
    dateStartInd = 4
    dates = header[dateStartInd:]
    totalDays = len(dates)

    countryData = {}

    countryData["WORLD"] = [
        [dates[i], 0] for i in range(totalDays)]

    ALL_COUNTRIES.append("WORLD")

    for l in lines[1:]:
        line = l.split(",")
        country = line[1]

        dat = []
        for ind, val in enumerate(line[-1 * totalDays:]):
            dat.append([dates[ind], int(float(val))])

            # Initialise the current country in the list of all countries if it isn't already there
            if country not in ALL_COUNTRIES:
                ALL_COUNTRIES.append(country)
                countryData[country] = [
                    [dates[i], 0] for i in range(totalDays)]

        # Some countries have multiple regions which need to be added onto the country total
        for ind, v in enumerate(dat):
            countryData[country][ind][1] += v[1]
            countryData["WORLD"][ind][1] += v[1]

    f.close()
    ALL_COUNTRIES.sort()
    return countryData


def daysSinceSurpassing(dat, val):
    print("Limiting data to days since surpassing", val, "cases")
    res = {}

    for country in dat.keys():
        found = False
        cnt = 0
        res[country] = []
        for i in dat[country]:
            if i[1] >= val:
                found = True
            if found:
                res[country].append([cnt, i[1]])
                cnt += 1

    return res


def smoothData(dat, sampleRate):
    print("Smoothing data with sample rate", sampleRate)
    res = {}

    for country in dat.keys():
        cdat = dat[country]
        proc = []
        r = len(cdat)
        l = r - 1
        s = 0
        while l >= 0:
            s += cdat[l][1]
            if r - l == sampleRate or l == 0:
                proc.append([cdat[r - 1][0], s / sampleRate])
                s = 0
                r = l
            l -= 1
        proc.reverse()
        res[country] = proc

    return res


def restrictData(dat, num):
    print("Restricting data to only last", num, "values")
    res = {}
    for country in ALL_COUNTRIES:
        res[country] = dat[country][-1 * num:]

    return res


def getCurrentMax(dat, size):
    print("Getting", size, "highest values")
    d = []
    for country in ALL_COUNTRIES:
        if len(dat[country]) == 0:
            continue
        d.append([dat[country][-1][1], country])
    d.sort()

    res = []
    for i in range(size):
        res.append(d[-1 - i][1])
    return res


def getIncreasePerc(dat):
    res = {}

    for country in ALL_COUNTRIES:
        d = []
        cdat = dat[country]
        for i in range(1, len(cdat)):
            if cdat[i - 1][1] == 0:
                d.append([cdat[i][0], 0])
            else:
                d.append([cdat[i][0], 100 * (cdat[i][1] / cdat[i - 1][1] - 1)])

        res[country] = d

    return res


def getIncVsVal(dat):
    res = {}
    for country in ALL_COUNTRIES:
        d = []
        cdat = dat[country]
        for i in range(1, len(cdat)):
            if i > 1 and d[-1][1] > 3 * (cdat[i][1] - cdat[i - 1][1]):
                # Likely noisy data
                continue
            d.append([cdat[i][1], cdat[i][1] - cdat[i - 1][1]])
        res[country] = d
    return res


def getBestFit(dat):
    res = {}

    for country in ALL_COUNTRIES:
        cdat = dat[country]
        if len(cdat) == 0:
            res[country] = [0, 0]
            continue

        xbar = 0
        ybar = 0

        for i in cdat:
            xbar += i[0]
            ybar += i[1]

        n = len(cdat)
        xbar /= n
        ybar /= n
        a, b = 0, 0
        sxy = 0
        xmbs = 0
        for i in cdat:
            sxy += i[0] * i[1]
            xmbs += (i[0] - xbar) ** 2

        b = (sxy - n * xbar * ybar) / (xmbs)
        a = ybar - b * xbar

        res[country] = [a, b]

    return res


def logY(dat):
    res = {}

    for country in ALL_COUNTRIES:
        cdat = dat[country]
        d = []
        for i in cdat:
            if i[1] <= 0:
                break
            d.append([i[0], math.log(i[1])])
        res[country] = d

    return res


def expY(dat):
    res = {}

    for country in ALL_COUNTRIES:
        cdat = dat[country]
        d = []
        for i in cdat:
            d.append([i[0], math.exp(i[1])])
        res[country] = d

    return res


def predictExp(dat, fut):
    fit = getBestFit(logY(dat))
    res = {}

    for country in ALL_COUNTRIES:
        if len(dat[country]) == 0:
            res[country] = 0
            continue
        res[country] = math.exp(fit[country][1] *
                                (dat[country][-1][0] + fut) + fit[country][0])

    return res


def extrapolateExp(sample, days):
    logV = [[val[0], math.log(val[1])] for val in sample]

    xvals = [i[0] for i in logV]
    yvals = [i[1] for i in logV]
    m, c = np.polyfit(xvals, yvals, 1)

    predictedValue = math.exp(c + m * (xvals[-1] + days))
    return predictedValue


def getDailyPredictions(dat, daysInFuture, sampleSize):
    res = {}

    for country in ALL_COUNTRIES:
        res[country] = []
        if len(dat[country]) == 0:
            continue
        for i in range(sampleSize - 1, dat[country][-1][0] - daysInFuture):
            sample = []
            for j in range(sampleSize):
                sample.append(dat[country][i - (sampleSize - 1) + j])
            v = extrapolateExp(sample, daysInFuture)
            res[country].append([i + daysInFuture, v])

    return res


def corrCoef(dat):
    res = {}

    for country in ALL_COUNTRIES:
        cdat = dat[country]
        n = len(cdat)
        if n <= 1:
            res[country] = 0
            continue
        xbar = 0
        ybar = 0
        for i in cdat:
            xbar += i[0]
            ybar += i[1]
        xbar /= n
        ybar /= n

        nu = 0
        dx = 0
        dy = 0

        for i in cdat:
            nu += (i[0] - xbar) * (i[1] - ybar)
            dx += (i[0] - xbar) ** 2
            dy += (i[1] - ybar) ** 2
        if dx * dy == 0:
            res[country] = 0
            continue
        res[country] = nu / ((dx * dy) ** 0.5)

    return res
