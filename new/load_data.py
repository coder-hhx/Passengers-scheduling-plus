# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project Name: Passengers-scheduling-plus
File Name: load_data.py
Author: hhx
Contact: houhaixu_email@163.com
Create Date: 2021/2/2
-------------------------------------------------
"""

import json
from typing import List

import redis

from new.models import Car, Order

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def load_data():
    car_list: List[Car] = []  # 车辆列表
    order_list: List[Order] = []  # 订单列表

    data = json.loads(r.get('data'))
    max_distance = int(data["config"]["far_distance"])  # 最远距离
    _type = data["config"]["type"]  # 类别

    for order in data['user_list']:
        order_list.append(
            Order(
                _id=int(order['id']),
                passenger_num=int(order['size']),
                lng=float(order['coordinate'][1]),
                lat=float(order['coordinate'][0])
            )
        )

    if _type == "receive":
        for car in data['driver_list']:
            car_list.append(
                Car(
                    _id=int(car['driver_id']),
                    lng=float(car['coordinate'][1]),
                    lat=float(car['coordinate'][0]),
                    sites=int(car['sites'])
                )
            )

    return order_list, car_list, max_distance, _type


if __name__ == '__main__':
    order_list, car_list, max_distance, _type = load_data()
