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
import copy
from typing import List

from new.caculate_utils import k_means, get_distance, DP, find_closest_obj, find_closest_cluster
from new.data_utils import load_data, push_data
from new.models import Order, Car


def get_cars_sites_num(cars: List[Car]):
    """
    获取当前车辆列表座位数
    :param cars:
    :return:
    """
    sites_num = 0
    for car in cars:
        sites_num += car.sites
    return sites_num


def get_orders_passengers_num(orders: List[Order]):
    """
    获取当前订单列表中乘客数量
    :param orders:
    :return:
    """
    passengers_num = 0
    for order in orders:
        passengers_num += order.passenger_num
    return passengers_num


def get_orders_center_point(orders: List[Order]):
    """
    获取订单列表中心点
    :param orders:
    :return:
    """
    avg_lng = 0
    avg_lat = 0
    count = 0
    for order in orders:
        avg_lng += order.lng
        avg_lat += order.lat
        count += 1
    return [avg_lng / count, avg_lat / count]


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


def preprocess_data(cars, orders, reserve_rate):
    """
    对数据进行预处理
    :param cars: 所有车辆
    :param orders: 所有订单
    :return: 可以使用的车辆
    """
    available_cars: List[Car] = []  # 可用车辆

    available_orders: List[Order] = []  # 可分配的订单

    grab_orders: List[Order] = []  # 需要抢单的列表

    all_passenger_num = 0

    for order in orders:
        if order.is_grab == 0:
            available_orders.append(order)
            all_passenger_num += order.passenger_num
            while get_cars_sites_num(available_cars) < all_passenger_num:
                available_cars.append(cars.pop(0))
        else:
            grab_orders.append(order)

    if math.floor(len(cars) * reserve_rate) >= 1:  # 如果还有可用车辆抢单
        for _ in range(math.floor(len(cars) * reserve_rate)):
            available_cars.append(cars.pop(0))

        center_point = get_orders_center_point(orders)

        grab_orders.sort(key=lambda elem: get_distance(center_point[0], center_point[1], elem.lng, elem.lat))

        while get_cars_sites_num(available_cars) < all_passenger_num + get_orders_passengers_num(grab_orders):
            # 若车辆座位数小于乘客数，则放弃最远的范围外的订单
            grab_orders.pop()

        available_orders.extend(grab_orders)

    return available_cars, available_orders


def abandon_order(orders: List[Order], center: List[float], max_dis: int):
    """
    放弃该簇中，范围外且距离簇心的距离大于最远距离的点
    :param orders:
    :param max_dis:
    :return:
    """
    new_orders = copy.copy(orders)
    for order in orders:
        order.weight = ((max_dis - get_distance(center[0], center[1], order.lng, order.lat)) / max_dis) * 0.01 \
                            + (0.9 * order.passenger_num) * (1 - order.is_grab)
        if order.is_grab == 0:
            new_orders.append(order)
        if order.is_grab == 1:
            if get_distance(center[0], center[1], order.lng, order.lat) <= max_dis:
                new_orders.remove(order)
    return new_orders


def receive_type_calculate(orders, cars, order_distance, car_distance):
    """
    接模式下，需计算司机位置
    :param mode: 加载模式
    :return:
    """

    result = []  # 计算结果

    in_orders = []  # 范围内订单
    out_orders = []  # 超出范围的订单

    for order in orders:
        if order.is_grab == 0:
            in_orders.append(order)
        else:
            out_orders.append(order)

    clusters = k_means(orders, len(cars))

    for cluster in clusters:
        closest_car: Car = find_closest_obj(cluster, cars)
        cluster['orders'] = abandon_order(cluster['orders'], cluster['coordinate'], order_distance)
        cluster['car'] = closest_car
        if not is_all_grab_orders(cluster['orders']):
            result.extend(DP(closest_car, cluster["orders"]))

    for order in in_orders:
        if order.unsolved:
            clusters.sort(
                key=lambda cluster: get_distance(order.lng, order.lat, cluster['coordinate'][0],
                                                 cluster['coordinate'][1]), reverse=True)
            for cluster in clusters:
                if cluster['car'].surplus_sites >= order.passenger_num:
                    order.unsolved = False
                    cluster['car'].orders.append(order)
                    cluster['car'].change_surplus_sites(order.passenger_num)
                    result.append((order, cluster['car']))
                    break

    # for order in in_orders:  # 将范围内的没有被分配的订单，进行分配
    #     if order.unsolved:
    #         clusters.sort(
    #             key=lambda cluster: get_distance(order.lng, order.lat, cluster['coordinate'][0],
    #                                              cluster['coordinate'][1]), reverse=True)
    #         for cluster in clusters:
    #             if cluster['car'].sites >= order.passenger_num:
    #                 cluster['orders'].append(order)
    #                 cluster['car'].change_surplus_sites(order.passenger_num)
    #                 cluster['orders'].sort(key=lambda order: order.passenger_num)
    #                 result.append((order, cluster['car']))
    #                 while cluster['car'].surplus_sites < 0:
    #                     o = cluster['orders'].pop()
    #                     o.unsolved = True
    #                     cluster['car'].surplus_sites += o.passenger_num
    #                     for ret in result:
    #                         if ret[0].id_ == o.id_ and ret[1].id_ == cluster['car'].id_:
    #                             result.remove(ret)
    #                             break

    push_data(result)

    return result


def send_type_calculate(order_list, car_list, max_distance):
    """
    送模式下，不需计算司机位置
    :return:
    """

    result = []
    while len(order_list) > 0 and len(car_list) > 0:
        car_list.sort(key=lambda car: car.surplus_sites, reverse=True)
        order_list.sort(key=lambda order: order.passenger_num, reverse=True)

        order = order_list.pop(0)
        car = car_list[0]
        if car.surplus_sites > order.passenger_num:
            result.append((order, car))
            car.change_surplus_sites(order.passenger_num)
            order.unsolved = False

            order_list.sort(key=lambda obj_: get_distance(order.lng, order.lat, obj_.lng, obj_.lat))

            for obj_ in order_list:
                if get_distance(order.lng, order.lat, obj_.lng, obj_.lat) > max_distance:
                    break
                if obj_.passenger_num <= car.surplus_sites:
                    result.append((obj_, car))
                    car.change_surplus_sites(obj_.passenger_num)
                    obj_.unsolved = False
                    order_list.remove(obj_)

        if car.surplus_sites == 0:
            car_list.remove(car)

    push_data(result)

    return result


def schedule(mode):
    order_list, car_list, type_, order_distance, car_distance, reserve_rate = load_data(mode=int(mode))
    available_cars, available_orders = preprocess_data(car_list, order_list, reserve_rate)
    return receive_type_calculate(available_orders, available_cars, order_distance, car_distance)


if __name__ == '__main__':
    schedule(1)
