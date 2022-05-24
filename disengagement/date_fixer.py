import pandas as pds

data: pds.DataFrame = pds.read_excel("/Users/22staples/PycharmProjects/HALSummer22/data/2021 CA disengagement.xlsx", sheet_name=0)

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

data.to_excel("/Users/22staples/PycharmProjects/HALSummer22/data/clean 2021 CA disengagement.xlsx", index=False)
if __name__ == '__main__':
    pass
