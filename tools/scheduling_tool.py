# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# 一个调度系统。给出乘客的坐标，司机的坐标和座位数 返回乘客与司机的绑定关系


# %%
import numpy as np
import collections
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
import copy

from tools import caculate
from tools import redis_api
from tools.load_user_data import load_user_data
from tools.load_driver_data import load_driver_data, load_matrix_drivers


# %%
class officer(object):
    """
    调度员对象
    """

    def update_map(self):
        self.the_maps = caculate.kmeans(self.users)

    def load_data(self):
        self.users, self.drivers, self.max_distance, self.type = redis_api.pop()
        self.users_backup = copy.deepcopy(self.users)
        self.sites_count = sorted([i["sites"] for i in self.drivers])
        if (self.type == 'send'):
            self.matrix_drivers = load_matrix_drivers(self.users)
        self.drivers_backup = copy.deepcopy(self.drivers)
    # def update_users(self):
    #     self.users = load_user_data()
    #     self.users_backup = copy.deepcopy(self.users)
    # def update_drivers(self):
    #     self.drivers = load_driver_data()
    #     self.sites_count = sorted([i["sites"] for i in self.drivers])
    #     if (self.type == 'send'):
    #         self.matrix_drivers = load_matrix_drivers(self.users)
    #     self.drivers_backup = copy.deepcopy(self.drivers)


# %%
def draw(officer, table):
    """
    画出所有用户的位置

    参数
    ----------
    officer : 调度员对象
    table : 司机与乘客的绑定表
    """
    coordinates = [i["coordinate"] for i in officer.users_backup]
    x, y = zip(*coordinates)
    plt.scatter(x, y)
    # 画出所有司机的位置
    if officer.type == 'receive':
        coordinates = [i["coordinate"] for i in officer.drivers_backup]
        x, y = zip(*coordinates)
        plt.scatter(x, y, c='y')
    # 连接已经分配好的司机和用户
    for user, driver in table:
        x, y = zip(user["coordinate"], driver["coordinate"])
        plt.plot(x, y, color='b')
    plt.xticks(np.arange(104.000, 104.150, 0.025))
    plt.yticks(np.arange(30.600, 30.750, 0.025))
    plt.gca().set_aspect(1)
    plt.show()


# %%
def kmeans_distribute(officer):
    """
    基于Kmeans给司机分配乘客

    参数
    ----------
    officer : 调度员对象

    返回
    ----------
    table : 司机与乘客的绑定表
    """
    table = []
    if officer.debug:
        draw(officer, table)
    while officer.users != []:
        officer.update_map()
        # print(officer.the_maps)
        user_box = []
        # 取出一个中心点和最近的司机
        center = officer.the_maps.pop(0)
        if officer.type == "receive":
            closest_driver = caculate.find_closest_obj(center, officer.drivers)
            officer.drivers.remove(closest_driver)
        elif officer.type == "send":
            site = officer.sites_count.pop(0)
            closest_driver = caculate.find_closest_obj(center, officer.matrix_drivers[site])
            officer.matrix_drivers[site].remove(closest_driver)
        # 如果该中心的cluster的用户数量大于司机的座位数量
        if len(center["users"]) >= closest_driver["sites"]:
            # 把距离司机最近的用户分配给司机
            for i in range(closest_driver["sites"]):
                closest_user = caculate.find_closest_obj(closest_driver, center["users"])
                center["users"].remove(closest_user)
                table.append([closest_user, closest_driver])
                officer.users.remove(closest_user)
        else:
            # 还需要N个乘客才能填满座位
            need_another = closest_driver["sites"] - len(center["users"])
            # 把所有用户分配给司机
            for i in range(len(center["users"])):
                closest_user = caculate.find_closest_obj(closest_driver, center["users"])
                center["users"].remove(closest_user)
                table.append([closest_user, closest_driver])
                officer.users.remove(closest_user)
            # 再找N个乘客来填满座位
            for i in range(need_another):
                if officer.users != []:
                    closest_user = caculate.find_closest_obj(center, officer.users)
                    table.append([closest_user, closest_driver])
                    officer.users.remove(closest_user)
    # 绘图
    if officer.debug:
        draw(officer, table)
    return table


# table = kmeans_distribute(officer)


# %%
def optimize(officer, table):
    """
    优化绑定表

    参数
    ----------
    officer : 调度员对象
    table : 司机与乘客的绑定表

    返回
    ----------
    table : 优化后的司机与乘客的绑定表
    """
    table.sort(key=lambda e: e[1]["id"])
    for XXX in range(2):  # 多轮优化
        for idx in range(len(table)):
            point_a, point_a_driver = table[idx]
            # raw
            # 当前的路程和
            raw_distance_to_driver = caculate.geodesic(point_a, point_a_driver)
            raw_distance = [raw_distance_to_driver + caculate.geodesic(i[0], i[1]) for i in table]
            # 当前每个群组的均方差
            raw_mean_square_difference = []
            for line in table:
                users = [i[0] for i in table if i[1] == line[1]]
                raw_mean_square_difference.append(caculate.mean_square_difference(users))
            raw_mean_square_difference = list(np.array(raw_mean_square_difference) + caculate.mean_square_difference(
                [i[0] for i in table if i[1] == point_a_driver]))
            # now
            # 交换后的路程和
            all_distance_to_drivers = [caculate.geodesic(point_a, i[1]) for i in table]
            all_distance_to_point_a_driver = [caculate.geodesic(i[0], point_a_driver) for i in table]
            now_distance = zip(all_distance_to_drivers, all_distance_to_point_a_driver)
            now_distance = [sum(i) for i in now_distance]
            # 交换后每个群组的均方差
            now_mean_square_difference = []
            for e, line in enumerate(table):
                table_a = table[:idx] + [[line[0], point_a_driver]] + table[idx + 1:]
                table_a = table_a[:e] + [[point_a, line[1]]] + table_a[e + 1:]
                users_a = [i[0] for i in table_a if i[1] == point_a_driver]
                users_b = [i[0] for i in table_a if i[1] == line[1]]
                now_mean_square_difference.append(
                    caculate.mean_square_difference(users_a) + caculate.mean_square_difference(users_b))
            # 分别作差，加权求和
            distance_difference = np.array(raw_distance) - np.array(now_distance)
            std_difference = np.array(raw_mean_square_difference) - np.array(now_mean_square_difference)
            difference = list(distance_difference + std_difference * 40)
            # 对交换后效果最好的两个点进行交换
            if (max(difference) > 0.001):
                index_of_line_b = difference.index(max(difference))
                line_b = table[index_of_line_b]
                table[index_of_line_b] = [point_a, line_b[1]]
                table[idx] = [line_b[0], point_a_driver]
    # 绘图
    if officer.debug: draw(officer, table)
    return table


# table = optimize(officer, table)


# %%
def handel_too_far(officer, table, max_distance):
    """
    处理距离司机太远的乘客

    参数
    ----------
    officer : 调度员对象
    table : 司机与乘客的绑定表
    max_distance : 超过多远算太远

    返回
    ----------
    table : 新的司机与乘客的绑定表
    """
    too_far_users = [i[0] for i in table if caculate.geodesic(i[0], i[1]) > max_distance]
    while (too_far_users != []):
        # 从table里去掉太远的点，送回用户池
        officer.users = copy.deepcopy(too_far_users)
        table = [i for i in table if caculate.geodesic(i[0], i[1]) < max_distance]
        # 重新分配太远的点，追加在原表后面
        too_far = kmeans_distribute(officer)
        table = table + too_far
        if too_far_users == [i[0] for i in table if caculate.geodesic(i[0], i[1]) > max_distance]:
            break
        too_far_users = [i[0] for i in table if caculate.geodesic(i[0], i[1]) > max_distance]
    # 绘图
    if officer.debug: draw(officer, table)
    return table


# table = handel_too_far(officer, table, max_distance)


# %%
def fill_in_drivers(officer, table):
    """
    用真实司机替代虚拟司机

    参数
    ----------
    officer : 调度员对象
    table : 司机与乘客的绑定表

    返回
    ----------
    table : 新的司机与乘客的绑定表
    """
    maxtrix_drivers = list(set([(i[1]["id"], i[1]["sites"]) for i in table]))
    maxtrix_drivers.sort(key=lambda e: e[1])
    maxtrix_drivers = [i[0] for i in maxtrix_drivers]
    officer_drivers = [(i["id"], i["sites"]) for i in officer.drivers]
    officer_drivers.sort(key=lambda e: e[1])
    officer_drivers = [i[0] for i in officer_drivers]
    map_dict = dict(list(zip(maxtrix_drivers, officer_drivers)))
    new_table = []
    for u, d in table:
        d = copy.deepcopy(d)
        d["id"] = map_dict[d["id"]]
        new_table.append([u, d])
    # 绘图
    if officer.debug:
        draw(officer, table)
    return new_table


# table = fill_in_drivers(officer, table)


# %%
def run(debug=True):
    """
    运行

    参数
    ----------
    debug : 是否调试
    """
    pdw = officer()
    pdw.load_data()
    pdw.debug = debug
    table = kmeans_distribute(pdw)
    table = optimize(pdw, table)
    table = handel_too_far(pdw, table, pdw.max_distance)
    if pdw.type == 'send':
        table = fill_in_drivers(pdw, table)
    redis_api.push(table)
    return table


# %%

if __name__ == '__main__':
    table = run(False)
    result = [[i[0][0], i[0][1], i[1]] for i in
              list(collections.Counter([(i[0]['id'], i[1]['id']) for i in table]).items())]

    for i in range(len(result)):
        for j in table:
            if result[i][0] == j[0]['id'] and result[i][1] == j[1]['id']:
                result[i] = {
                    "driver": {'id': result[i][0], 'lnglat': j[0]['coordinate']},
                    "passenger": {'id': result[i][1], 'lnglat': j[1]['coordinate']},
                    "passenger_num": result[i][2]
                }
                break

    print(result)
