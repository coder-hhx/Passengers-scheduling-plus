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


class Order(object):
    __slots__ = ["_id", "passenger_num", "lng", "lat"]

    def __init__(self, _id, passenger_num, lng, lat):
        self._id = _id
        self.passenger_num = passenger_num
        self.lng = lng
        self.lat = lat


class Car(object):
    __slots__ = ["_id", "sites", "lng", "lat"]

    def __init__(self, _id, sites, lng, lat):
        self._id = _id
        self.sites = sites
        self.lng = lng
        self.lat = lat
