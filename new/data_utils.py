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

from new.models import Car, Order

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def load_data(mode: int):
    """
    加载数据
    :param mode: 加载模式：mode=1 为一个订单多个乘客；mode=2 为一个订单一个乘客（实际是将一个订单中的多个乘客，拆为多个订单）
    :return:
    """
    car_list: List[Car] = []  # 车辆列表
    order_list: List[Order] = []  # 订单列表

    data = json.loads(r.get('data'))
    # max_distance = int(data["config"]["far_distance"])  # 最远距离
    order_distance = int(data['config']['order_distance'])  # 订单最远距离
    car_distance = int(data['config']['car_distance'])  # 车辆最远距离
    reserve_rate = float(data['config']['reserve_rate'])  # 作为剩余比例
    type_ = data["config"]["type"]  # 类别

    if mode == 1:
        for order in data['user_list']:
            order_list.append(
                Order(
                    id_=int(order['id']),
                    passenger_num=int(order['size']),
                    lng=float(order['coordinate'][0]),
                    lat=float(order['coordinate'][1]),
                    is_grab=int(order['is_grab'])
                )
            )
    elif mode == 2:
        for order in data['user_list']:
            for i in range(int(order['size'])):
                order_list.append(
                    Order(
                        id_=int(order['id']),
                        passenger_num=1,
                        lng=float(order['coordinate'][0]),
                        lat=float(order['coordinate'][1]),
                        is_grab=int(order['is_grab'])
                    )
                )

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
    # print(str([((ret[0].id_, ret[1].id_), ret[0].passenger_num) for ret in result]))
    r.lpush('table', str([((ret[0].id_, ret[1].id_), ret[0].passenger_num) for ret in result]))


def receive_data():
    data_txt = '''  {
                        "user_list": [{
                            "size": "1",
                            "coordinate": ["104.07565", "30.664052"],
                            "id": "1",
                            "is_grab": 0
                        }, {
                            "size": "3",
                            "coordinate": ["104.086121", "30.66383"],
                            "id": "2",
                            "is_grab": 0
                        }, {
                            "size": "2",
                            "coordinate": ["104.095305", "30.659031"],
                            "id": "3",
                            "is_grab": 0
                        }, {
                            "size": "1",
                            "coordinate": ["104.099425", "30.648473"],
                            "id": "4",
                            "is_grab": 0
                        }, {
                            "size": "4",
                            "coordinate": ["104.086464", "30.64094"],
                            "id": "5",
                            "is_grab": 0
                        }, {
                            "size": "3",
                            "coordinate": ["104.078654", "30.653789"],
                            "id": "6",
                            "is_grab": 0
                        }, {
                            "size": "1",
                            "coordinate": ["104.072903", "30.64574"],
                            "id": "7",
                            "is_grab": 0
                        }, {
                            "size": "1",
                            "coordinate": ["104.073332", "30.669072"],
                            "id": "8",
                            "is_grab": 1
                        }, {
                            "size": "2",
                            "coordinate": ["104.085349", "30.670327"],
                            "id": "9",
                            "is_grab": 1
                        }, {
                            "size": "2",
                            "coordinate": ["104.103631", "30.668777"],
                            "id": "10",
                            "is_grab": 1
                        }, {
                            "size": "1",
                            "coordinate": ["104.108265", "30.653051"],
                            "id": "11",
                            "is_grab": 1
                        }, {
                            "size": "1",
                            "coordinate": ["104.069384", "30.637396"],
                            "id": "12",
                            "is_grab": 1
                        }, {
                            "size": "5",
                            "coordinate": ["104.089469", "30.640202"],
                            "id": "13",
                            "is_grab": 0
                        }],
                        "gid": "152",
                        "driver_list": [{
                            "driver_id": "1",
                            "coordinate": ["104.09655", "30.65343"],
                            "sites": 4
                        }, {
                            "driver_id": "2",
                            "coordinate": ["104.075736", "30.650107"],
                            "sites": 6
                        }, {
                            "driver_id": "3",
                            "coordinate": ["104.0808", "30.64707"],
                            "sites": 4
                        }, {
                            "driver_id": "4",
                            "coordinate": ["104.077281", "30.658662"],
                            "sites": 4
                        }, {
                            "driver_id": "5",
                            "coordinate": ["104.09685", "30.644411"],
                            "sites": 6
                        }, {
                            "driver_id": "6",
                            "coordinate": ["104.092902", "30.656964"],
                            "sites": 4
                        }, {
                            "driver_id": "7",
                            "coordinate": ["104.08552", "30.664864"],
                            "sites": 6
                        }, {
                            "driver_id": "8",
                            "coordinate": ["104.076766", "30.640571"],
                            "sites": 6
                        }, {
                            "driver_id": "9",
                            "coordinate": ["104.070843", "30.652312"],
                            "sites": 4
                        }, {
                            "driver_id": "10",
                            "coordinate": ["104.090069", "30.640497"],
                            "sites": 4
                        }],
                        "config": {
                            "far_distance": "10000",
                            "order_distance": "2000",
                            "car_distance": "2000",
                            "reserve_rate": "0.2",
                            "type": "receive"
                        }
                    }'''
    r.set('data', data_txt)


def send_data():
    data_txt = '{"user_list":[{"size":"2","coordinate":["104.085177","30.651646"],"id":"1","is_grab":0}],"gid":"152","driver_list":[{"driver_id":"9","coordinate":["104.085177","30.651646"],"sites":4},{"driver_id":"11","coordinate":["104.085177","30.651646"],"sites":6},{"driver_id":"59","coordinate":["104.085177","30.651646"],"sites":4},{"driver_id":"71","coordinate":["104.085177","30.651646"],"sites":4}],"config":{"far_distance":"10000","order_distance":"2000","car_distance":"2000","reserve_rate":"0.2","type":"send"}}'
    r.set('data', data_txt)
