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

from schedule_utils.caculate_utils import k_means, get_distance, DP, find_closest_car
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


def abandon_order(orders: List[Order], center: List[float], max_dis: int):
    """
    放弃该簇中，范围外且距离簇心的距离大于最远距离的点
    :param orders:
    :param max_dis:
    :return:
    """
    for order in orders:
        if get_distance(center[0], center[1], order.lng, order.lat) > max_dis:
            return order
    return None


def term_weight(orders: List[Order], center: List[float], max_dis: int):
    """
    计算每个订单的权重
    :param orders:
    :param center:
    :param max_dis:
    :return:
    """
    new_orders = []
    for order in orders:
        if max_dis > 0:
            order.weight = ((max_dis - get_distance(center[0], center[1], order.lng, order.lat)) / max_dis) * 0.01 \
                           + (0.99 * order.passenger_num)
        else:
            order.weight = 0.99 * order.passenger_num
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


def new_schedule(cars: List[Car], orders: List[Order], reserve_rate: float, order_distance: int, car_distance: int,
                 type_: str, debug=False):
    # TODO 调试使用，生产环境删除
    debug_cars = []

    must_cars = []  # 已经抢过单的车辆
    must_clusters = []  # 组
    available_cars_num = 0  # 可用的车辆数量

    in_orders = []  # 范围内订单

    temp = []
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
            temp.append(order)

    for order in temp:
        orders.remove(order)

    for car in must_cars:
        cars.remove(car)

    # TODO 调试使用，生产环境删除
    debug_cars.extend(must_cars)

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
            orders.sort(
                key=lambda obj: get_distance(obj.lng, obj.lat, cluster["coordinate"][0], cluster["coordinate"][1])
            )
            for i in range(len(orders)):
                if orders[i].passenger_num <= car.surplus_sites and get_distance(
                        orders[i].lng,
                        orders[i].lat,
                        cluster['coordinate'][0],
                        cluster['coordinate'][1]
                ) <= order_distance:
                    o = orders.pop(i)
                    o.unsolved = False
                    car.change_surplus_sites(o.passenger_num)

                    car.orders.append(o)
                    result.append((o, car))
                    lng = 0
                    lat = 0
                    for order in car.orders:
                        lng += order.lng
                        lat += order.lat
                    cluster['coordinate'] = [lng / len(car.orders), lat / len(car.orders)]
                    break
            else:
                must_clusters.append(cluster)
                break

    must_passenger_num = 0  # 必须拉的乘客数量
    sites_num = 0
    for order in orders:
        if order.is_grab == 0 and order.unsolved is not False:
            must_passenger_num += order.passenger_num
            in_orders.append(order)

    if must_passenger_num > 0:
        for car in cars:
            sites_num += car.surplus_sites
            available_cars_num += 1
            if sites_num >= must_passenger_num:
                break

    for order in in_orders:
        orders.remove(order)

    clusters_in = k_means(in_orders, available_cars_num)

    for cluster in clusters_in:
        closest_car: Car = find_closest_car(cluster, cars, car_distance, type_)
        cluster['orders'] = term_weight(cluster['orders'], cluster['coordinate'], order_distance)
        cluster['car'] = closest_car
        result.extend(DP(closest_car, cluster["orders"]))

        # TODO 调试使用，生产环境删除
        if closest_car not in debug_cars:
            debug_cars.append(closest_car)

    must_clusters.extend(clusters_in)

    for order in in_orders:  # 一轮优化
        if order.unsolved:
            clusters_in.sort(
                key=lambda cluster: get_distance(order.lng, order.lat, cluster['coordinate'][0],
                                                 cluster['coordinate'][1]))
            for cluster in clusters_in:
                if cluster['car'].surplus_sites >= order.passenger_num:
                    order.unsolved = False
                    cluster['car'].orders.append(order)
                    cluster['car'].change_surplus_sites(order.passenger_num)
                    result.append((order, cluster['car']))
                    break

    calculate_centroid(clusters_in)

    for order in in_orders:  # 二轮优化
        if order.unsolved:
            must_clusters.sort(
                key=lambda cluster: get_distance(order.lng, order.lat, cluster['coordinate'][0],
                                                 cluster['coordinate'][1]))
            order.unsolved = False
            while order.passenger_num > 0:
                for cluster in clusters_in:
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
                else:
                    break

    calculate_centroid(clusters_in)

    for cluster in clusters_in:
        while True:
            orders.sort(key=lambda order: get_distance(order.lng, order.lat, cluster['coordinate'][0],
                                                       cluster['coordinate'][1]))
            for order in orders:
                if order.passenger_num <= cluster['car'].surplus_sites and get_distance(
                        order.lng,
                        order.lat,
                        cluster['coordinate'][0],
                        cluster['coordinate'][1]
                ) <= order_distance:
                    order.unsolved = False
                    cluster['car'].orders.append(order)
                    cluster['car'].change_surplus_sites(order.passenger_num)
                    orders.remove(order)
                    result.append((order, cluster['car']))
                    break
            else:
                break

    surplus_available_cars_num = math.floor((len(cars) - available_cars_num) * reserve_rate)

    clusters_out = None

    available_orders = copy.copy(orders)
    while True:
        surplus_passenger_num = 0  # 剩余乘客数量
        sites_num = 0
        available_cars_num = 0
        for order in available_orders:
            surplus_passenger_num += order.passenger_num

        if surplus_passenger_num > 0:
            for car in cars:
                sites_num += car.surplus_sites
                available_cars_num += 1
                if sites_num >= surplus_passenger_num:
                    break
        else:
            break
        if surplus_available_cars_num < available_cars_num:
            k = surplus_available_cars_num
        else:
            k = available_cars_num
        if k > len(available_orders):
            k = len(available_orders)
        clusters_out = k_means(available_orders, k)
        for cluster in clusters_out:
            obj = abandon_order(cluster['orders'], cluster['coordinate'], order_distance)
            if obj:
                available_orders.remove(obj)
                break
        else:
            surplus_available_cars_num -= k
            break

    if clusters_out:
        for cluster in clusters_out:
            closest_car: Car = find_closest_car(cluster, cars, car_distance, type_, is_grab=True)
            if closest_car:
                cluster['orders'] = term_weight(cluster['orders'], cluster['coordinate'], order_distance)
                cluster['car'] = closest_car
                result.extend(DP(closest_car, cluster["orders"]))

                # TODO 调试使用，生产环境删除
                if closest_car not in debug_cars:
                    debug_cars.append(closest_car)
                must_clusters.append(cluster)

        for cluster in clusters_out:
            while surplus_available_cars_num > 0:
                closest_car: Car = find_closest_car(cluster, cars, car_distance, type_, is_grab=True)
                if closest_car:
                    cluster['orders'] = term_weight(cluster['orders'], cluster['coordinate'], order_distance)
                    cluster['car'] = closest_car
                    r = DP(closest_car, cluster["orders"])
                    if len(r) == 0:
                        break
                    result.extend(r)
                    surplus_available_cars_num -= 1

                    # TODO 调试使用，生产环境删除
                    if closest_car not in debug_cars:
                        debug_cars.append(closest_car)
                    must_clusters.append(cluster)
                else:
                    break

    available_orders = []
    for order in orders:
        if order.unsolved:
            available_orders.append(order)
    if surplus_available_cars_num > 0:
        while True:
            surplus_passenger_num = 0  # 剩余乘客数量
            sites_num = 0
            available_cars_num = 0
            for order in available_orders:
                surplus_passenger_num += order.passenger_num

            if surplus_passenger_num > 0:
                for car in cars:
                    sites_num += car.surplus_sites
                    available_cars_num += 1
                    if sites_num >= surplus_passenger_num:
                        break
            else:
                break
            if surplus_available_cars_num < available_cars_num:
                k = surplus_available_cars_num
            else:
                k = available_cars_num
            if k > len(available_orders):
                k = len(available_orders)
            clusters_out = k_means(available_orders, k)

            for cluster in clusters_out:
                obj = abandon_order(cluster['orders'], cluster['coordinate'], order_distance)
                if obj:
                    available_orders.remove(obj)
                    break
            else:
                surplus_available_cars_num -= k
                break

        if clusters_out:
            for cluster in clusters_out:
                closest_car: Car = find_closest_car(cluster, cars, car_distance, type_, is_grab=True)
                if closest_car:
                    cluster['orders'] = term_weight(cluster['orders'], cluster['coordinate'], order_distance)
                    cluster['car'] = closest_car
                    result.extend(DP(closest_car, cluster["orders"]))

                    # TODO 调试使用，生产环境删除
                    if closest_car not in debug_cars:
                        debug_cars.append(closest_car)
                    must_clusters.append(cluster)

    # TODO 调试使用，生产环境删除
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
            for cluster in must_clusters:
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

    push_data(result)


def run(mode: int, debug=False):
    if not have_data():
        return None

    result.clear()
    order_list, car_list, type_, order_distance, car_distance, reserve_rate = load_data(mode)
    ret = new_schedule(car_list, order_list, reserve_rate, order_distance, car_distance, type_, debug=False)
    if debug:
        return ret


def test_schedule(order_list, car_list, type_, order_distance, car_distance, reserve_rate):
    result.clear()
    # must_cars, available_cars, available_orders = preprocess_data(car_list, order_list, reserve_rate, order_distance)
    # ret = schedule(must_cars, available_cars, available_orders, order_distance, car_distance, type_, debug=True)
    ret = new_schedule(car_list, order_list, reserve_rate, order_distance, car_distance, type_, debug=True)
    return ret


if __name__ == '__main__':
    run(1)
