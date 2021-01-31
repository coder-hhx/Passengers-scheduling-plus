import collections

from flask import Flask, render_template, jsonify

from tools.scheduling_tool import run

app = Flask(__name__)


@app.route('/')
def test():
    return render_template('test.html')


@app.route('/data')
def data():
    table = run(False)
    result = [[i[0][0], i[0][1], i[1]] for i in
              list(collections.Counter([(i[0]['id'], i[1]['id']) for i in table]).items())]

    lng = lat = count = 0
    for i in range(len(result)):
        for j in table:
            if result[i][0] == j[0]['id'] and result[i][1] == j[1]['id']:
                result[i] = {
                    "driver": {'id': result[i][0], 'lnglat': j[0]['coordinate']},
                    "passenger": {'id': result[i][1], 'lnglat': j[1]['coordinate']},
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


if __name__ == '__main__':
    app.run()
