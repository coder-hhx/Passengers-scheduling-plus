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

import collections
import copy
import json

from flask import Flask, render_template, jsonify

from new.data_utils import receive_data, send_data, load_data
from new.scheduling import receive_type_calculate, send_type_calculate
from old.scheduling_tool import run

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/old_arithmetic')
def old_arithmetic():
    table = run(False)
    result = [[i[0][0], i[0][1], i[1]] for i in
              list(collections.Counter([(i[0]['id'], i[1]['id']) for i in table]).items())]

    lng = lat = count = 0
    for i in range(len(result)):
        for j in table:
            if result[i][0] == j[0]['id'] and result[i][1] == j[1]['id']:
                result[i] = {
                    "order": {'id': result[i][0], 'lnglat': j[0]['coordinate']},
                    "driver": {'id': result[i][1], 'lnglat': j[1]['coordinate'], 'site_num': j[1]['sites']},
                    "passenger_num": result[i][2]
                }
                lng += j[0]['coordinate'][0] + j[1]['coordinate'][0]
                lat += j[0]['coordinate'][1] + j[1]['coordinate'][1]
                count += 2
                break

    return jsonify({
        'data': result,
        'center': [lng / count, lat / count]
    })


@app.route('/new_arithmetic/<mode>/')
def new_arithmetic(mode):
    order_list, car_list, max_distance, type_ = load_data(mode=int(mode))

    cars = copy.deepcopy(car_list)

    if type_ == "receive":
        result = receive_type_calculate(order_list, car_list, max_distance)
        data = []
        lng = lat = count = 0
        for ret in result:
            data.append({
                "order": {'id': ret[0].id_, 'lnglat': [ret[0].lng, ret[0].lat]},
                "driver": {'id': ret[1].id_, 'lnglat': [ret[1].lng, ret[1].lat], 'site_num': ret[1].sites},
                "passenger_num": ret[0].passenger_num
            })
            lng += ret[0].lng + ret[1].lng
            lat += ret[0].lat + ret[1].lat
            count += 2

        return jsonify({
            'data': data,
            'center': [lng / count, lat / count]
        })
    elif type_ == "send":
        result = send_type_calculate(order_list, car_list, max_distance)
        data = []
        lng = lat = count = 0
        for car in cars:
            temp = []
            for ret in result:
                if ret[1].id_ == car.id_:
                    temp.append({
                        'id': ret[0].id_, 'lnglat': [ret[0].lng, ret[0].lat],
                        'passenger_num': ret[0].passenger_num
                    })
                    lng += ret[0].lng
                    lat += ret[0].lat
                    count += 1

            if len(temp) > 0:
                data.append(temp)

        return jsonify({
            'data': data,
            'center': [lng / count, lat / count]
        })


@app.route('/scene_change/<scene>/')
def scene_change(scene):
    if scene == "receive":
        receive_data()
    elif scene == "send":
        send_data()

    return jsonify({
        'status': 200
    })


if __name__ == '__main__':
    app.run()
