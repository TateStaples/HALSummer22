import openpyxl
import os
import json


def get_data(path):
    result_jsons = sorted(os.listdir(path))
    result_data = list()
    for r in result_jsons:
        file = json.load(open(r))
        r = r.removesuffix(".json")
        c, i = r.split('_')
        tv, ctv = c.split('-')
        # 1-3 = tv %, ctv %, id
        result = [int(tv), int(ctv), int(i)]

        # cars
        # 4-9
        for car_id in range(4):
            car_data = list()
            for datum in ("numCarsVT", "avgDelayTimesVT"):
                car_data.append(file[datum][car_id])
            result.extend(car_data)

        # routes
        # 10-28
        for i in range(3):  # for each of tbe 3 routes
            route_data = list()
            # go through each of the data points
            for datum in ("routePercentageTV", "routePercentageCTV", "routeAvgDelayTimes", "routeMaxDelayTimes", "routeLevelOfImpacts"):
                route_data.append(file[datum][i])
            route_data.append(hash(file["routes"][i])) # way to look for unique paths
            result.extend(route_data)
        """
        Missing data:
        - delaytimes (for each car)
        - routePercentageCAV
        - peakCongestionPeriods
        """
        result_data.append(result)
    return result_data


def main():
    path = os.getcwd() + "/results"
    result_data = get_data(path)
    wb = openpyxl.Workbook()
    sheet = wb.create_sheet("Data")
    for r in result_data:
        sheet.append(r)
    wb.save(f"{path}/data.xlsx")


if __name__ == '__main__':
    main()
