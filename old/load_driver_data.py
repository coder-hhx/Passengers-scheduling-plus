# 载入司机数据

from old.coordinates_generator import random_coordinates_generator, matrix_coordinates_generator
import random


def load_driver_data():
    """
    载入司机数据
    """
    coordinates = random_coordinates_generator(25)
    drivers = []
    for e, i in enumerate(coordinates):
        driver = {
            "driver_id": e,
            "coordinate": i,
            # "order" : e,
            "sites": random.choice([4, 6])
        }
        drivers.append(driver)
    return drivers


def load_matrix_drivers(users):
    """
    载入矩阵司机数据
    """
    users = [i["coordinate"] for i in users]
    x, y = zip(*users)
    xRange = max(x), min(x)
    yRange = max(y), min(y)

    coordinates = matrix_coordinates_generator(xRange, yRange)
    drivers_dict = {}
    for site in [4, 6]:
        drivers = []
        for e, i in enumerate(coordinates):
            driver = {
                "id": len(coordinates) + e,
                "coordinate": i,
                # "order" : e,
                "sites": site
            }
            drivers.append(driver)
        drivers_dict[site] = drivers
    return drivers_dict
