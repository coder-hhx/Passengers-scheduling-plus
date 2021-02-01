import json
from typing import List

import redis

from new.models import Car, Order

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def load_data():
    car_list: List[Car] = []
    order_list: List[Order] = []

    data = json.loads(r.get('data'))
    max_distance = int(data["config"]["far_distance"])
    _type = data["config"]["type"]

    for order in data['user_list']:
        order_list.append(
            Order(
                _id=int(order['id']),
                passenger_num=int(order['size']),
                lng=float(order['coordinate']['lng']),
                lat=float(order['coordinate']['lat'])
            )
        )

    for car in data['driver_list']:
        car_list.append(
            Car(
                _id=int(car['id']),
                lng=float(car['coordinate']['lng']),
                lat=float(car['coordinate']['lat']),
                sites=int(car['sites'])
            )
        )
