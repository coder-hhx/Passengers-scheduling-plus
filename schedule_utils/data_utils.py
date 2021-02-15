# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project Name: Passengers-scheduling-plus
File Name: data_utils.py
Author: hhx
Contact: houhaixu_email@163.com
Create Date: 2021/2/2
-------------------------------------------------
"""

import json
from typing import List, Tuple

import redis

from schedule_utils.models import Car, Order

r = redis.Redis(host='localhost', port=6379, decode_responses=True, db=1)


def have_data():
    """
    判断数据库中是否存在数据
    :return:
    """
    if r.llen('data') > 0:
        return True
    return False


def load_data(mode: int):
    """
    加载数据
    :param mode: 数据加载模式   1为不拆分模式；2为拆分模式
    :return:
    """
    car_list: List[Car] = []  # 车辆列表
    order_list: List[Order] = []  # 订单列表

    data = json.loads(r.rpop('data'))
    # max_distance = int(data["config"]["far_distance"])  # 最远距离
    order_distance = int(data['config']['order_distance'])  # 订单最远距离
    car_distance = int(data['config']['car_distance'])  # 车辆最远距离
    reserve_rate = float(data['config']['reserve_rate'])  # 作为剩余比例
    type_ = data["config"]["type"]  # 类别

    if mode == 1:
        for order in data['user_list']:
            o = Order(
                id_=int(order['id']),
                passenger_num=int(order['size']),
                lng=float(order['coordinate'][0]),
                lat=float(order['coordinate'][1]),
                is_grab=int(order['is_grab'])
            )
            if order['bind_car'] != '':
                o.bind_car = int(order['bind_car'])
            order_list.append(o)
    else:
        for order in data['user_list']:
            for i in range(int(order['size'])):
                o = Order(
                    id_=int(order['id']),
                    passenger_num=1,
                    lng=float(order['coordinate'][0]),
                    lat=float(order['coordinate'][1]),
                    is_grab=int(order['is_grab'])
                )
                if order['bind_car'] != '':
                    o.bind_car = int(order['bind_car'])
                order_list.append(o)

    if type_ == "receive":
        for car in data['driver_list']:
            car_list.append(
                Car(
                    id_=int(car['driver_id']),
                    lng=float(car['coordinate'][0]),
                    lat=float(car['coordinate'][1]),
                    sites=int(car['sites'])
                )
            )
    elif type_ == "send":
        for car in data['driver_list']:
            car_list.append(
                Car(
                    id_=int(car['driver_id']),
                    lng=0,
                    lat=0,
                    sites=int(car['sites'])
                )
            )

    return order_list, car_list, type_, order_distance, car_distance, reserve_rate


def push_data(result: List[Tuple[Order, Car]]):
    r.lpush('table', json.dumps([[[ret[0].id_, ret[1].id_], ret[0].passenger_num] for ret in result]))


def receive_data():
    with open(r'C:\Users\10219\Desktop\Passengers-scheduling-plus\data.txt', 'r', encoding='utf-8') as f:
        data_txt = f.read()
    r.lpush('data', data_txt)


def send_data():
    with open(r'C:\Users\10219\Desktop\Passengers-scheduling-plus\data.txt', 'r', encoding='utf-8') as f:
        data_txt = f.read()
    r.lpush('data', data_txt)
