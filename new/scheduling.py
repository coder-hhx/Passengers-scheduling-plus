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

from new.load_data import load_data
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
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radLat1)))
    return math.hypot(order.lng - car.lng, order.lat - car.lat)


def receive_type_caculate():
    order_list, car_list, max_distance, _type = load_data()
