# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project Name: Passengers-scheduling-plus
File Name: caculate_utils.py
Author: hhx
Contact: houhaixu_email@163.com
Create Date: 2021/2/3
-------------------------------------------------
"""
import math
from typing import List

import numpy as np
from sklearn.cluster import KMeans

from new.data_utils import load_data
from new.models import Order, Car


def get_distance(lng1, lat1, lng2, lat2):
    """
    计算车与订单位置之间的距离
    :param order: 订单对象
    :param car: 车辆对象
    :return: 距离（米）
    """
    radLat1 = lat1 * math.pi / 180
    radLat2 = lat2 * math.pi / 180
    a = radLat1 - radLat2
    b = (lng1 - lng2) * math.pi / 180
    s = 2 * math.asin(
        math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(math.sin(b / 2), 2)))
    s = s * 6378.137
    s = math.ceil(s * 10000) / 10
    return s


def DP(car: Car, dis_list: List[Order]):
    """
    动态规划，参考背包问题
    :param car: 要分配的车
    :param dis_list: 可被分配的订单列表
    :return:
    """
    path = np.zeros((len(dis_list) + 1, car.surplus_sites + 1))
    table = np.zeros(car.surplus_sites + 1)
    if len(dis_list) == 1:  # 若只有一个订单，则直接分配给该车
        r = []
        car.change_surplus_sites(dis_list[0].passenger_num)
        dis_list[0].unsolved = False
        r.append((dis_list[0], car))
    else:
        for i in range(1, len(dis_list) + 1):
            for j in range(car.surplus_sites, dis_list[i - 1].passenger_num - 1, -1):
                path[i, j] = 0
                if table[j] < (table[j - dis_list[i - 1].passenger_num] + dis_list[i - 1].dis):
                    table[j] = table[j - dis_list[i - 1].passenger_num] + dis_list[i - 1].dis
                    path[i, j] = 1

        r = []

        i, j = len(dis_list), car.surplus_sites
        while i > 0 and j > 0:
            if path[i, j] == 1:
                car.change_surplus_sites(dis_list[i - 1].passenger_num)
                dis_list[i - 1].unsolved = False
                r.append((dis_list[i - 1], car))
                j -= dis_list[i - 1].passenger_num
            i -= 1
    return r


def k_means(order_list: List[Order]):
    """
    聚类
    :param order_list:
    :return:
    """
    ol = []  # 未分配车辆的订单列表
    for order in order_list:
        if order.unsolved:
            ol.append(order)
    data = np.array([[order.lng, order.lat] for order in ol])
    k = round(len(data) / 5) + 1
    model1 = KMeans(n_clusters=k, n_init=10)
    model1.fit(data)
    clusters = model1.predict(data)
    centers = model1.cluster_centers_

    the_maps = []
    lng = lat = count = 0
    for index, center in enumerate(centers):
        orders = [order_list[e] for e, i in enumerate(clusters) if i == index]
        the_map = {
            "id": index,
            "coordinate": list(center),
            "orders": orders
        }
        lng += list(center)[0]
        lat += list(center)[1]
        count += 1
        the_maps.append(the_map)

    aver_lng = lng / count
    aver_lat = lat / count
    the_maps.sort(key=lambda elem: get_distance(aver_lng, aver_lat, elem["coordinate"][0], elem["coordinate"][1]),
                  reverse=True)
    return the_maps


def find_closest_obj(point, data):
    """
    寻找距离point最近的一个点
    :param point:
    :param data:
    :return:
    """
    distances = [get_distance(point['coordinate'][0], point['coordinate'][1], obj_.lng, obj_.lat) for obj_ in data]
    closest_obj = data[distances.index(min(distances))]
    return closest_obj


if __name__ == '__main__':
    order_list, car_list, max_distance, _type = load_data(mode=1)

    maps = k_means(order_list)

    center = maps.pop(0)

    closest_car = find_closest_obj(center, car_list)

    # print(type(closest_car))
