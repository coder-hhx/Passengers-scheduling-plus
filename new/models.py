# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project Name: Passengers-scheduling-plus
File Name: models.py
Author: hhx
Contact: houhaixu_email@163.com
Create Date: 2021/2/1
-------------------------------------------------
"""
from typing import List


class Order(object):
    __slots__ = ["id_", "passenger_num", "lng", "lat", "unsolved", "dis"]

    def __init__(self, id_, passenger_num, lng, lat):
        """
        :param id_: 订单id
        :param passenger_num: 订单中的乘客数量
        :param lng: 经度
        :param lat: 纬度
        """
        self.id_ = id_
        self.passenger_num = passenger_num
        self.lng = lng
        self.lat = lat
        self.unsolved = True  # 未被分配车辆
        self.dis = 0  # 该订单与某车之间的距离


class Car(object):
    __slots__ = ["id_", "sites", "lng", "lat", "orders", "surplus_sites"]

    def __init__(self, id_, sites, lng, lat):
        """
        :param id_: 车辆id
        :param sites: 车辆座位数
        :param lng: 经度
        :param lat: 纬度
        """
        self.id_ = id_
        self.sites = sites
        self.lng = lng
        self.lat = lat
        self.surplus_sites = self.sites  # 剩余的座位数
        self.orders: List[Order] = []  # 该车被分配了哪些订单

    def change_surplus_sites(self, n: int):
        self.surplus_sites -= n
