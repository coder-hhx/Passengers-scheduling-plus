# 计算库

import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from itertools import combinations
import math


def geodesic(a, b):
    """
    测地线, 计算两点间距

    参数
    ----------
    a : a点
    b : b点

    返回
    ----------
    value : 两点间距
    """
    if isinstance(a, dict):
        a = a["coordinate"]
        b = b["coordinate"]
    return math.hypot(a[0] - b[0], a[1] - b[1])


def take_coordinate(elem):
    """
    从外至内选点
    """
    center = [104.075, 30.675][::-1]
    elem = elem["coordinate"][::-1]
    distance = geodesic(center, elem)
    return distance


# @profile
def kmeans(data):
    """
    用Kmeans计算乘客的聚类中心点

    参数
    ----------
    data : 乘客数据

    返回
    ----------
    the_maps : 乘客的聚类中心点
    """
    users_data = data
    data = np.array([i["coordinate"] for i in data])
    k = round(len(data) / 5) + 1
    model1 = KMeans(n_clusters=k, n_init=10)
    model1.fit(data)
    clusters = model1.predict(data)
    centers = model1.cluster_centers_
    the_maps = []
    for index, center in enumerate(centers):
        users = [users_data[e] for e, i in enumerate(clusters) if i == index]
        the_map = {
            "id": index,
            "coordinate": list(center),
            "users": users
        }
        the_maps.append(the_map)
    the_maps.sort(key=take_coordinate, reverse=True)
    return the_maps


# @profile
def find_closest_point(point, data):
    """
    寻找距离point最近的一个点

    参数
    ----------
    point : point点
    data : 被寻找的点的集合

    返回
    ----------
    value : 距离point最近的点
    """
    point = list(point)[::-1]
    data = [list(i)[::-1] for i in data]
    distances = [geodesic(point, i) for i in data]
    closest_point = data[distances.index(min(distances))]
    closest_point = closest_point[::-1]
    return closest_point


def find_closest_obj(point, data):
    """
    寻找距离point最近的一个点, 返回其对象

    参数
    ----------
    point : point点
    data : 被寻找的点的集合

    返回
    ----------
    value : 距离point最近的点的对象
    """
    point_coordinate = point["coordinate"]
    data_coordiantes = [i["coordinate"] for i in data]
    closest_point_coordinate = find_closest_point(point_coordinate, data_coordiantes)
    return data[data_coordiantes.index(closest_point_coordinate)]


# @profile
def mean_square_difference(data):
    """
    计算点的均方差

    参数
    ----------
    data : 点的集合

    返回
    ----------
    value : 点的均方差
    """
    data = [i["coordinate"] for i in data]
    data = combinations(data, 2)
    data = [geodesic(i[0], i[1]) for i in data]
    if len(data) == 1:
        return data[0] * data[0]
    elif len(data) == 0:
        return 0
    else:
        return sum([i * i for i in data]) / len(data)
