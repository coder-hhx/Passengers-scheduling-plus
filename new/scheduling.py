# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project Name: Passengers-scheduling-plus
File Name: scheduling.py
Author: hhx
Contact: houhaixu_email@163.com
Create Date: 2021/2/2
-------------------------------------------------
"""
import math
import numpy as np
from typing import List

from sklearn.cluster import KMeans

from new.data_utils import load_data, push_data
from new.models import Order, Car


def get_distance(order: Order, car: Car):
    """
    计算车与订单位置之间的距离
    :param order: 订单对象
    :param car: 车辆对象
    :return: 距离（米）
    """
    radLat1 = order.lat * math.pi / 180
    radLat2 = car.lat * math.pi / 180
    a = radLat1 - radLat2
    b = (order.lng - car.lng) * math.pi / 180
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
    path = np.zeros((len(dis_list) + 1, car.sites + 1))
    table = np.zeros(car.sites + 1)
    for i in range(1, len(dis_list) + 1):
        for j in range(car.sites, dis_list[i - 1].passenger_num, -1):
            path[i, j] = 0
            if table[j] < (table[j - dis_list[i - 1].passenger_num] + dis_list[i - 1].dis):
                table[j] = table[j - dis_list[i - 1].passenger_num] + dis_list[i - 1].dis
                path[i, j] = 1

    r = []

    i, j = len(dis_list), car.sites
    while i > 0 and j > 0:
        if path[i, j] == 1:
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
    data = np.array([[order.lng, order.lat] for order in order_list])
    k = round(len(data) / 5) + 1
    model1 = KMeans(n_clusters=k, n_init=10)
    model1.fit(data)
    clusters = model1.predict(data)
    centers = model1.cluster_centers_

    the_maps = []
    for index, center in enumerate(centers):
        orders = [order_list[e] for e, i in enumerate(clusters) if i == index]
        the_map = {
            "id": index,
            "coordinate": list(center),
            "orders": orders
        }
        the_maps.append(the_map)
    # the_maps.sort(key=take_coordinate, reverse=True)
    return the_maps


def receive_type_calculate(mode: int):
    """
    接模式下，需计算司机位置
    :param mode: 加载模式
    :return:
    """
    # TODO 使用动态规划之01背包问题算法进行计算
    order_list, car_list, max_distance, _type = load_data(mode=mode)

    result = []  # 计算结果

    for car in car_list:
        dis_list: List[Order] = []  # 所有与该车距离小于最大距离的订单列表
        for order in order_list:
            dis = get_distance(order, car)
            if dis < max_distance and order.unsolved:
                order.dis = max_distance - dis  # 方便一会儿动态规划算法，距离司机最近，等于最大距离-距离司机的距离 最大
                dis_list.append(order)
        result.extend(DP(car, dis_list))

    # for order in order_list:
    #     min_dis = max_distance
    #     min_car = None
    #     for car in car_list:
    #         dis = get_distance(order, car)
    #         if min_dis > dis and car.surplus_sites > order.passenger_num:
    #             min_dis = dis
    #             min_car = car
    #
    #     if min_car:
    #         order.unsolved = False
    #         min_car.change_surplus_sites(order.passenger_num)
    #         result.append((order, min_car))

    push_data(result)

    return result


def send_type_calculate(mode: int):
    """
    送模式下，不需计算司机位置
    :return:
    """

    # TODO 从第一个订单和第一个车找，第一个车找完，再从剩下的订单和剩下的车找，依次类推
    order_list, car_list, max_distance, _type = load_data(mode=mode)


if __name__ == '__main__':
    order_list, car_list, max_distance, _type = load_data(mode=1)

    min_car = car_list[0]

    print(car_list[0].surplus_sites)

    min_car.change_surplus_sites(1)

    print(car_list[0].surplus_sites)
