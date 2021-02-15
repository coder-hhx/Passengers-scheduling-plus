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
import copy
import math
from typing import List

from schedule_utils.caculate_utils import k_means, get_distance, DP, find_closest_obj
from schedule_utils.data_utils import load_data, push_data, have_data
from schedule_utils.models import Order, Car

result = []  # 计算结果


def is_in_scope(lng, lat, radius):
    if get_distance(lng, lat, 104.085177, 30.651646) > radius:
        return 1
    else:
        return 0


def get_cars_sites_num(cars: List[Car]):
    """
    获取当前车辆列表座位数
    :param cars:
    :return:
    """
    sites_num = 0
    for car in cars:
        sites_num += car.surplus_sites
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


def abandon_order(orders: List[Order], center: List[float], max_dis: int):
    """
    放弃该簇中，范围外且距离簇心的距离大于最远距离的点
    :param orders:
    :param max_dis:
    :return:
    """
    new_orders = []
    for order in orders:
        order.weight = ((max_dis - get_distance(center[0], center[1], order.lng, order.lat)) / max_dis) * 0.01 \
                       + (0.9 * order.passenger_num) * (1 - order.is_grab)
        if order.is_grab == 0:
            new_orders.append(order)
        if order.is_grab == 1:
            if get_distance(center[0], center[1], order.lng, order.lat) <= max_dis:
                new_orders.append(order)
    return new_orders


def calculate_centroid(clusters):
    """
    重新计算质心
    :param clusters: 所有的组
    :return:
    """
    for cluster in clusters:
        # 重新计算质心
        if len(cluster['car'].orders) > 0:
            lng = lat = 0
            for order in cluster['car'].orders:
                lng += order.lng
                lat += order.lat
            cluster['coordinate'] = [lng / len(cluster['car'].orders), lat / len(cluster['car'].orders)]
        else:
            cluster['coordinate'] = [cluster['car'].lng, cluster['car'].lat]


def preprocess_data(cars, orders, reserve_rate):
    """
    对数据进行预处理
    :param cars: 所有车辆
    :param orders: 所有订单
    :return: 可以使用的车辆
    """

    must_cars: List[Car] = []  # 必须使用车辆

    available_cars: List[Car] = []  # 可用车辆

    available_orders: List[Order] = []  # 可分配的订单

    grab_orders: List[Order] = []  # 需要抢单的列表

    all_passenger_num = 0

    for order in orders:
        if isinstance(order.bind_car, int):
            for car in cars:
                if order.bind_car == car.id_:
                    car.change_surplus_sites(order.passenger_num)
                    car.orders.append(order)
                    if car not in must_cars:
                        must_cars.append(car)
                    result.append((order, car))
                    break
            order.unsolved = False
            all_passenger_num += order.passenger_num

    for car in must_cars:
        cars.remove(car)

    for order in orders:
        if order.is_grab == 0 and order.unsolved != False:
            available_orders.append(order)
            all_passenger_num += order.passenger_num
            while get_cars_sites_num(must_cars) + get_cars_sites_num(available_cars) < all_passenger_num:
                available_cars.append(cars.pop(0))
        else:
            if order.bind_car is None:
                grab_orders.append(order)

    if get_cars_sites_num(must_cars) + get_cars_sites_num(available_cars) \
            < all_passenger_num + get_orders_passengers_num(grab_orders):
        if math.floor(len(cars) * reserve_rate) >= 1:  # 如果还有可用车辆抢单
            for _ in range(math.floor(len(cars) * reserve_rate)):
                available_cars.append(cars.pop(0))

    center_point = get_orders_center_point(orders)

    grab_orders.sort(key=lambda elem: get_distance(center_point[0], center_point[1], elem.lng, elem.lat))

    while get_cars_sites_num(must_cars) + get_cars_sites_num(available_cars) \
            < all_passenger_num + get_orders_passengers_num(grab_orders):
        # 若车辆座位数小于乘客数，则放弃最远的范围外的订单
        grab_orders.pop()

    available_orders.extend(grab_orders)

    return must_cars, available_cars, available_orders


def schedule(must_cars: List[Car], cars: List[Car], orders: List[Order], order_distance: int, car_distance: int,
             type_: str, debug=False):
    """
    乘客调度
    :param must_cars: 优先分配车辆
    :param cars: 其他可用车辆
    :param orders: 订单
    :param order_distance:
    :param car_distance:
    :param type_:
    :param debug:
    :return:
    """

    if debug:
        debug_cars = []
        debug_cars.extend(copy.deepcopy(must_cars))
        debug_cars.extend(copy.deepcopy(cars))

    must_clusters = []  # 组

    in_orders = []  # 范围内订单

    out_orders = []  # 超出范围的订单
    for order in orders:
        if order.is_grab == 0:
            in_orders.append(order)
        else:
            out_orders.append(order)

    center = [0, 0]

    for order in in_orders:
        center[0] += order.lng
        center[1] += order.lat

    center[0] /= len(in_orders)
    center[1] /= len(in_orders)

    must_cars.sort(key=lambda car: get_distance(center[0], center[1], car.lng, car.lat))

    for car in must_cars:
        lng = 0
        lat = 0
        for order in car.orders:
            lng += order.lng
            lat += order.lat
        cluster = {
            "coordinate": [lng / len(car.orders), lat / len(car.orders)],
            "orders": car.orders,
            "car": car
        }
        while True:
            in_orders.sort(key=lambda order: get_distance(order.lng, order.lat, cluster["coordinate"][0],
                                                          cluster["coordinate"][1]))
            if get_distance(in_orders[0].lng, in_orders[1].lat, cluster['coordinate'][0],
                            cluster['coordinate'][1]) > order_distance:
                break
            if in_orders[0].passenger_num <= car.surplus_sites:
                o = in_orders.pop(0)
                o.unsolved = False
                car.change_surplus_sites(o.passenger_num)

                car.orders.append(o)
                result.append((o, car))
                orders.remove(o)
                for order in car.orders:
                    lng += order.lng
                    lat += order.lat
                cluster['coordinate'] = [lng / len(car.orders), lat / len(car.orders)]
                if len(in_orders) == 0:
                    break
            else:
                break
        must_clusters.append(cluster)

    if len(in_orders) > 0:
        clusters = k_means(orders, len(cars))

        for cluster in clusters:
            closest_car: Car = find_closest_obj(cluster, cars)
            cluster['orders'] = abandon_order(cluster['orders'], cluster['coordinate'], order_distance)
            cluster['car'] = closest_car
            if type_ == 'receive':
                if not is_all_grab_orders(cluster['orders']):
                    result.extend(DP(closest_car, cluster["orders"]))
                else:
                    if get_distance(cluster['coordinate'][0], cluster['coordinate'][1], closest_car.lng,
                                    closest_car.lat) <= car_distance:
                        result.extend(DP(closest_car, cluster["orders"]))
            else:
                result.extend(DP(closest_car, cluster["orders"]))

        clusters.extend(must_clusters)

        for order in in_orders:  # 一轮优化
            if order.unsolved:
                clusters.sort(
                    key=lambda cluster: get_distance(order.lng, order.lat, cluster['coordinate'][0],
                                                     cluster['coordinate'][1]))
                for cluster in clusters:
                    if cluster['car'].sites >= order.passenger_num:
                        cluster['car'].orders.append(order)
                        cluster['car'].change_surplus_sites(order.passenger_num)
                        cluster['car'].orders.sort(key=lambda order: order.passenger_num, reverse=True)
                        result.append((order, cluster['car']))
                        order.unsolved = False
                        while cluster['car'].surplus_sites < 0:
                            cluster['car'].orders.sort(key=lambda elem: elem.is_grab)
                            for o in cluster['car'].orders:
                                if o.bind_car is None:
                                    cluster['car'].orders.remove(o)
                                    o.unsolved = True
                                    cluster['car'].surplus_sites += o.passenger_num
                                    for ret in result:
                                        if ret[0].id_ == o.id_ and ret[1].id_ == cluster['car'].id_:
                                            result.remove(ret)
                                            break
                                    break
                        if not order.unsolved:
                            break

        calculate_centroid(clusters)

        for order in in_orders:  # 二轮优化
            if order.unsolved:
                clusters.sort(
                    key=lambda cluster: get_distance(order.lng, order.lat, cluster['coordinate'][0],
                                                     cluster['coordinate'][1]))
                for cluster in clusters:
                    if cluster['car'].surplus_sites >= order.passenger_num:
                        order.unsolved = False
                        cluster['car'].orders.append(order)
                        cluster['car'].change_surplus_sites(order.passenger_num)
                        result.append((order, cluster['car']))
                        break

        calculate_centroid(clusters)

        for order in in_orders:  # 三轮优化
            if order.unsolved:
                clusters.sort(
                    key=lambda cluster: get_distance(order.lng, order.lat, cluster['coordinate'][0],
                                                     cluster['coordinate'][1]))
                order.unsolved = False
                while order.passenger_num > 0:
                    for cluster in clusters:
                        if cluster['car'].surplus_sites > 0:
                            o = Order(
                                id_=order.id_,
                                passenger_num=cluster['car'].surplus_sites,
                                lng=order.lng,
                                lat=order.lat,
                                is_grab=order.is_grab
                            )
                            order.passenger_num -= o.passenger_num
                            cluster['car'].orders.append(o)
                            cluster['car'].change_surplus_sites(o.passenger_num)
                            result.append((o, cluster['car']))
                            break

        calculate_centroid(clusters)

        for cluster in clusters:  # 范围外
            for order in cluster['orders']:
                if order.is_grab == 0 and order.unsolved:
                    if cluster['car'].surplus_sites >= order.passenger_num:
                        order.unsolved = False
                        cluster['car'].orders.append(order)
                        cluster['car'].change_surplus_sites(order.passenger_num)
                        result.append((order, cluster['car']))
                        break

        calculate_centroid(clusters)

        for order in out_orders:  # 抢单二轮优化
            if order.unsolved:
                clusters.sort(
                    key=lambda cluster: get_distance(order.lng, order.lat, cluster['coordinate'][0],
                                                     cluster['coordinate'][1]))
                for cluster in clusters:
                    if cluster['car'].surplus_sites >= order.passenger_num and \
                            get_distance(cluster['coordinate'][0], cluster['coordinate'][1], order.lng,
                                         order.lat) <= order_distance:
                        order.unsolved = False
                        cluster['car'].orders.append(order)
                        cluster['car'].change_surplus_sites(order.passenger_num)
                        result.append((order, cluster['car']))
                        break

    if debug:
        data = []
        if type_ == 'receive':
            for car in debug_cars:
                temp = []
                for ret in result:
                    if ret[1].id_ == car.id_:
                        temp.append({
                            'order': {
                                'id': ret[0].id_, 'lnglat': [ret[0].lng, ret[0].lat],
                                'passenger_num': ret[0].passenger_num,
                                'is_grab': ret[0].is_grab
                            }
                        })

                if len(temp) > 0:
                    data.append({
                        'car': {'id': car.id_, 'sites': car.sites, 'lnglat': [car.lng, car.lat]},
                        'orders': temp
                    })
        else:
            for cluster in clusters:
                temp = []
                for order in cluster['car'].orders:
                    temp.append({
                        'order': {
                            'id': order.id_, 'lnglat': [order.lng, order.lat],
                            'passenger_num': order.passenger_num,
                            'is_grab': order.is_grab
                        }
                    })
                if len(temp) > 0:
                    data.append({
                        'car': {'id': cluster['car'].id_, 'sites': cluster['car'].sites,
                                'lnglat': [cluster['coordinate'][0], cluster['coordinate'][1]]},
                        'orders': temp
                    })

        return data
    else:
        push_data(result)


def run(mode: int, debug=False):
    if not have_data():
        return None

    result.clear()
    order_list, car_list, type_, order_distance, car_distance, reserve_rate = load_data(mode)
    must_cars, available_cars, available_orders = preprocess_data(car_list, order_list, reserve_rate)
    ret = schedule(must_cars, available_cars, available_orders, order_distance, car_distance, type_, debug=debug)
    if debug:
        return ret


def test_schedule(order_list, car_list, type_, order_distance, car_distance, reserve_rate):
    result.clear()
    must_cars, available_cars, available_orders = preprocess_data(car_list, order_list, reserve_rate)
    ret = schedule(must_cars, available_cars, available_orders, order_distance, car_distance, type_, debug=True)
    return ret


if __name__ == '__main__':
    run(1)
