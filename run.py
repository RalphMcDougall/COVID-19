import os
import sys
import locale
import math
import base64

import graph
import process
import share

locale.setlocale(locale.LC_ALL, "en_ZA")

MIN_SIGNIFICANT_INFECTIONS = 100
SAMPLE_RATE = 1
NUM_DAYS = 10
SHARE_MODE = False
UPDATE_MODE = False
DISPLAY_MODE = False

SA = ["South Africa"]


def refreshData():
    if not UPDATE_MODE:
        return
    print("Pulling from upstream/master")
    os.system("git pull upstream master")
    print("Done")


def startAnalysis():
    rawDat = process.loadInfectionDataFromFile()

    sinceEpoch = process.daysSinceSurpassing(rawDat, 0)
    smoothedEpoch = process.smoothData(sinceEpoch, SAMPLE_RATE)
    restrictedEpoch = process.restrictData(smoothedEpoch, NUM_DAYS)
    incRateEpoch = process.getIncreasePerc(smoothedEpoch)
    restrictedIncRateEpoch = process.restrictData(incRateEpoch, NUM_DAYS)
    incVsValEpoch = process.getIncVsVal(smoothedEpoch)

    sinceSignificant = process.daysSinceSurpassing(
        rawDat, MIN_SIGNIFICANT_INFECTIONS)
    smoothedSignificant = process.smoothData(sinceSignificant, SAMPLE_RATE)
    restrictedSignificant = process.restrictData(smoothedSignificant, NUM_DAYS)
    incRateSignificant = process.getIncreasePerc(smoothedSignificant)
    restrictedIncRateSignificant = process.restrictData(
        incRateSignificant, NUM_DAYS)
    incVsValSignificant = process.getIncVsVal(smoothedSignificant)

    highestCountries = process.getCurrentMax(rawDat, 5)

    sa_chart = graph.Chart(2, 2, "SA")

    sa_chart.makeScatter(0, 0, smoothedSignificant, SA, "linear", "log", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Number of infections", "Infections since start")

    sa_chart.makeScatter(0, 1, restrictedSignificant, SA, "linear", "log", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Num infections", "Infections in last " + str(NUM_DAYS) + " days")

    sa_chart.makeScatter(1, 0, restrictedIncRateSignificant, SA, "linear", "linear", "Days since surpassing " + str(
        MIN_SIGNIFICANT_INFECTIONS) + " infections", "Daily growth rate (%)", "Growth rate for last " + str(NUM_DAYS) + " days")

    sa_chart.makeScatter(1, 1, incVsValSignificant, SA, "linear", "linear",
                         "Number of cases", "Number of new cases per day", "Increase vs Value")

    world_chart = graph.Chart(2, 2, "WORLD")

    world_chart.makeScatter(0, 0, sinceSignificant, highestCountries, "linear",
                            "log", "Days since epoch", "Num infections", "Current highest since surpassing" + str(MIN_SIGNIFICANT_INFECTIONS) + " infections")

    world_chart.makeScatter(0, 1, restrictedEpoch, highestCountries, "linear",
                            "log", "Days since epoch", "Num infections", "Current highest for last " + str(NUM_DAYS) + " days")

    world_chart.makeScatter(1, 0, restrictedIncRateEpoch, highestCountries, "linear", "linear",
                            "Days since epoch", "Growth rate (%)", "Growth rate for last " + str(NUM_DAYS) + " days")

    world_chart.makeScatter(1, 1, incVsValEpoch, highestCountries, "log", "log",
                            "Number of cases", "Number of new cases per day", "Increase vs Value")

    if DISPLAY_MODE:
        sa_chart.displayImage()
        world_chart.displayImage()

    saImg = sa_chart.saveImage()
    print(saImg)
    worldImg = world_chart.saveImage()
    print(saImg, worldImg)
    images = [saImg, worldImg]

    info = ""
    info += "<table border=\"1\">\n"

    info += """<tr>
<th> Country </th>
<th> Infected count </th>
<th> Absolute increase </th>
<th> Percent increase </th>
</tr>
"""
    for c in highestCountries + SA:
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
    info += "</table>\n"

    info += "<br>\n"
    info += "<h2> South Africa Analysis</h2>\n"
    info += "<p><img src=\"cid:{0}\"</p>\n".format(saImg)
    info += "<h2> World Analysis</h2>\n"
    info += "<p><img src=\"cid:{0}\"</p>\n".format(worldImg)

    share.sendEmail(info, images, not SHARE_MODE)


if __name__ == "__main__":
    SHARE_MODE = len(sys.argv) > 1 and "s" in sys.argv[1]
    UPDATE_MODE = len(sys.argv) > 1 and "u" in sys.argv[1]
    DISPLAY_MODE = len(sys.argv) > 1 and "d" in sys.argv[1]
    refreshData()
    startAnalysis()
