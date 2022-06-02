# Decision Tree on CA Disengagment
# started May 24, 2022
# Tate Staples

# Reads the disengagement data, converts it into numerical encoding, and saves to encoded.xlsx

import pandas as pds
import numpy as np


data: pds.DataFrame = pds.read_excel("data/clean 2021 CA disengagement.xlsx", sheet_name=0, parse_dates=["DATE"])
makers = list(set(data["Manufacturer"]))


def debug():
    """
    debugs what values we have.
    Was using this when I was trying to figure out how these things work
    :return:
    """
    disengagements = set(data["DISENGAGEMENT INITIATED BY\n(AV System, Test Driver, Remote Operator, or Passenger)"]) # remote and passenger aren't in the data
    locations = set(data["DISENGAGEMENT\nLOCATION\n(Interstate, Freeway, Highway, Rural Road, Street, or Parking Facility)"])
    descriptions = list(set(data["DESCRIPTION OF FACTS CAUSING DISENGAGEMENT"]))
    auto = set(data['VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)'])
    driver = set(data['DRIVER PRESENT\n(Yes or No)'])
    print(f"{makers=}") # {'TOYOTA RESEARCH INSTITUTE, INC.', 'ZOOX, INC', 'GATIK AI INC.', 'NURO, INC', 'MERCEDES-BENZ RESEARCH & DEVELOPMENT NORTH AMERICA, INC.', 'ARGO AI, LLC', 'AIMOTIVE INC.', 'NISSAN NORTH AMERICA, INC DBA ALLIANCE INNOVATION LAB', 'AUTOX TECHNOLOGIES, INC', 'LYFT', 'UDELV, INC.', 'APOLLO AUTONOMOUS DRIVING USA LLC', 'NVIDIA', 'APPLE INC.', 'WERIDE CORP', 'DIDI RESEARCH AMERICA LLC', 'PONY.AI, INC.', 'DEEPROUTE.AI', 'VALEO NORTH AMERICA INC.', 'AURORA OPERATIONS, INC.', 'WAYMO LLC', 'EASYMILE', 'CRUISE LLC', 'QUALCOMM TECHNOLOGIES, INC.', 'QCRAFT INC.'}
    print(f"{len(makers)}") # 25
    print(f"{disengagements=}") # {'Operator', 'AV System - Emergency Stop', 'Test Drive', 'Test Driver - Soft Stop', 'Driver', 'Software', 'Test Driver', 'AV System'}
    print(f"{locations=}") #{'freeway', 'Street', 'Highway', 'STREET', 'HIGHWAY', 'street', 'Freeway', 'Parking Facility'}
    print(f"{len(descriptions)}")
    print(data['VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)'].sort_values().tail(100))
'''
Data Types - how each section is being encoded:
- Manufacturer: Categorical - categorical
- date: numeric - either days since 2021 or whatever SGO align has
- auto capable: boolean - 1/0 (only true for udelv, inc)
- driver: boolean - 1/0 (data irrelevant because output always yes)
- disengagement: boolean - 1/0 **(output)**
- location: categorical - potential slight numeric by speed
- description: categorical
'''
### ----- embedding section ----- ###
def one_hot_encode(values):
    """
    Takes a list of categorial variables and embeds it into a binary system that the tree can split
    description: https://www.educative.io/blog/one-hot-encoding
    :param values: all the catergorical variables
    :return:
    """
    uniques = list(set(values))
    encoding = list(list() for _ in range(len(uniques)))
    for datum in values:
        insertion = uniques.index(datum)
        for i, l in enumerate(encoding):
            l.append(1 if i == insertion else 0)
    return encoding

## Manufacturer
manu_encoding = one_hot_encode(data["Manufacturer"].values)

## dates
base = np.datetime64("2020-01-01")
date_encoding = [pds.to_timedelta(time - base).days / 30 for time in data["DATE"].values]

## location encoding
# note: rural road is nowhere in the dataset
location_indices = ("interstate", "freeway", "highway", "rural road", "street", "parking facility")
location_encoding = [location_indices.index(loc.lower()) for loc in data["DISENGAGEMENT\nLOCATION\n(Interstate, Freeway, Highway, Rural Road, Street, or Parking Facility)"].values]

## auto capable
auto_encoding = [0 if "no" == datum.lower() else 1 for datum in data['VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)'].values]

## output - operator/comp
output = [1 if "AV" in datum or datum == "Software" else 0 for datum in data["DISENGAGEMENT INITIATED BY\n(AV System, Test Driver, Remote Operator, or Passenger)"].values]

## cause
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
def condesed_causes(causes):
    """
    Converts the 340 descriptions in column I into the 14 unique categories
    :param causes: the I column long desciptions
    :return: condensed cause ids
    """
    map = dict()
    with open("disengagement/causes.txt", 'r') as file:
        for line in file:
            id, description = line.split(' - ', 1)
            map[description.strip()] = int(id.strip("?"))
    return [map[c.strip().replace("\n", " ")] for c in causes]
new_causes = condesed_causes(data["DESCRIPTION OF FACTS CAUSING DISENGAGEMENT"].values)
print(set(new_causes))
cause_encoding = one_hot_encode(new_causes)
print(len(cause_encoding))


# store formatted data into the recording
storage = pds.DataFrame()
for i in range(len(manu_encoding)): storage[makers[i]] = manu_encoding[i]  # manufacturer
storage['date'] = date_encoding  # days after 2020
storage["road"] = location_encoding
storage["auto capable"] = auto_encoding
for i in range(len(cause_encoding)): storage[condensed[i]] = cause_encoding[i]
storage["output"] = output

storage.to_excel("disengagement/encoded.xlsx", index=False)
