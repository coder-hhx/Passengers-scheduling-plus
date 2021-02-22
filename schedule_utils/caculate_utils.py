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

from schedule_utils.models import Order, Car


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


def has_unsolved_orders(orders):
    """
    判断是否有未分配的订单
    :param orders:
    :return:
    """
    for order in orders:
        if order.unsolved:
            return True
    return False


def is_all_grab_orders(orders: List[Order]):
    """
    判断一组订单中是否全部在范围之外
    :param orders:
    :return:
    """
    for order in orders:
        if order.is_grab == 0:
            return False
    return True


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


def DP(car: Car, orders: List[Order]):
    """
    动态规划，参考背包问题
    :param car: 要分配的车
    :param orders: 可被分配的订单列表
    :return:
    """
    path = np.zeros((len(orders) + 1, car.surplus_sites + 1))
    table = np.zeros(car.surplus_sites + 1)
    r = []
    if len(orders) == 1 and orders[0].unsolved:  # 若只有一个订单，则直接分配给该车
        if car.surplus_sites >= orders[0].passenger_num:
            if is_all_grab_orders(orders):
                if orders[0].passenger_num <= car.surplus_sites * 0.5:
                    return r
            car.change_surplus_sites(orders[0].passenger_num)
            orders[0].unsolved = False
            car.orders.append(orders[0])
            r.append((orders[0], car))
    else:
        for i in range(1, len(orders) + 1):
            for j in range(car.surplus_sites, orders[i - 1].passenger_num - 1, -1):
                path[i, j] = 0
                if table[j] < (table[j - orders[i - 1].passenger_num] + orders[i - 1].weight) and orders[
                    i - 1].unsolved:
                    table[j] = table[j - orders[i - 1].passenger_num] + orders[i - 1].weight
                    path[i, j] = 1

        i, j = len(orders), car.surplus_sites
        if is_all_grab_orders(orders):
            all_passenger = 0
            while i > 0 and j > 0:
                if path[i, j] == 1:
                    all_passenger += orders[i - 1].passenger_num
                    j -= orders[i - 1].passenger_num
                i -= 1
            if all_passenger <= car.surplus_sites * 0.5:
                return r
        i, j = len(orders), car.surplus_sites
        while i > 0 and j > 0:
            if path[i, j] == 1:
                car.change_surplus_sites(orders[i - 1].passenger_num)
                orders[i - 1].unsolved = False
                car.orders.append(orders[i - 1])
                r.append((orders[i - 1], car))
                j -= orders[i - 1].passenger_num
            i -= 1
    return r


def k_means(order_list: List[Order], k: int):
    """
    聚类
    :param order_list:
    :return:
    """
    data = np.array([[order.lng, order.lat] for order in order_list])
    model1 = KMeans(n_clusters=k, max_iter=500, init='random', n_init=10, random_state=10)
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


def find_closest_car(cluster, cars, car_distance, type_, is_grab=False):
    """
    寻找距离cluster最近的一个车
    :param cluster:
    :param cars:
    :param car_distance:
    :param type_
    :param is_grab:
    :return:
    """
    passenger_num = 0

    for order in cluster['orders']:
        passenger_num += order.passenger_num

    if type_ == 'receive':
        if not is_grab:
            cars.sort(
                key=lambda car: get_distance(car.lng, car.lat, cluster['coordinate'][0], cluster['coordinate'][1]))
            for car in cars:
                if len(car.orders) == 0 and \
                        get_distance(car.lng, car.lat, cluster['coordinate'][0],
                                     cluster['coordinate'][1]) < car_distance and \
                        car.surplus_sites >= passenger_num:
                    # cars.remove(car)
                    return car

            for car in cars:
                if len(car.orders) == 0 and \
                        get_distance(car.lng, car.lat, cluster['coordinate'][0],
                                     cluster['coordinate'][1]) < car_distance \
                        and car.surplus_sites > max(cluster['orders'], key=lambda o: o.passenger_num).passenger_num:
                    # cars.remove(car)
                    return car

            for car in cars:
                if len(car.orders) == 0 and \
                        get_distance(car.lng, car.lat, cluster['coordinate'][0],
                                     cluster['coordinate'][1]) < car_distance:
                    # cars.remove(car)
                    return car

            for car in cars:
                if len(car.orders) == 0:
                    # cars.remove(car)
                    return car
        else:
            cars.sort(
                key=lambda car: get_distance(car.lng, car.lat, cluster['coordinate'][0], cluster['coordinate'][1]))
            for car in cars:
                if len(car.orders) == 0:
                    # cars.remove(car)
                    return car

    else:
        cars.sort(key=lambda car: car.surplus_sites, reverse=True)
        for car in cars:
            if len(car.orders) == 0 and car.surplus_sites >= passenger_num:
                # cars.remove(car)
                return car

        for car in cars:
            if len(car.orders) == 0 and \
                    car.surplus_sites > max(cluster['orders'], key=lambda o: o.passenger_num).passenger_num:
                # cars.remove(car)
                return car

        for car in cars:
            if len(car.orders) == 0:
                # cars.remove(car)
                return car


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
