import os
import sys
import locale
import math
import base64
import time

import graph
import process
import share

import constants

locale.setlocale(locale.LC_ALL, "en_GB")


# Runtime modes
SHARE_MODE = False  # Send email to full mailing list
UPDATE_MODE = False  # Pull data from upstream before reporting

SA = ["South Africa"]
UK = ["United Kingdom"]

dataset = {}

images = []


def refreshData():
    # Get data from Johns Hopkins upstream
    if not UPDATE_MODE:
        return
    print("Pulling from upstream/master")
    os.system("git pull upstream master")
    time.sleep(1)
    print("Done")


def constructDatasets():
    global dataset
    print("Constructing datasets:\n")
    dataset["infectedDat"] = process.loadData(
        "csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    dataset["recoveredDat"] = process.loadData(
        "csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
    dataset["deathDat"] = process.loadData(
        "csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
    dataset["deathsSinceSignificant"] = process.daysSinceSurpassing(
        dataset["deathDat"], constants.MIN_SIGNIFICANT_NUMBER)

    dataset["mergedRecovered"] = process.mergeData(
        dataset["recoveredDat"], dataset["deathDat"])
    dataset["activeDat"] = process.subtractData(
        dataset["infectedDat"], dataset["mergedRecovered"])
    dataset["startActiveDat"] = process.daysSinceSurpassing(
        dataset["activeDat"], 1)
    dataset["significantActiveDat"] = process.daysSinceSurpassing(
        dataset["activeDat"], constants.MIN_SIGNIFICANT_NUMBER)

    # Get the number of cases of each country from the common point of when the first reportings started
    dataset["sinceEpoch"] = process.daysSinceSurpassing(
        dataset["infectedDat"], 0)
    # Get the number of cases per day for the last (constants.NUM_DAYS) days
    dataset["restrictedEpoch"] = process.restrictData(
        dataset["sinceEpoch"], constants.NUM_DAYS)
    # Get the percentage increase per day since the start
    dataset["incRateEpoch"] = process.getIncreasePerc(dataset["sinceEpoch"])
    # Only get the last (constants.NUM_DAYS) daily increases
    dataset["restrictedIncRateEpoch"] = process.restrictData(
        dataset["incRateEpoch"], constants.NUM_DAYS)
    # Get the data plotting the number of new cases vs the total cases up to that point
    dataset["incVsValEpoch"] = process.getIncVsVal(dataset["sinceEpoch"])

    # Use the last (constants.NUM_DAYS) infection counts to predictExp the value in 7 days
    dataset["weekPrediction"] = process.predictExp(
        dataset["restrictedEpoch"], 7)

    # Get the data for the number of cases since surpassing the minimum significant value
    dataset["sinceSignificant"] = process.daysSinceSurpassing(
        dataset["infectedDat"], constants.MIN_SIGNIFICANT_NUMBER)
    # Only look at the last 10 days
    dataset["restrictedSignificant"] = process.restrictData(
        dataset["sinceSignificant"], constants.NUM_DAYS)
    dataset["incRateSignificant"] = process.getIncreasePerc(
        dataset["sinceSignificant"])
    dataset["restrictedIncRateSignificant"] = process.restrictData(
        dataset["incRateSignificant"], constants.NUM_DAYS)
    dataset["smoothedIncRateSignificant"] = process.smoothData(
        dataset["incRateSignificant"], constants.SAMPLE_RATE)

    dataset["incVsValSignificant"] = process.getIncVsVal(
        dataset["sinceSignificant"])

    # Get the best fit line for the restricted data
    dataset["logBestFit"] = process.getBestFit(
        process.logY(dataset["restrictedEpoch"]))

    # Get the 7-day predictions
    dataset["predict7"] = process.getDailyPredictions(
        dataset["sinceSignificant"], 7, constants.NUM_DAYS)
    # Get the 30-day predictions
    dataset["predict30"] = process.getDailyPredictions(
        dataset["sinceSignificant"], 30, constants.NUM_DAYS)

    print("Datasets constructed. \n\n")


def startAnalysis():
    global images, dataset
    constructDatasets()

    sa_chart = graph.CountryProfile("South Africa", dataset)
    uk_chart = graph.CountryProfile("United Kingdom", dataset)

    # Get the data for the current 4 highest countries as well as the world total
    highestCountries = process.getCurrentMax(dataset["infectedDat"], 6)

    world_chart = graph.Chart(2, 2, "WORLD")

    world_chart.makeScatter(0, 0, dataset["sinceSignificant"], highestCountries, "linear",
                            "log", "Days since surpassing " + str(constants.MIN_SIGNIFICANT_NUMBER) + " infections", "Number of infections", "Current highest countries")

    world_chart.makeScatter(0, 1, dataset["significantActiveDat"], highestCountries, "linear", "log",
                            "Days since " + str(constants.MIN_SIGNIFICANT_NUMBER) + " active cases", "Number of infections", "Active cases")

    world_chart.makeScatter(1, 0, dataset["restrictedIncRateEpoch"], highestCountries, "linear", "linear",
                            "Days since epoch", "Growth rate (%)", "Daily growth rate")

    world_chart.makeScatter(1, 1, dataset["incVsValEpoch"], highestCountries, "log", "log",
                            "Number of infections", "New infections per day", "Increase vs Value")

    saImg = sa_chart.saveImage()
    ukImg = uk_chart.saveImage()
    worldImg = world_chart.saveImage()

    images = [saImg, ukImg, worldImg]
    info = ""
    info += getEditorsNotes()
    info += """<section>
<p>
<h2> Executive Summary </h2>

Over the last {:n} days, COVID-19 has been exhibiting a daily growth rate of {:n}%. The {:n} countries with the highest number of infections are:
<ol>
""".format(len(dataset["restrictedEpoch"]["WORLD"]), round(100 * math.exp(dataset["logBestFit"]["WORLD"][1]) - 100, 2), len(highestCountries) - 1)

    for country in highestCountries:
        if country == "WORLD":
            continue
        info += "<li> {} </li>\n".format(country)

    info += """
</ol>

The table below gives a summary of the latest statistics from various countries for the last 24 hours.
"""
    info += """
<table>
<tr>
<th> Country </th>
<th> Number of infections </th>
<th> Absolute increase </th>
<th> Percent increase </th>
</tr>
"""

    datC = highestCountries[::]
    if "United Kingdom" not in datC:
        datC += UK
    if "South Africa" not in datC:
        datC += SA

    for c in datC:
        cnt = dataset["infectedDat"][c][-1][1]
        inc = dataset["infectedDat"][c][-1][1] - \
            dataset["infectedDat"][c][-2][1]
        perc = round(100 * inc / (cnt - inc), 2)
        info += """<tr> 
<td> {:s} </td>
<td align="right"> {:n} </td>
<td align="right"> {:n} </td>
<td align="right"> {:n}% </td>
</tr>
""".format(c, cnt, inc, perc)
    info += """</table>
</p>
</section>"""

    info += sa_chart.getProfileAnalysis(dataset)
    info += uk_chart.getProfileAnalysis(dataset)

    info += "<section>"
    info += "<h2> World Analysis</h2>\n"
    info += "<p><img src=\"cid:{0}\"</p>\n".format(worldImg)
    info += displayGroupTrend(highestCountries)
    info += "</section>\n"

    share.sendEmail(info, images, not SHARE_MODE)


def getEditorsNotes():
    res = ""
    with open("editorsnotes.txt") as f:
        text = f.read()
        if len(text) > 0:
            print("Adding editor's notes")
            res = "<section>\n"
            res += "<h2> Editor's Notes </h2>\n"
            res += "<p>" + text + "</p>\n"
            res += "</section>"
            with open("editorsbackup.txt", "w") as bf:
                bf.write(text)

    if SHARE_MODE:
        with open("editorsnotes.txt", "w") as f:
            print("Clearing file")
            f.write("")
    return res


def displayTrend(c, dataset):
    global images
    r = ""
    bestFit = process.getBestFit(
        process.logY(dataset["restrictedSignificant"]))
    corrCoef = process.corrCoef(process.logY(dataset["restrictedSignificant"]))
    p1 = process.predictExp(dataset["restrictedSignificant"], 7)
    p2 = process.predictExp(dataset["restrictedSignificant"], 30)

    for country in c:
        func = "<i>y = "
        a = bestFit[country][0]
        b = bestFit[country][1]
        func += str(round(math.exp(a), 4)) + "&#215;"
        func += str(round(math.exp(b), 4)) + "<sup> t </sup> </i>"
        r += """
The following table represents the exponential function of best fit for the last {:n} days. This is used to extrapolate what the number of cases will be in 7 and 30 days if the rate of increase stays the same.
<table>
<tr>
<td> Growth function </td>
<td> {:s} </td>
</tr>
<tr>
<td> Daily growth rate </td>
<td align="right"> {:n}% </td>
</tr>
<tr>
<td> Current infections </td>
<td align="right"> {:n} </td>
</tr>
<tr>
<td> 7-day infections </td>
<td align="right"> {:n} </td>
</tr>
<tr>
<td> 30-day infections </td>
<td align="right"> {:n} </td>
</tr>
</table>

""".format(constants.NUM_DAYS, func, round(100 * (math.exp(b) - 1), 2),
           int(dataset["restrictedSignificant"][country][-1][1]), round(p1[country]), round(p2[country]))

        predDat = {
            "Actual": dataset["sinceSignificant"][country], "7 Day": dataset["predict7"][country], "30 Day": dataset["predict30"][country]}
        predGraph = graph.Chart(1, 1, country + "PREDICTIONS")
        predGraph.makeScatter(0, 0, predDat, ["Actual", "7 Day", "30 Day"], "linear", "log", "Days since surpassing " + str(
            constants.MIN_SIGNIFICANT_NUMBER) + " infections", "Number of infections", country + " predictions vs actual values")
        predImage = predGraph.saveImage()
        #r += "<p><img src=\"cid:{0}\"</p>\n".format(predImage)
        images.append(predImage)

    r += """</p>\n""".format(len(dataset["restrictedSignificant"][c[0]]))
    return r


def displayGroupTrend(c):
    global images
    r = ""
    bestFit = process.getBestFit(
        process.logY(dataset["restrictedSignificant"]))
    corrCoef = process.corrCoef(process.logY(dataset["restrictedSignificant"]))
    p1 = process.predictExp(dataset["restrictedSignificant"], 7)
    p2 = process.predictExp(dataset["restrictedSignificant"], 30)

    r += """
The following table represents the exponential function of best fit for the last {:n} days. This is used to extrapolate what the number of cases will be in 7 and 30 days if the rate of increase stays the same.
<table>
<tr>
<td> Country </td>
<td> Growth Function </td>
<td> Avg. daily growth rate </td>
<td> Current infections </td>
<td> 7-day infections </td>
<td> 30-day infections </td>
</tr>
""".format(constants.NUM_DAYS)

    for country in c:
        func = "<i>"
        a = bestFit[country][0]
        b = bestFit[country][1]
        func += str(round(math.exp(a), 4)) + "&#215;"
        func += str(round(math.exp(b), 4)) + "<sup> t </sup> </i>"
        r += """
<tr>
<td> {:s} </td>
<td align="right"> {:s} </td>
<td align="right"> {:n}% </td>
<td align="right"> {:n} </td>
<td align="right"> {:n} </td>
<td align="right"> {:n} </td>
</tr>

""".format(country, func, round(100 * (math.exp(b) - 1), 2),
           int(dataset["restrictedSignificant"][country][-1][1]), round(p1[country]), round(p2[country]))

        predDat = {
            "Actual": dataset["sinceSignificant"][country], "7 Day": dataset["predict7"][country], "30 Day": dataset["predict30"][country]}
        predGraph = graph.Chart(1, 1, country + "PREDICTIONS")
        predGraph.makeScatter(0, 0, predDat, ["Actual", "7 Day", "30 Day"], "linear", "log", "Days since surpassing " + str(
            constants.MIN_SIGNIFICANT_NUMBER) + " infections", "Number of infections", country + " predictions vs actual values")
        predImage = predGraph.saveImage()
        #r += "<p><img src=\"cid:{0}\"</p>\n".format(predImage)
        images.append(predImage)

    r += """</table> </p>\n"""
    return r


if __name__ == "__main__":
    SHARE_MODE = len(sys.argv) > 1 and "s" in sys.argv[1]
    UPDATE_MODE = len(sys.argv) > 1 and "u" in sys.argv[1]
    refreshData()
    startAnalysis()
