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
    max_distance = int(data["config"]["far_distance"])  # 最远距离
    type_ = data["config"]["type"]  # 类别

    if mode == 1:
        for order in data['user_list']:
            order_list.append(
                Order(
                    id_=int(order['id']),
                    passenger_num=int(order['size']),
                    lng=float(order['coordinate'][0]),
                    lat=float(order['coordinate'][1])
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
                        lat=float(order['coordinate'][1])
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

    return order_list, car_list, max_distance, type_


def push_data(result: List[Tuple[Order, Car]]):
    # print(str([((ret[0].id_, ret[1].id_), ret[0].passenger_num) for ret in result]))
    r.lpush('table', str([((ret[0].id_, ret[1].id_), ret[0].passenger_num) for ret in result]))


def receive_data(dis: int = 5000):
    data_txt = '{"user_list": [{"id": 0, "coordinate": [104.05072191555561, 30.601844722095155], "size": 1}, {"id": 1, "coordinate": [104.00496562983494, 30.70074681444294], "size": 2}, {"id": 2, "coordinate": [104.14045553894448, 30.73300443419149], "size": 3}, {"id": 3, "coordinate": [104.02016267833693, 30.619050275402277], "size": 2}, {"id": 4, "coordinate": [104.13241229459545, 30.64683281862825], "size": 1}, {"id": 5, "coordinate": [104.05259526872707, 30.611761866491253], "size": 4}, {"id": 6, "coordinate": [104.115379614329, 30.70677969334144], "size": 2}, {"id": 7, "coordinate": [104.12193746985935, 30.724862334364683], "size": 4}, {"id": 8, "coordinate": [104.09090825803933, 30.728295883714857], "size": 1}, {"id": 9, "coordinate": [104.0285242479951, 30.614870159888227], "size": 2}, {"id": 10, "coordinate": [104.06284149961331, 30.70747397855058], "size": 1}, {"id": 11, "coordinate": [104.11987547144402, 30.627279410030678], "size": 2}, {"id": 12, "coordinate": [104.07503043588602, 30.637436189508534], "size": 2}, {"id": 13, "coordinate": [104.03356388083553, 30.745934287967504], "size": 1}, {"id": 14, "coordinate": [104.08864592890527, 30.65378357734492], "size": 3}, {"id": 15, "coordinate": [104.07171940097238, 30.72545910001263], "size": 5}, {"id": 16, "coordinate": [104.0287053083747, 30.712661078442444], "size": 5}, {"id": 17, "coordinate": [104.0366340603779, 30.676309665123235], "size": 4}, {"id": 18, "coordinate": [104.08848219455142, 30.748417271652695], "size": 2}, {"id": 19, "coordinate": [104.11455486424384, 30.603287106975106], "size": 1}], "driver_list":[{"driver_id": 0, "coordinate": [104.13310339290251, 30.64023468231509], "sites": 6}, {"driver_id": 1, "coordinate": [104.06858829295508, 30.684775516129474], "sites": 4}, {"driver_id": 2, "coordinate": [104.07634566390571, 30.67253660532822], "sites": 6}, {"driver_id": 3, "coordinate": [104.11986185147461, 30.65146266953304], "sites": 4}, {"driver_id": 4, "coordinate": [104.01122446092239, 30.636035430082305], "sites": 4}, {"driver_id": 5, "coordinate": [104.0650708257392, 30.65331807839672], "sites": 6}, {"driver_id": 6, "coordinate": [104.13078679816792, 30.716117616265876], "sites": 6}, {"driver_id": 7, "coordinate": [104.10029849302218, 30.606095462242887], "sites": 4}, {"driver_id": 8, "coordinate": [104.13261988469455, 30.673075654782593], "sites": 6}, {"driver_id": 9, "coordinate": [104.05631982063983, 30.716668079749933], "sites": 6}, {"driver_id": 10, "coordinate": [104.0129599489303, 30.706041997085503], "sites": 4}, {"driver_id": 11, "coordinate": [104.04563538964011, 30.718795538285743], "sites": 4}, {"driver_id": 12, "coordinate": [104.11286262900849, 30.71735595215192], "sites": 6}, {"driver_id": 13, "coordinate": [104.0769169935041, 30.606079684390995], "sites": 4}, {"driver_id": 14, "coordinate": [104.13131856755234, 30.684256613919015], "sites": 4}, {"driver_id": 15, "coordinate": [104.07665267505828, 30.628217281276648], "sites": 6}, {"driver_id": 16, "coordinate": [104.116557362039, 30.658893367870643], "sites": 6}, {"driver_id": 17, "coordinate": [104.09161717386395, 30.729267126666507],"sites": 4}, {"driver_id": 18, "coordinate": [104.07466188480925, 30.608231721076802], "sites": 4}, {"driver_id": 19,"coordinate": [104.03904389827431, 30.65543276111534], "sites": 6}, {"driver_id": 20, "coordinate": [104.05508727319406, 30.603201278268482], "sites": 6}, {"driver_id": 21, "coordinate": [104.09974349492846, 30.641880551833964], "sites": 6}, {"driver_id": 22, "coordinate": [104.13738981820846, 30.732496049099296], "sites": 6}, {"driver_id": 23, "coordinate": [104.08907297086817, 30.67219050110285], "sites": 6}, {"driver_id": 24, "coordinate": [104.103402806249, 30.67335282780415], "sites": 4}], "config": {"far_distance": "' + str(
        dis) + '", "type": "receive"}}'
    r.set('data', data_txt)


def send_data(dis: int = 5000):
    data_txt = '{"user_list": [{"id": 0, "coordinate": [104.05072191555561, 30.601844722095155], "size": 1}, {"id": 1, "coordinate": [104.00496562983494, 30.70074681444294], "size": 2}, {"id": 2, "coordinate": [104.14045553894448, 30.73300443419149], "size": 3}, {"id": 3, "coordinate": [104.02016267833693, 30.619050275402277], "size": 2}, {"id": 4, "coordinate": [104.13241229459545, 30.64683281862825], "size": 1}, {"id": 5, "coordinate": [104.05259526872707, 30.611761866491253], "size": 4}, {"id": 6, "coordinate": [104.115379614329, 30.70677969334144], "size": 2}, {"id": 7, "coordinate": [104.12193746985935, 30.724862334364683], "size": 4}, {"id": 8, "coordinate": [104.09090825803933, 30.728295883714857], "size": 1}, {"id": 9, "coordinate": [104.0285242479951, 30.614870159888227], "size": 2}, {"id": 10, "coordinate": [104.06284149961331, 30.70747397855058], "size": 1}, {"id": 11, "coordinate": [104.11987547144402, 30.627279410030678], "size": 2}, {"id": 12, "coordinate": [104.07503043588602, 30.637436189508534], "size": 2}, {"id": 13, "coordinate": [104.03356388083553, 30.745934287967504], "size": 1}, {"id": 14, "coordinate": [104.08864592890527, 30.65378357734492], "size": 3}, {"id": 15, "coordinate": [104.07171940097238, 30.72545910001263], "size": 5}, {"id": 16, "coordinate": [104.0287053083747, 30.712661078442444], "size": 5}, {"id": 17, "coordinate": [104.0366340603779, 30.676309665123235], "size": 4}, {"id": 18, "coordinate": [104.08848219455142, 30.748417271652695], "size": 2}, {"id": 19, "coordinate": [104.11455486424384, 30.603287106975106], "size": 1}], "driver_list":[{"driver_id": 0, "coordinate": [104.13310339290251, 30.64023468231509], "sites": 6}, {"driver_id": 1, "coordinate": [104.06858829295508, 30.684775516129474], "sites": 4}, {"driver_id": 2, "coordinate": [104.07634566390571, 30.67253660532822], "sites": 6}, {"driver_id": 3, "coordinate": [104.11986185147461, 30.65146266953304], "sites": 4}, {"driver_id": 4, "coordinate": [104.01122446092239, 30.636035430082305], "sites": 4}, {"driver_id": 5, "coordinate": [104.0650708257392, 30.65331807839672], "sites": 6}, {"driver_id": 6, "coordinate": [104.13078679816792, 30.716117616265876], "sites": 6}, {"driver_id": 7, "coordinate": [104.10029849302218, 30.606095462242887], "sites": 4}, {"driver_id": 8, "coordinate": [104.13261988469455, 30.673075654782593], "sites": 6}, {"driver_id": 9, "coordinate": [104.05631982063983, 30.716668079749933], "sites": 6}, {"driver_id": 10, "coordinate": [104.0129599489303, 30.706041997085503], "sites": 4}, {"driver_id": 11, "coordinate": [104.04563538964011, 30.718795538285743], "sites": 4}, {"driver_id": 12, "coordinate": [104.11286262900849, 30.71735595215192], "sites": 6}, {"driver_id": 13, "coordinate": [104.0769169935041, 30.606079684390995], "sites": 4}, {"driver_id": 14, "coordinate": [104.13131856755234, 30.684256613919015], "sites": 4}, {"driver_id": 15, "coordinate": [104.07665267505828, 30.628217281276648], "sites": 6}, {"driver_id": 16, "coordinate": [104.116557362039, 30.658893367870643], "sites": 6}, {"driver_id": 17, "coordinate": [104.09161717386395, 30.729267126666507],"sites": 4}, {"driver_id": 18, "coordinate": [104.07466188480925, 30.608231721076802], "sites": 4}, {"driver_id": 19,"coordinate": [104.03904389827431, 30.65543276111534], "sites": 6}, {"driver_id": 20, "coordinate": [104.05508727319406, 30.603201278268482], "sites": 6}, {"driver_id": 21, "coordinate": [104.09974349492846, 30.641880551833964], "sites": 6}, {"driver_id": 22, "coordinate": [104.13738981820846, 30.732496049099296], "sites": 6}, {"driver_id": 23, "coordinate": [104.08907297086817, 30.67219050110285], "sites": 6}, {"driver_id": 24, "coordinate": [104.103402806249, 30.67335282780415], "sites": 4}], "config": {"far_distance": "' + str(
        dis) + '", "type": "send"}}'
    r.set('data', data_txt)
