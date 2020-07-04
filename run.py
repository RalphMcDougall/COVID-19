import os
import sys
import locale
import math
import base64

import graph
import process
import share

locale.setlocale(locale.LC_ALL, "en_GB")

# The minimum number of infections to start processing data for
MIN_SIGNIFICANT_INFECTIONS = 100
# The number of days to process before giving a data point
SAMPLE_RATE = 1
# The number of days to look into the past for the model predictExpion
NUM_DAYS = 10

# Runtime modes
SHARE_MODE = False  # Send email to full mailing list
UPDATE_MODE = False  # Pull data from upstream before reporting
DISPLAY_MODE = False  # Display the graphs

SA = ["South Africa"]
UK = ["United Kingdom"]

rawDat = {}
sinceEpoch = {}
smoothedEpoch = {}
restrictedEpoch = {}
incRateEpoch = {}
restrictedIncRateEpoch = {}
incVsValEpoch = {}
weekPrediction = {}
sinceSignificant = {}
smoothedSignificant = {}
restrictedSignificant = {}
incRateSignificant = {}
restrictedIncRateSignificant = {}
incVsValSignificant = {}
highestCountries = {}
logBestFit = {}
predict7 = {}
predict30 = {}
images = []


def refreshData():
    # Get data from Johns Hopkins upstream
    if not UPDATE_MODE:
        return
    print("Pulling from upstream/master")
    os.system("git pull upstream master")
    print("Done")


def startAnalysis():
    global images, rawDat, sinceEpoch, smoothedEpoch, restrictedEpoch, incRateEpoch, restrictedIncRateEpoch, incVsValEpoch, weekPrediction, sinceSignificant, smoothedSignificant, restrictedSignificant, incRateSignificant, restrictedIncRateSignificant, incVsValSignificant, highestCountries, logBestFit, predict7, predict30
    # Get the number of cases that every country had on a given day
    rawDat = process.loadInfectionDataFromFile()

    # Get the number of cases of each country from the common point of when the first reportings started
    sinceEpoch = process.daysSinceSurpassing(rawDat, 0)
    # Smooth the data to average out every (SAMPLE_RATE) days
    smoothedEpoch = process.smoothData(sinceEpoch, SAMPLE_RATE)
    # Get the number of cases per day for the last (NUM_DAYS) days
    restrictedEpoch = process.restrictData(smoothedEpoch, NUM_DAYS)
    # Get the percentage increase per day since the start
    incRateEpoch = process.getIncreasePerc(smoothedEpoch)
    # Only get the last (NUM_DAYS) daily increases
    restrictedIncRateEpoch = process.restrictData(incRateEpoch, NUM_DAYS)
    # Get the data plotting the number of new cases vs the total cases up to that point
    incVsValEpoch = process.getIncVsVal(smoothedEpoch)

    # Use the last (NUM_DAYS) infection counts to predictExp the value in 7 days
    weekPrediction = process.predictExp(restrictedEpoch, 7)

    # Get the data for the number of cases since surpassing the minimum significant value
    sinceSignificant = process.daysSinceSurpassing(
        rawDat, MIN_SIGNIFICANT_INFECTIONS)
    # Smooth the above value
    smoothedSignificant = process.smoothData(sinceSignificant, SAMPLE_RATE)
    # Only look at the last 10 days
    restrictedSignificant = process.restrictData(smoothedSignificant, NUM_DAYS)
    incRateSignificant = process.getIncreasePerc(smoothedSignificant)
    restrictedIncRateSignificant = process.restrictData(
        incRateSignificant, NUM_DAYS)
    incVsValSignificant = process.getIncVsVal(smoothedSignificant)

    # Get the data for the current 4 highest countries as well as the world total
    highestCountries = process.getCurrentMax(rawDat, 5)

    # Get the best fit line for the restricted data
    logBestFit = process.getBestFit(process.logY(restrictedEpoch))

    # Get the 7-day predictions
    predict7 = process.getDailyPredictions(sinceSignificant, 7, NUM_DAYS)
    # Get the 30-day predictions
    predict30 = process.getDailyPredictions(sinceSignificant, 30, NUM_DAYS)
    sa_chart = graph.Chart(2, 2, "SA")

    sa_chart.makeScatter(0, 0, smoothedSignificant, SA, "linear", "log", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Number of infections", "Overview")

    sa_chart.makeScatter(0, 1, restrictedSignificant, SA, "linear", "log", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Number of infections", "Last " + str(NUM_DAYS) + " days")

    sa_chart.makeScatter(1, 0, incRateSignificant, SA, "linear", "linear", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Daily growth rate (%)", "Daily growth rate")

    sa_chart.makeScatter(1, 1, incVsValSignificant, SA, "linear", "linear",
                         "Number of infections", "New infections per day", "Increase vs Value")

    uk_chart = graph.Chart(2, 2, "UK")

    uk_chart.makeScatter(0, 0, smoothedSignificant, UK, "linear", "log", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Number of infections", "Overview")

    uk_chart.makeScatter(0, 1, restrictedSignificant, UK, "linear", "log", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Number of infections", "Last " + str(NUM_DAYS) + " days")

    uk_chart.makeScatter(1, 0, incRateSignificant, UK, "linear", "linear", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Daily growth rate (%)", "Daily growth rate")

    uk_chart.makeScatter(1, 1, incVsValSignificant, UK, "linear", "linear",
                         "Number of infections", "New infections per day", "Increase vs Value")

    world_chart = graph.Chart(2, 2, "WORLD")

    world_chart.makeScatter(0, 0, sinceSignificant, highestCountries, "linear",
                            "log", "Days since surpassing " + str(MIN_SIGNIFICANT_INFECTIONS) + " infections", "Number of infections", "Current highest countries")

    world_chart.makeScatter(0, 1, restrictedEpoch, highestCountries, "linear",
                            "log", "Days since epoch", "Number of infections", "Last " + str(NUM_DAYS) + " days")

    world_chart.makeScatter(1, 0, restrictedIncRateEpoch, highestCountries, "linear", "linear",
                            "Days since epoch", "Growth rate (%)", "Daily growth rate")

    world_chart.makeScatter(1, 1, incVsValEpoch, highestCountries, "log", "log",
                            "Number of infections", "New infections per day", "Increase vs Value")

    if DISPLAY_MODE:
        sa_chart.displayImage()
        uk_chart.displayImage()
        world_chart.displayImage()

    saImg = sa_chart.saveImage()
    ukImg = uk_chart.saveImage()
    worldImg = world_chart.saveImage()
    images += [saImg, ukImg, worldImg]

    info = """<section>
<p>
<h2> Executive Summary </h2>

Over the last {:n} days, COVID-19 has been exhibiting a daily growth rate of {:n}%. The {:n} countries with the highest number of infections are:
<ol>
""".format(len(restrictedEpoch["WORLD"]), round(100 * math.exp(logBestFit["WORLD"][1]) - 100, 2), len(highestCountries) - 1)

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

    if "United Kingdom" not in datC and "South Africa" not in datC:
        if rawDat["United Kingdom"][-1][1] > rawDat["South Africa"][-1][1]:
            datC += UK
            datC += SA
        else:
            datC += SA
            datC += UK
    elif "United Kingdom" in datC:
        datC += SA
    elif "South Africa" in datC:
        datC += UK

    for c in datC:
        print(c, weekPrediction[c])
        cnt = rawDat[c][-1][1]
        inc = rawDat[c][-1][1] - rawDat[c][-2][1]
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

    info += "<section>\n"
    info += "<h2> South Africa Analysis</h2>\n"
    info += "<p><img src=\"cid:{0}\"</p>\n".format(saImg)
    info += displayTrend(SA)
    info += "</section>\n"

    info += "<section>\n"
    info += "<h2> United Kingdom Analysis</h2>\n"
    info += "<p><img src=\"cid:{0}\"</p>\n".format(ukImg)
    info += displayTrend(UK)
    info += "</section>\n"

    info += "<section>"
    info += "<h2> World Analysis</h2>\n"
    info += "<p><img src=\"cid:{0}\"</p>\n".format(worldImg)
    info += displayTrend(highestCountries)
    info += "</section>\n"

    share.sendEmail(info, images, not SHARE_MODE)


def displayTrend(c):
    global images
    r = ""
    bestFit = process.getBestFit(process.logY(restrictedSignificant))
    corrCoef = process.corrCoef(process.logY(restrictedSignificant))
    p1 = process.predictExp(sinceSignificant, 7)
    p2 = process.predictExp(sinceSignificant, 30)

    for country in c:
        if len(c) > 1:
            r += "<h3> <u> {}: </u> </h3>\n".format(country)
        func = "<i>y = "
        a = bestFit[country][0]
        b = bestFit[country][1]
        func += str(round(math.exp(a), 4)) + "&#215;"
        func += str(round(math.exp(b), 4)) + "<sup> t </sup> </i>"
        print(country, func)
        r += """
The log-linear graph of infections vs time for the last {:n} days has a best-fit line of <i> y = {:n}x + {:n} </i> with a correlation coefficient
of {:n}. This can be used to predictExp the short-term spread of the virus. In the model, <i> t </i> represents the number of days since epoch (when the first data regarding COVID-19 was reported).

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

""".format(len(restrictedSignificant[country]), round(bestFit[country][1], 4), round(bestFit[country][0], 4), round(corrCoef[country], 3),
            func, round(100 * (math.exp(b) - 1), 2),
           int(restrictedSignificant[country][-1][1]), round(p1[country]), round(p2[country]))

        predDat = {
            "Actual": sinceSignificant[country], "7 Day": predict7[country], "30 Day": predict30[country]}
        predGraph = graph.Chart(1, 1, country + "PREDICTIONS")
        predGraph.makeScatter(0, 0, predDat, ["Actual", "7 Day", "30 Day"], "linear", "log", "Days since surpassing " + str(
            MIN_SIGNIFICANT_INFECTIONS) + " infections", "Number of infections", "Predictions vs actual values")
        predImage = predGraph.saveImage()
        r += "<p><img src=\"cid:{0}\"</p>\n".format(predImage)
        images.append(predImage)
    r += """</p>\n""".format(len(restrictedSignificant[c[0]]))
    return r


if __name__ == "__main__":
    SHARE_MODE = len(sys.argv) > 1 and "s" in sys.argv[1]
    UPDATE_MODE = len(sys.argv) > 1 and "u" in sys.argv[1]
    DISPLAY_MODE = len(sys.argv) > 1 and "d" in sys.argv[1]
    refreshData()
    startAnalysis()
