# Decision Tree on CA Disengagment
# started May 24, 2022
# Tate Staples

# Reads the disengagement data, converts it into numerical encoding, and saves to encoded.xlsx

import pandas as pds
import numpy as np
from excel_cleaner import condensed

path = "/Users/22staples/PycharmProjects/HALSummer22/data/F_CleanData1.xlsx"
data: pds.DataFrame = pds.read_excel(path, sheet_name="Mature")
data: pds.DataFrame = data.iloc[:, 1:7]


'''
Data Types - how each section is being encoded:
- Manufacturer: Categorical - categorical
- date: numeric - months since 2020 or whatever SGO align has
- disengagement: boolean - 1/0 **(output)**
- location: boolean - limited (street) or unlimited (highway)
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
date_encoding = data["Months after 2020"].values

## location encoding
location_encoding = [1 if d == "STREET" else 0 for d in data["location"].values]

## auto capable
# auto_encoding = [0 if "no" == datum.lower() else 1 for datum in data['VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)'].values]
# capable = ('QCRAFT INC.', 'GATIK AI INC.', 'VALEO NORTH AMERICA INC.', 'AURORA OPERATIONS, INC.', 'EASYMILE', 'APPLE INC.', 'MERCEDES-BENZ RESEARCH & DEVELOPMENT NORTH AMERICA, INC.', 'WAYMO LLC')
# auto_encoding = [manu in capable for manu in data["Manufacturer"].values]

## output - operator/comp
output = [1 if datum else 0 for datum in data["av disengage"].values]

## cause
cause_encoding = one_hot_encode(data["condensed"].values)

if __name__ == '__main__':
    # store formatted data into the recording
    storage = pds.DataFrame()
    makers = list(set(data["Manufacturer"].values))
    for i in range(len(manu_encoding)): storage[makers[i]] = manu_encoding[i]  # manufacturer
    storage['date'] = date_encoding  # days after 2020
    storage["limited road"] = location_encoding
    # storage["auto capable"] = auto_encoding
    condensed = list(set(data["condensed"].values))
    for i in range(len(cause_encoding)): storage[condensed[i]] = cause_encoding[i]
    storage["output"] = output
    storage.to_excel("disengagement/encoded.xlsx", index=False)
