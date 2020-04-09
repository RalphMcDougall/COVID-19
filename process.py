import math

ALL_COUNTRIES = []


def loadInfectionDataFromFile():
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
    print("Limiting data to days since surpassing", val)
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
            d.append([cdat[i][1], cdat[i][1] - cdat[i - 1][1]])
        res[country] = d
    return res
