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

from schedule_utils.data_utils import receive_data, send_data, load_data
from schedule_utils.scheduling import run

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
    app.run(host="0.0.0.0", port=8888)
