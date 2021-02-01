# 随机坐标点生成器

# X = np.loadtxt(r'pdw_data.txt')
# print(np.max(X[:,0]), np.min(X[:,0]))
# print(np.max(X[:,1]), np.min(X[:,1]))
# 
# 104.147461 104.004307
# 30.740067 30.604392
import random
import numpy as np
import itertools


def random_coordinates_generator(length, xRange=(104.15, 104.00), yRange=(30.75, 30.60)):
    """
    生成随机点
    """
    x = [random.uniform(xRange[0], xRange[1]) for i in range(length)]
    y = [random.uniform(yRange[0], yRange[1]) for i in range(length)]
    coordinates = [list(i) for i in zip(x, y)]
    return coordinates

def matrix_coordinates_generator(xRange=(104.15, 104.00), yRange=(30.75, 30.60)):
    """
    生成矩阵点
    """
    x = np.arange(xRange[1], xRange[0], 0.003)
    y = np.arange(yRange[1], yRange[0], 0.003)
    coordinates = [list(i) for i in itertools.product(x,y)]
    return coordinates
