import graph
import process


def startAnalysis():
    data = process.DataStore()
    chart1 = graph.Chart(3, 2)

    chart1.makeScatter(0, 0, data, [
                       "South Africa"], "linear", "log", "Days", "Number of infections", "")
    chart1.displayImage()


if __name__ == "__main__":
    startAnalysis()
