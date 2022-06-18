import pandas as pds
from matplotlib import pyplot as plt
import parser


# thing for making graphs to search for outliers and make category bar charts
# no missing data

"""
Graphs to make:
manu v output - relative freq bar
manu v cause - stacked bar
date v output - hist of proportions
cause v output - bar
overall ratios
"""


def list_to_dict(l: list) -> dict:
    """
    Convert list of items into map of item->count
    :param l: list of items
    :return: dictionary with set of items as keys and # of occurrences as the output
    """
    out = dict()
    for item in l:
        if item in out: out[item] += 1
        else: out[item] = 1
    return out


class Incident:
    """
    Stores all info from row in spreadsheet
    """
    _all = list()

    def __init__(self, row: tuple):
        self.manu, self.date, self.location, self.road_number, self.condensed, self.av_disengage = row
        Incident._all.append(self)
        self.line = len(Incident._all) + 1

    @staticmethod
    def matching(predicate):
        """
        Allow for filtering through the incidents
        :param predicate: lambda function that takes an incident and returns true/false on whether it should be return
        :return: list of values matching values
        """
        return list(filter(predicate, Incident._all))


# sorts bar data based of different categories
def sort_largest(categories, matches, totals):return list(zip(*sorted(list(zip(categories, matches, totals)), key=lambda tup: tup[2])))  # sorts most samples to least
def sort_matches(categories, matches, totals):return list(zip(*sorted(list(zip(categories, matches, totals)), key=lambda tup: tup[1])))  # sorts by most av disengage
def sort_alphabetical(categories, matches, totals): return list(zip(*sorted(list(zip(categories, matches, totals)), key=lambda tup: tup[0])))  # sorts by category name
def sort_month(categories, matches, totals):return list(zip(*sorted(list(zip(categories, matches, totals)),key=lambda tup: int(tup[0][-2:]), reverse=True)))  # sorts month


def two_var_bar(x_categories: list, y_categories: list, x_label:str, y_label:str, proportion=False):
    """
    Creates stacked bar chart for how often each y happens for each x
    :param x_categories: the list of categories on x-axis
    :param y_categories: the sub categories to show in each bar chart
    :param x_label: what to label the x-axis
    :param y_label: what to label the y-axis
    :param proportion: False-> chart # of occurrence, True->chart % of occurrence
    :return:
    """
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
            ax.barh(small_label, [m/t for m, t in zip(matches[i], totals)], label=y_)
        else:
            ax.barh(small_label, matches[i], label=y_)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


def bar(title: str, x: list, sucess: list, sorter=sort_largest, proportion=False):
    """
    Creates a bar chart of how often category. Shows and saves it.
    :param title:
    :param x: list of categorical variable
    :param sucess: list paired with x if that datum was cancelled by the av (bool_
    :param sorter: method for sorting the bars. Defaults to sorting by # of occurences
    :param proportion: True->chart % av disengage, False->chart # of av disengage
    :return:
    """
    fig, ax = plt.subplots()
    uniques = list(set(x))
    matches = [0] * len(uniques)
    totals = [0] * len(uniques)
    for x_, s_ in zip(x, sucess):
        i = uniques.index(x_)
        if s_:
            matches[i] += 1
        totals[i] += 1
    small_label = [s.split()[0][:8] for s in uniques]
    heights = [m/t for m, t in zip(matches, totals)]  if proportion else matches
    s_labels, s_matches, s_totals = sorter(small_label, heights, totals)
    if not proportion:
        bar2 = ax.barh(s_labels, [t-m for m, t in zip(s_matches, s_totals)], label="human")
    bars = ax.barh(s_labels, s_matches, label="av")
    if proportion:
        ax.bar_label(bars, labels=[f"{round(x*100, 2)}%" for x in s_matches])
    ax.legend()
    plt.title(title)

    plt.savefig('imgs/' + title.replace(' ', '_') + '.png', format='png')
    plt.show()


def hist(title: str, x: list, proportion=False):
    """
    Creates a histogram with the counts of a collection of categories
    :param title: what to save the plot as
    :param x: column of categorical variables
    :param proportion: absolute or relative freq
    :return:
    """
    fig, ax = plt.subplots()
    counts = list_to_dict(x)
    item = sorted(counts.keys(), key=lambda x: counts[x])
    small_label = [s.split()[0][:8] for s in item]
    heights = [counts[i] for i in item]
    ax.barh(small_label, heights)
    plt.title(title)

    plt.savefig('imgs/' + title.replace(' ', '_') + '.png', format='png')
    plt.show()


# load the data
data: pds.DataFrame = parser.data
manufacturer_data = data["Manufacturer"].values
location_data = [v.upper() for v in data["DISENGAGEMENT\nLOCATION\n(Interstate, Freeway, Highway, Rural Road, Street, or Parking Facility)"].values]
output = parser.output
cond = data["Fcondensed"].values
proportional = False
incidents = [Incident(row) for row in zip(manufacturer_data, data["DATE"].values, location_data, parser.location_encoding, cond, output)]
"""
outliers in the data
check the ommisions caught by the av - lines [1030, 1034]:
  Perception discrepancy; On city road in moderate traffic with light rain during day -> only perception errors caught by av
check the apple that caught the traj error - line 125:
  Incorrect prediction led to undesirable motion plan -> only time Apple caught trajectory error
waymo had one human caught software bug - lines [2456, 2577]:
  Disengage for a software discrepancy for which our vehicle's diagnostics received a message indicating a potential performance issue with a software component -> interestingly same description the next day and auto disengage
mercedes had one human caught software bug: line 1061
  A general error caused the system to stop the engaged status. Vehicle not in an active construction zone. No emergency vehicles or collisions present in the vicinity. Weather and/or road conditions dry in the area. -> notably only datum in section disengaged by 'Driver' instead of 'Test Driver'
easymile has a lot of unexpected activations and commissions
check why mercedes is catching much more traj than everyone else
"""
if __name__ == '__main__':

    ### histograms
    # manufacturer
    bar("disengagement by manufacturer", manufacturer_data, output, proportion=proportional)
    hist("disengagement count by manufacturer", manufacturer_data)
    # date
    bar("disengagement by months since 2020", [f"Month-{int(d)}" for d in parser.date_encoding], output, sorter=sort_month, proportion=proportional)
    plt.hist(parser.date_encoding)
    plt.title("disengagement count by month")
    plt.savefig('imgs/' + "disengagement count by month".replace(' ', '_') + '.png', format='png')
    plt.boxplot(parser.date_encoding)
    plt.savefig('imgs/' + "disengagement dist by month".replace(' ', '_') + '.png', format='png')
    # road type
    bar("disengagement by road type", location_data, output, proportion=proportional)
    hist("road type counts", location_data)
    # condensed causes
    bar("disengagement by cause", cond, output, proportion=proportional)
    hist("cause counts", cond)

    # target variables
    hist("output counts", ["av" if o else "human" for o in output])

    # auto capable
    hist("auto capable counts", ["auto capable" if a else "autoless" for a in parser.auto_encoding])

    # raw cause
    raw_causes = data["DESCRIPTION OF FACTS CAUSING DISENGAGEMENT"].values
    raw_set = list(set(raw_causes))
    hist("raw cause counts", [str(raw_set.index(c)) for c in raw_causes])

    # driver present
    hist("driver present counts", [d.upper() for d in data["DRIVER PRESENT\n(Yes or No)"].values])


    # print(len(Incident.matching(lambda i: i.condensed == "ODD" and i.av_disengage == 0)))
    # bar(manufacturer_data, output, "manu", "out", proportion=proportional)
    # freq_bar(manufacturer_data, cond, "manu", "cond", proportion=proportional)
    # freq_bar(cond, manufacturer_data, "manu", "cond", proportion=proportional)
    # bar(cond, output, "cond", "out", proportion=proportional)

    # traj = Incident.matching(lambda i: i.condensed == "Trajectory anomaly")
    # bar([i.manu for i in traj], [i.av_disengage for i in traj], "man", "out", proportion=True)

    # om = Incident.matching(lambda i: i.condensed == "Omission (perception error)" and i.av_disengage)
    # print([o.line for o in om])

    # traj = Incident.matching(lambda i: i.condensed == "Trajectory anomaly" and i.manu == "APPLE INC." and i.av_disengage)
    # print([i.line for i in traj])

    # for manu in list(set(manufacturer_data)):
    #     stuff = Incident.matching(lambda i: i.manu == manu)
    #     bar([i.condensed for i in stuff], [i.av_disengage for i in stuff], "condition", manu, proportion=False)

    # x = Incident.matching(lambda i: "WAYMO LLC" == i.manu and not i.av_disengage and i.condensed == "Software failure")
    # print([i.line for i in x])

    # x = Incident.matching(
    #     lambda i: "mercedes" in i.manu.lower() and not i.av_disengage and i.condensed == "Software failure")
    # print([i.line for i in x])