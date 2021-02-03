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
from typing import List

from new.caculate_utils import k_means, get_distance, DP, find_closest_obj
from new.data_utils import load_data, push_data
from new.models import Order, Car


def has_unsolved_orders(orders):
    """
    判断是否有为分配的订单
    :param orders:
    :return:
    """
    for order in orders:
        if order.unsolved:
            return True
    return False


def get_dis_list(max_dis, car: Car, orders: List[Order]):
    dis_list = []
    for order in orders:
        dis = get_distance(order.lng, order.lat, car.lng, car.lat)
        if dis < max_dis and order.unsolved and car.surplus_sites >= order.passenger_num:
            order.dis = max_dis - dis  # 方便一会儿动态规划算法，距离司机最近，等于最大距离-距离司机的距离 最大
            dis_list.append(order)
    return dis_list


def receive_type_calculate(order_list, car_list, max_distance):
    """
    接模式下，需计算司机位置
    :param mode: 加载模式
    :return:
    """

    result = []  # 计算结果

    while has_unsolved_orders(order_list) and len(car_list) > 0:
        maps = k_means(order_list)
        if len(maps) == 0:
            break

        while True:
            if len(maps) == 0 or len(car_list) == 0:
                break
            center = maps.pop(0)
            closest_car: Car = find_closest_obj(center, car_list)
            dis_list: List[Order] = get_dis_list(max_distance, closest_car, order_list)
            if dis_list:
                result.extend(DP(closest_car, dis_list))
                break
            else:
                car_list.remove(closest_car)

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


if __name__ == '__main__':
    order_list, car_list, max_distance, type_ = load_data(mode=1)
    result = send_type_calculate(order_list, car_list, max_distance)
    print(result)
