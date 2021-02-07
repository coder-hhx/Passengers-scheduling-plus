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

from new.BiKmeans import biKmeans
from new.data_utils import load_data
from new.models import Order, Car


def has_solved_orders(orders):
    """
    判断是否有分配的订单
    :param orders:
    :return:
    """
    for order in orders:
        if not order.unsolved:
            return True
    return False


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
    r = []
    if len(dis_list) == 1:  # 若只有一个订单，则直接分配给该车
        if car.surplus_sites >= dis_list[0].passenger_num:
            car.change_surplus_sites(dis_list[0].passenger_num)
            dis_list[0].unsolved = False
            car.orders.append(dis_list[0])
            r.append((dis_list[0], car))
    else:
        for i in range(1, len(dis_list) + 1):
            for j in range(car.surplus_sites, dis_list[i - 1].passenger_num - 1, -1):
                path[i, j] = 0
                if table[j] < (table[j - dis_list[i - 1].passenger_num] + dis_list[i - 1].weight) and dis_list[i - 1].is_grab == 0:
                    table[j] = table[j - dis_list[i - 1].passenger_num] + dis_list[i - 1].weight
                    path[i, j] = 1

        i, j = len(dis_list), car.surplus_sites
        while i > 0 and j > 0:
            if path[i, j] == 1:
                car.change_surplus_sites(dis_list[i - 1].passenger_num)
                dis_list[i - 1].unsolved = False
                car.orders.append(dis_list[i - 1])
                r.append((dis_list[i - 1], car))
                j -= dis_list[i - 1].passenger_num
            i -= 1
    return r


def k_means(order_list: List[Order], k):
    """
    聚类
    :param order_list:
    :return:
    """
    data = np.array([[order.lng, order.lat] for order in order_list])
    model1 = KMeans(n_clusters=k, max_iter=500, init='random', n_init=10)
    model1.fit(data)
    clusters = model1.predict(data)
    centers = model1.cluster_centers_

    # 二分K-means
    # centers, clusters = biKmeans(data, k)
    # centers = np.array([i.A.tolist()[0] for i in centers])
    # clusters = clusters[:, 0].A[:, 0]


    the_maps = []
    lng = lat = count = 0
    for index, center in enumerate(centers):
        orders = [order_list[e] for e, i in enumerate(clusters) if int(i) == index]
        cluster = {
            "id": index,
            "coordinate": list(center),
            "orders": orders
        }
        lng += list(center)[0]
        lat += list(center)[1]
        count += 1
        the_maps.append(cluster)

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
    data.sort(
        key=lambda obj: get_distance(obj.lng, obj.lat, point['coordinate'][0], point['coordinate'][1]))
    for obj in data:
        if len(obj.orders) == 0:
            return obj


def find_closest_cluster(obj, clusters):
    """
    寻找离车最近的并且没有分配过的簇
    :param car:
    :param clusters:
    :return:
    """
    clusters.sort(
        key=lambda cluster: get_distance(obj.lng, obj.lat, cluster['coordinate'][0], cluster['coordinate'][1]))
    if isinstance(obj, Car):
        for cluster in clusters:
            if not has_solved_orders(cluster['orders']):
                return cluster
    if isinstance(obj, Order):
        return clusters[0]
