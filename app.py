# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project Name: Passengers-scheduling-plus
File Name: app.py
Author: hhx
Contact: houhaixu_email@163.com
Create Date: 2021/1/31
-------------------------------------------------
"""
import json
from typing import List

from flask import Flask, render_template, jsonify, request

from schedule_utils.data_utils import receive_data, send_data, load_data
from schedule_utils.models import Car, Order
from schedule_utils.scheduling import run, test_schedule

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/schedule/<mode>/')
def schedule(mode):
    result = run(int(mode), debug=True)

    if result is None:
        return jsonify({'status': 500})
    return jsonify({
        'status': 200,
        'data': result
    })


@app.route('/test/', methods=["POST"])
def test():
    try:
        data_txt = str(request.form["data_txt"])
        order_distance = int(request.form["order_distance"])
        car_distance = int(request.form["car_distance"])
        reserve_rate = float(request.form["reserve_rate"])
        type_ = str(request.form["data_type"])
        mode = int(request.form["mode"])

        data = json.loads(data_txt)

        car_list: List[Car] = []  # 车辆列表
        order_list: List[Order] = []  # 订单列表

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

        result = test_schedule(order_list, car_list, type_, order_distance, car_distance, reserve_rate)
        return jsonify({
            'status': 200,
            'data': result
        })

    except Exception as e:
        print(e)
        return jsonify({
            'status': 500
        })
    pass


@app.route('/scene_change/<scene>/')
def scene_change(scene):
    if scene == "receive":
        receive_data()
        order_list, car_list, type_, order_distance, car_distance, reserve_rate = load_data(1)
        receive_data()
    else:
        send_data()
        order_list, car_list, type_, order_distance, car_distance, reserve_rate = load_data(1)
        send_data()

    orders = [{"lnglat": [order.lng, order.lat], "id": order.id_, "passenger_num": order.passenger_num,
               "is_grab": order.is_grab} for order in
              order_list]
    cars = [{"lnglat": [car.lng, car.lat], "id": car.id_, "site_num": car.sites} for car in car_list]

    return jsonify({
        'status': 200,
        'orders': orders,
        'cars': cars
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)
