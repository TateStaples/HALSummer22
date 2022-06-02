import pandas as pds
from matplotlib import pyplot as plt
import parser


# thing for making graphs to search for outliers
# no missing data

"""
Graphs to make:
manu v output - relative freq bar
manu v cause - stacked bar
date v output - hist of proportions
cause v output - bar
overall ratios
"""


class Incident:
    _all = list()

    def __init__(self, row: tuple):
        self.manu, self.date, self.location, self.road_number, self.condensed, self.av_disengage = row
        Incident._all.append(self)
        self.line = len(Incident._all) + 1

    @staticmethod
    def matching(predicate):
        return list(filter(predicate, Incident._all))


def freq_bar(x_categories: list, y_categories: list, x_label:str, y_label:str, proportion=False):
    fig, ax = plt.subplots()
    unique_x = list(set(x_categories))
    unique_y = list(set(y_categories))

    matches = [[0] * len(unique_x) for i in range(len(unique_y))]
    totals = [0] * len(unique_x)

    for x_, y_ in zip(x_categories, y_categories):
        i_x = unique_x.index(x_)
        i_y = unique_y.index(y_)
        matches[i_y][i_x] += 1
        totals[i_x] += 1

    small_label = [s[:4] for s in unique_x]
    for i, y_ in enumerate(unique_y):
        if proportion:
            ax.bar(small_label, [m/t for m, t in zip(matches[i], totals)], label=y_)
        else:
            ax.bar(small_label, matches[i], label=y_)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


def bar(x, sucess, x_label:str, y_label:str, proportion=False):
    uniques = list(set(x))
    matches = [0] * len(uniques)
    totals = [0] * len(uniques)
    for x_, s_ in zip(x, sucess):
        i = uniques.index(x_)
        if s_:
            matches[i] += 1
        totals[i] += 1
    print(matches)
    print(totals)
    small_label = [s[:5] for s in uniques]
    heights = [m/t for m, t in zip(matches, totals)]  if proportion else matches

    if len(small_label) > 15:
        sorted_labels = sorted(small_label, key=lambda x: heights[small_label.index(x)], reverse=True)[:10]
        sorted_h = sorted(heights, reverse=True)[:10]
        plt.bar(sorted_labels, sorted_h, width=0.5)
    else:
        plt.bar(small_label, heights, width=0.5)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


data: pds.DataFrame = parser.data#pds.read_excel("/Users/22staples/PycharmProjects/HALSummer22/data/clean 2021 CA disengagement.xlsx", sheet_name=0, parse_dates=["DATE"])
manufacturer_data = data["Manufacturer"].values
location_data = data["DISENGAGEMENT\nLOCATION\n(Interstate, Freeway, Highway, Rural Road, Street, or Parking Facility)"].values
output = parser.output#data["output"].values
cond = data["condensed"].values
proportional = True
incidents = [Incident(row) for row in zip(manufacturer_data, data["DATE"].values, location_data, parser.location_encoding, cond, output)]

# outliers in the data
# todo: check the ommisions caught by the av - lines [1030, 1034]: Perception discrepancy; On city road in moderate traffic with light rain during day -> only perception errors caught by av
# todo: check the apple that caught the traj error - line 125: Incorrect prediction led to undesirable motion plan -> only time Apple caught trajectory error
if __name__ == '__main__':
    # print(len(Incident.matching(lambda i: i.condensed == "ODD" and i.av_disengage == 0)))
    # bar(manufacturer_data, output, "manu", "out", proportion=proportional)
    # freq_bar(manufacturer_data, cond, "manu", "cond", proportion=proportional)
    # freq_bar(cond, manufacturer_data, "manu", "cond", proportion=proportional)
    # bar(cond, output, "cond", "out", proportion=proportional)

    # traj = Incident.matching(lambda i: i.condensed == "Trajectory anomaly")
    # bar([i.manu for i in traj], [i.av_disengage for i in traj], "man", "out", proportion=True)

    # om = Incident.matching(lambda i: i.condensed == "Omission (perception error)" and i.av_disengage)
    # print([o.line for o in om])

    traj = Incident.matching(lambda i: i.condensed == "Trajectory anomaly" and i.manu == "APPLE INC." and i.av_disengage)
    print([i.line for i in traj])
