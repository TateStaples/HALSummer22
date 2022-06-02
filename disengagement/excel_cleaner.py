# takes the originally supplied files and reformat some of dates to be readable by the code

import pandas as pds

# read the original file
data: pds.DataFrame = pds.read_excel("/Users/22staples/PycharmProjects/HALSummer22/data/2021 CA disengagement.xlsx", sheet_name=0)
condensed = [
        "Unanticipated behavior of other cars",
        "Hardware failure",
        "Commission (perception error)",
        "Omission (perception error)",
        "ODD",
        "Trajectory anomaly",
        "Software failure",
        "Unexpected actuation",
        "Precautionary"
    ]

def fix_dates():
    """
    Fixes a typo in some of the data that prevent some of the dates from being properly parsed
    :return: None
    """
    manu = data["Manufacturer"].values
    date_values = data["DATE"].values

    for i in range(len(date_values)):
        if manu[i] == "AIMOTIVE INC.":
            current: str = date_values[i]
            new = current.replace('.', '/', 2)
            new = new.removesuffix('.')
            date_values[i] = new
        elif manu[i] == "EASYMILE":
            current: str = date_values[i]
            new = current.replace("/", '')
            date_values[i] = new

    data["DATE"] = date_values


def write_condensed_causes():
    """
    Reads the long descriptions in column I and converts them into 1 of 9 broader categories.
    It writes the new data into a new column
    :return: None
    """
    causes = data["DESCRIPTION OF FACTS CAUSING DISENGAGEMENT"].values
    map = dict()
    with open("/Users/22staples/PycharmProjects/HALSummer22/disengagement/causes.txt", 'r') as file:
        for line in file:
            id, description = line.split(' - ', 1)
            map[description.strip()] = int(id.strip("?"))
    indices = [map[c.strip().replace("\n", " ")] - 1 for c in causes]
    data["condensed"] = [condensed[i] for i in indices]


if __name__ == '__main__':
    fix_dates()
    write_condensed_causes()
    data.to_excel("/Users/22staples/PycharmProjects/HALSummer22/data/clean 2021 CA disengagement.xlsx", index=False)
