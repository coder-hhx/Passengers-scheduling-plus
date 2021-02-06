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

from flask import Flask, render_template, jsonify

from new.data_utils import receive_data, send_data, load_data
from new.scheduling import schedule

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new_arithmetic/<mode>/')
def new_arithmetic(mode):
    result = schedule(mode)
    data = []
    for ret in result:
        data.append({
            "order": {'id': ret[0].id_, 'lnglat': [ret[0].lng, ret[0].lat]},
            "driver": {'id': ret[1].id_, 'lnglat': [ret[1].lng, ret[1].lat], 'site_num': ret[1].sites},
            "passenger_num": ret[0].passenger_num
        })

    return jsonify({
        'data': data
    })

    # if type_ == "receive":
    #     result = receive_type_calculate(available_orders, available_cars, order_distance, car_distance)
    #     data = []
    #     for ret in result:
    #         data.append({
    #             "order": {'id': ret[0].id_, 'lnglat': [ret[0].lng, ret[0].lat]},
    #             "driver": {'id': ret[1].id_, 'lnglat': [ret[1].lng, ret[1].lat], 'site_num': ret[1].sites},
    #             "passenger_num": ret[0].passenger_num
    #         })
    #
    #     return jsonify({
    #         'data': data
    #     })
    # elif type_ == "send":
    #     result = send_type_calculate(order_list, car_list, order_distance)
    #     data = []
    #     for car in cars:
    #         temp = []
    #         for ret in result:
    #             if ret[1].id_ == car.id_:
    #                 temp.append({
    #                     'id': ret[0].id_, 'lnglat': [ret[0].lng, ret[0].lat],
    #                     'passenger_num': ret[0].passenger_num
    #                 })
    #
    #         if len(temp) > 0:
    #             data.append(temp)
    #
    #     return jsonify({
    #         'data': data
    #     })


@app.route('/scene_change/<scene>/')
def scene_change(scene):
    if scene == "receive":
        receive_data()
        order_list, car_list, type_, order_distance, car_distance, reserve_rate = load_data(mode=int(1))
    else:
        send_data()
        order_list, car_list, type_, order_distance, car_distance, reserve_rate = load_data(mode=int(1))

    orders = [{"lnglat": [order.lng, order.lat], "id": order.id_, "passenger_num": order.passenger_num} for order in
              order_list]
    cars = [{"lnglat": [car.lng, car.lat], "id": car.id_, "site_num": car.sites} for car in car_list]

    return jsonify({
        'status': 200,
        'orders': orders,
        'cars': cars
    })


if __name__ == '__main__':
    app.run()
