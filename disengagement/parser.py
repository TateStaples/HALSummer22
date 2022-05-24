## Decision Tree on CA Disengagment
## started May 24, 2022
## Tate Staples

# description
'''
I want you to develop a decision tree that predicts whether a human (called driver, test driver, operator)
disengaged or the AV software disengaged (called AV system/software),
and how the various features (like company, day, location) contributed to this.
You will not need permit number.
You goal is to develop a decision tree visualization like the one here: http://hal.pratt.duke.edu/sites/hal.pratt.duke.edu/files/u35/HAL2019_1.pdf

Your next big step will be translating column I into column J, which we will call "Contributing Factors". You need to figure out how to classify the events in 20 or fewer categories. You could use behaviors like lane drift, improper merge, too slow...or something else.  Then you need to develop clear rules for how you decided which case goes into which category.

This is the most painful part but also the most important! If you are struggling or have questions, let me know and we can jump on zoom.
'''

# dataset size = 2605
# categories = manufacture, permit #, date, vin number, auto capable, driver, disengager, location, description
## todo: what is column I and J (contact missy)
## todo: should I use description data (probably not - 323 categories)
import pandas as pd
import pandas as pds
import sklearn.tree as sk
import numpy as np

# load sheet
from numpy import datetime64

data: pds.DataFrame = pds.read_excel("data/clean 2021 CA disengagement.xlsx", sheet_name=0, parse_dates=["DATE"])
print(data.dtypes)
makers = list(set(data["Manufacturer"]))
# permits = set(data["Permit Number"])  # this is the same info as the manufacture just in different format
disengagements = set(data["DISENGAGEMENT INITIATED BY\n(AV System, Test Driver, Remote Operator, or Passenger)"]) # remote and passenger aren't in the data
locations = set(data["DISENGAGEMENT\nLOCATION\n(Interstate, Freeway, Highway, Rural Road, Street, or Parking Facility)"])
descriptions = set(data["DESCRIPTION OF FACTS CAUSING DISENGAGEMENT"])
print(f"{makers=}") # {'TOYOTA RESEARCH INSTITUTE, INC.', 'ZOOX, INC', 'GATIK AI INC.', 'NURO, INC', 'MERCEDES-BENZ RESEARCH & DEVELOPMENT NORTH AMERICA, INC.', 'ARGO AI, LLC', 'AIMOTIVE INC.', 'NISSAN NORTH AMERICA, INC DBA ALLIANCE INNOVATION LAB', 'AUTOX TECHNOLOGIES, INC', 'LYFT', 'UDELV, INC.', 'APOLLO AUTONOMOUS DRIVING USA LLC', 'NVIDIA', 'APPLE INC.', 'WERIDE CORP', 'DIDI RESEARCH AMERICA LLC', 'PONY.AI, INC.', 'DEEPROUTE.AI', 'VALEO NORTH AMERICA INC.', 'AURORA OPERATIONS, INC.', 'WAYMO LLC', 'EASYMILE', 'CRUISE LLC', 'QUALCOMM TECHNOLOGIES, INC.', 'QCRAFT INC.'}
print(f"{len(makers)}") # 25
print(f"{disengagements=}") # {'Operator', 'AV System - Emergency Stop', 'Test Drive', 'Test Driver - Soft Stop', 'Driver', 'Software', 'Test Driver', 'AV System'}
print(f"{locations=}") #{'freeway', 'Street', 'Highway', 'STREET', 'HIGHWAY', 'street', 'Freeway', 'Parking Facility'}
print(f"{len(descriptions)}")
auto = set(data['VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)'])
driver = set(data['DRIVER PRESENT\n(Yes or No)'])
print(f"{auto=}")
print(f"{driver=}")
print(data['VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)'].sort_values().tail(100))


### ----- format ----- ###
'''
Data Types:
- Manufacturer: Categorical - no real numeric value (maybe sorted by auto capable?)
- date: numeric - either days since 2021 or whatever SGO align has
- auto capable: boolean - 1/0 (only true for udelv, inc)
- driver: boolean - 1/0 (data irrelevant because output always yes)
- disengagement: boolean - 1/0 **(output)**
- location: categorical - potential slight numeric by speed
'''

# one hot encoding of manufactures # todo: unit test
def one_hot_encode(values):
    uniques = list(set(values))
    encoding = list(list() for _ in range(len(uniques)))
    for datum in values:
        insertion = uniques.index(datum)
        for i, l in enumerate(encoding):
            l.append(1 if i == insertion else 0)
    return encoding


manu_encoding = one_hot_encode(data["Manufacturer"].values)
## todo: figure out dates. (what is sgo align)
# base: datetime64 = pd.Timestamp.year
base = np.datetime64("2020-01-01")
date_encoding = [pd.to_timedelta(time - base).days for time in data["DATE"].values]  ## FIXME - contact missy about this

## location encoding
# note: rural road is nowhere in the dataset
location_indices = ("interstate", "freeway", "highway", "rural road", "street", "parking facility")
location_encoding = [location_indices.index(loc.lower()) for loc in data["DISENGAGEMENT\nLOCATION\n(Interstate, Freeway, Highway, Rural Road, Street, or Parking Facility)"].values]

##  auto capable
auto_encoding = [0 if "no" == datum.lower() else 1 for datum in data['VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)'].values]

## output - operator/comp
# op: Test Driver, Test Drive, Test Driver - Soft Stop, Operator, Driver
# comp: AV System - Emergency Stop, AV System, Software
output = [1 if "AV" in datum or datum == "Software" else 0 for datum in data["DISENGAGEMENT INITIATED BY\n(AV System, Test Driver, Remote Operator, or Passenger)"].values]

# store formatted data
storage = pds.DataFrame()
for i in range(len(makers)): storage[makers[i]] = manu_encoding[i]  # manufacturer
storage['date'] = date_encoding  # days after 2020
storage["road"] = location_encoding
storage["auto capable"] = auto_encoding
storage["output"] = output

storage.to_excel("disengagement/encoded.xlsx", index=False)