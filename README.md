# Passengers-scheduling-plus
乘客调度算法-改进版使用方法

1、安装依赖，在项目根目录下，打开cmd，或用Pycharm打开Terminal

```
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
```

2、redis数据库开启的情况下，输入启动命令

```
flask run
```

3、浏览器中，打开“127.0.0.1:5000”

4、先点击右下角的场景按钮，然后点击开始调度按钮

5、存入redis中的数据格式与上一版相同，((订单id， 车辆id)， 订单人数)

```
[
	((12, 3), 1), 
	((3, 6), 2), 
	((2, 4), 3), 
	……
]
```

