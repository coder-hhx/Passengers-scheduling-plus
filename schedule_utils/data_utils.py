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

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def load_data():
    """
    加载数据
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
                        }, {
                            "size": "2",
                            "coordinate": ["104.086658", "30.652903"],
                            "id": "14",
                            "is_grab": 0
                        }, {
                            "size": "1",
                            "coordinate": ["104.075113", "30.659585"],
                            "id": "15",
                            "is_grab": 0
                        }, {
                            "size": "3",
                            "coordinate": ["104.096228", "30.655635"],
                            "id": "16",
                            "is_grab": 0
                        }, {
                            "size": "1",
                            "coordinate": ["104.082366", "30.659917"],
                            "id": "17",
                            "is_grab": 0
                        }, {
                            "size": "2",
                            "coordinate": ["104.058634", "30.663203"],
                            "id": "18",
                            "is_grab": 1
                        }, {
                            "size": "1",
                            "coordinate": ["104.061981", "30.644522"],
                            "id": "19",
                            "is_grab": 1
                        }, {
                            "size": "2",
                            "coordinate": ["104.055716", "30.641347"],
                            "id": "20",
                            "is_grab": 1
                        }, {
                            "size": "1",
                            "coordinate": ["104.049793", "30.652349"],
                            "id": "21",
                            "is_grab": 1
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
                        }, {
                            "driver_id": "11",
                            "coordinate": ["104.086379", "30.667116"],
                            "sites": 5
                        }, {
                            "driver_id": "12",
                            "coordinate": ["104.109295", "30.662834"],
                            "sites": 6
                        }, {
                            "driver_id": "13",
                            "coordinate": ["104.063719", "30.668075"],
                            "sites": 8
                        }, {
                            "driver_id": "14",
                            "coordinate": ["104.066294", "30.633149"],
                            "sites": 6
                        }, {
                            "driver_id": "15",
                            "coordinate": ["104.057969", "30.652349"],
                            "sites": 4
                        }, {
                            "driver_id": "16",
                            "coordinate": ["104.096764", "30.633814"],
                            "sites": 6
                        }, {
                            "driver_id": "17",
                            "coordinate": ["104.08389", "30.650208"],
                            "sites": 8
                        }, {
                            "driver_id": "18",
                            "coordinate": ["104.075306", "30.645851"],
                            "sites": 4
                        }, {
                            "driver_id": "19",
                            "coordinate": ["104.095648", "30.64083"],
                            "sites": 6
                        }, {
                            "driver_id": "20",
                            "coordinate": ["104.098052", "30.657148"],
                            "sites": 6
                        }],
                        "config": {
                            "order_distance": "2000",
                            "car_distance": "2000",
                            "reserve_rate": "0.2",
                            "type": "receive"
                        }
                    }'''
    r.lpush('data', data_txt)


def send_data():
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
                        }, {
                            "size": "2",
                            "coordinate": ["104.086658", "30.652903"],
                            "id": "14",
                            "is_grab": 0
                        }, {
                            "size": "1",
                            "coordinate": ["104.075113", "30.659585"],
                            "id": "15",
                            "is_grab": 0
                        }, {
                            "size": "3",
                            "coordinate": ["104.096228", "30.655635"],
                            "id": "16",
                            "is_grab": 0
                        }, {
                            "size": "1",
                            "coordinate": ["104.082366", "30.659917"],
                            "id": "17",
                            "is_grab": 0
                        }, {
                            "size": "2",
                            "coordinate": ["104.058634", "30.663203"],
                            "id": "18",
                            "is_grab": 1
                        }, {
                            "size": "1",
                            "coordinate": ["104.061981", "30.644522"],
                            "id": "19",
                            "is_grab": 1
                        }, {
                            "size": "2",
                            "coordinate": ["104.055716", "30.641347"],
                            "id": "20",
                            "is_grab": 1
                        }, {
                            "size": "1",
                            "coordinate": ["104.049793", "30.652349"],
                            "id": "21",
                            "is_grab": 1
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
                        }, {
                            "driver_id": "11",
                            "coordinate": ["104.086379", "30.667116"],
                            "sites": 5
                        }, {
                            "driver_id": "12",
                            "coordinate": ["104.109295", "30.662834"],
                            "sites": 6
                        }, {
                            "driver_id": "13",
                            "coordinate": ["104.063719", "30.668075"],
                            "sites": 8
                        }, {
                            "driver_id": "14",
                            "coordinate": ["104.066294", "30.633149"],
                            "sites": 6
                        }, {
                            "driver_id": "15",
                            "coordinate": ["104.057969", "30.652349"],
                            "sites": 4
                        }, {
                            "driver_id": "16",
                            "coordinate": ["104.096764", "30.633814"],
                            "sites": 6
                        }, {
                            "driver_id": "17",
                            "coordinate": ["104.08389", "30.650208"],
                            "sites": 8
                        }, {
                            "driver_id": "18",
                            "coordinate": ["104.075306", "30.645851"],
                            "sites": 4
                        }, {
                            "driver_id": "19",
                            "coordinate": ["104.095648", "30.64083"],
                            "sites": 6
                        }, {
                            "driver_id": "20",
                            "coordinate": ["104.098052", "30.657148"],
                            "sites": 6
                        }],
                        "config": {
                            "order_distance": "2000",
                            "car_distance": "2000",
                            "reserve_rate": "0.2",
                            "type": "send"
                        }
                    }'''
    r.lpush('data', data_txt)
