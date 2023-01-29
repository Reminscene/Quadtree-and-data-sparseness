# 靡不有初，鲜克有终
# 开发时间：2022/6/27 11:09
# 靡不有初，鲜克有终
# 开发时间：2022/6/25 11:52
import pandas as pd
import numpy as np
import copy
import time
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import Geometry
from shapely import geometry
pd.set_option('display.max_columns', None)
"""—————————————————————————————————————————————————————调取数据——————————————————————————————————————————————————————"""
print("读取数据中... ...")
fpath = "C:/Users/张晨皓/Desktop/2022TRB投稿内容/分小时数据/hour23.txt"
Taxi_df = pd.read_csv(fpath, sep=",")
print(Taxi_df)

fpath = "C:/Users/张晨皓/Desktop/2022TRB投稿内容/分小时数据/24DataFrame_O.txt"
Pickup_df = pd.read_csv(fpath, sep=",")

Pickup_df['Time'] = pd.to_datetime(Pickup_df['Time'], errors='raise', yearfirst=True)  # 将时间转化成datetime形式
Pickup_df = Pickup_df.sort_values(by=["Taxi_ID", "Time"]).copy()   # 按照车辆ID和时间进行排序
Pickup_df['Hour'] = Pickup_df['Time'].apply(lambda x: x.hour)  # 在原数据中增加一列'Hour'，至此可以根据Hour的取值进行筛选groupby
Pickup_df_df_hour0 = Pickup_df.groupby("Hour").get_group(0).copy().reset_index()
Pickup_df_df_hour0.drop(labels = ['index','Unnamed: 0','Unnamed: 0.1'], axis = 1,inplace = True)
print(Pickup_df_df_hour0)

"""——————————————————————————————————————————————将每个OD-trip生成线————————————————————————————————————————————————————"""


def find_carry_trip(data):  # 找车辆载客的trip对应的index，输出[[start_index,end_index],[],[],[]]
    origin = []  # O点索引的集合
    destination = []  # D点索引的集合
    carry_trip_lst = []
    for i in range(1, len(data)):
        status = data.loc[i, 'Occupancy_Status']
        status_last = data.loc[i - 1, 'Occupancy_Status']
        if status > status_last:
            origin.append(i)
        elif status < status_last:
            destination.append(i)
    if len(destination) != 0 and len(origin) != 0:
        if origin[0] > destination[0]:
            destination.pop(0)
        origin_new = copy.deepcopy(origin[0:min(len(origin), len(destination))-1:1])
        destination_new = copy.deepcopy(destination[0:min(len(origin), len(destination))-1:1])  # 得到项数相同的，包含O点、D点的列表
        for i in range(0, len(origin_new)):
            carry_trip_lst.append([origin_new[i], destination_new[i]])
    return carry_trip_lst


def find_vacant_trip(data):  # 找车辆空驶的trip对应的index，输出[[start_index,end_index],[],[],[]]
    origin = []  # O点索引的集合
    destination = []  # D点索引的集合
    vacant_trip_lst = []
    for i in range(1, len(data)):
        status = data.loc[i, 'Occupancy_Status']
        status_last = data.loc[i - 1, 'Occupancy_Status']
        if status > status_last:
            origin.append(i)
        elif status < status_last:
            destination.append(i)
    if len(destination) !=0 and len(origin) !=0:
        if destination[0] > origin[0]:
            origin.pop(0)
        destination_new = copy.deepcopy(destination[0:min(len(origin), len(destination))-1:1])  # 得到项数相同的，包含O点、D点的列表
        origin_new = copy.deepcopy(origin[0:min(len(origin), len(destination)) - 1:1])
        for i in range(0, len(origin_new)):
            vacant_trip_lst.append([destination_new[i], origin_new[i]])
    return vacant_trip_lst  # 输出[[start_index,end_index],[],[],[]]
# print(find_carry_trip(Taxi_df))
# print(find_vacant_trip(Taxi_df))


class ReadGPSData:
    def __init__(self, GPS_data):  # 类属性
        self.GPS_data = "C:/Users/张晨皓/Desktop/2022TRB投稿内容/分小时数据/hour23.txt"
        print("正在读取GPS数据中...")


    def rade_trip(self):  # 针对trip类的【实例方法】
        self.vacant_trip_lst = []  # 里面的每一个元素是一个trip类
        self.carry_trip_lst = []
        self.vacant_trip_gdf_lst = []  # 用来存储多段线的，结构为[ [(x1,y1),(x2,y2),...,(xn,yn)],..., [(x1,y1),(x2,y2),...,(xn,yn)] ]
        self.carry_trip_gdf_lst = []
        with open(self.GPS_data, "r") as fl_GPS_data:
            GPS_data = pd.read_csv(fl_GPS_data)
            vehicle_lst = pd.unique(GPS_data['Taxi_ID'])  # 车辆编号的列表，储存在vehicle_lst中
            print("读取的GPS_data结果为:")
            print(GPS_data)
            for i in vehicle_lst:
                new_df = copy.deepcopy(GPS_data.groupby('Taxi_ID').get_group(i).reset_index())  # 分组、提取目标组别、重置索引
                a = find_vacant_trip(new_df)  # 空驶trip起始点坐标
                b = find_carry_trip(new_df)  # 载客trip起始点坐标
                for j in range(0, len(a)):  # 空驶trip的数量
                    vt = Vacant_Trip()  # 建立Vacant_Trip的【实例对象】
                    vt.start_x = new_df.loc[a[j][0], 'Longitude']
                    vt.start_y = new_df.loc[a[j][0], 'Latitude']
                    vt.end_x = new_df.loc[a[j][1], 'Longitude']
                    vt.end_y = new_df.loc[a[j][1], 'Latitude']
                    lst = []
                    for k in range(a[j][0], a[j][1]+1):
                        lst.append((new_df.loc[k, 'Longitude'], new_df.loc[k, 'Latitude']))
                    vt.line = geometry.LineString(lst)
                    vt.line_gdf = gpd.GeoSeries([geometry.LineString(lst)])
                    self.vacant_trip_gdf_lst.append(lst)
                    self.vacant_trip_lst.append(vt)

                for l in range(0, len(b)):  # 载客trip的数量
                    ct = Carry_Trip()  # 建立Carry_Trip的【实例对象】
                    ct.start_x = new_df.loc[b[l][0], 'Longitude']
                    ct.start_y = new_df.loc[b[l][0], 'Latitude']
                    ct.end_x = new_df.loc[b[l][1], 'Longitude']
                    ct.end_y = new_df.loc[b[l][1], 'Latitude']
                    lst = []
                    for m in range(b[l][0], b[l][1] + 1):
                        lst.append((new_df.loc[m, 'Longitude'], new_df.loc[m, 'Latitude']))  # 单个[(x,y),(x,y)]
                    ct.line = geometry.LineString(lst)
                    ct.line_gdf = gpd.GeoSeries([geometry.LineString(lst)])
                    self.carry_trip_gdf_lst.append(lst)
                    self.carry_trip_lst.append(ct)


class Vacant_Trip:  # 建立空驶的trip类
    def __init__(self):
        self.line = None  # 是单个的geometry元素，是后续得到GeoDataFrame，进而实现空间连接的基础
        self.line_gdf = None  # 用列表来储存中间结点的坐标（坐标用元组表示，（x，y）），为直接画多段线服务的，是后续得到GeoSeries的基础
        self.start_x = None  # 行程起始点的x坐标
        self.start_y = None  # 行程起始点的y坐标
        self.end_x = None
        self.end_y = None


class Carry_Trip:  # 建立载客的trip类
    def __init__(self):
        self.line = None
        self.line_gdf = None
        self.start_x = None  # 行程起始点的x坐标
        self.start_y = None  # 行程起始点的y坐标
        self.end_x = None
        self.end_y = None


GPS_data = ReadGPSData(0)
print(GPS_data.rade_trip())  # 读取文件
vacant_trip_gpd = gpd.GeoSeries([geometry.MultiLineString(GPS_data.vacant_trip_gdf_lst)])
carry_trip_gpd = gpd.GeoSeries([geometry.MultiLineString(GPS_data.carry_trip_gdf_lst)])

"""————————————————————————————————————————————基于空驶轨迹的四叉树网格划分———————————————————————————————————————————————"""
# 定义正方形类（子节点）


class Square:

    def __init__(self, lx, ly, rx, ry):  # lx、ly为左上角坐标(x对应行号，y对应列号)，rx、ry为右下角坐标，用经纬度表示
        self.lx = lx
        self.ly = ly
        self.rx = rx
        self.ry = ry
        self.square = geometry.Polygon([(lx, ry), (lx, ly), (rx, ly), (rx, ry)])
        self.square_gdf = gpd.GeoDataFrame([geometry.Polygon([(lx, ry), (lx, ly), (rx, ly), (rx, ry)])], geometry=0)
        self.join_data = gpd.sjoin(self.square_gdf, Line_GDF, op='intersects')
        self.Trip_count = len(self.join_data)  # 包含的 GPS点的数量
        self.side_length = int(abs(111000 * (self.lx - self.rx)))  # 边长，米

    def check(self):
        if self.side_length <= min_size:  # 停止分裂后用列表存储正方形
            return True
        if self.Trip_count >= Trip_amount:
            return False
        return True

    # 打印正方形的坐标
    def print(self):
        print("lx:", self.lx, end=", ")
        print("ly:", self.ly, end=", ")
        print("rx:", self.rx, end=", ")
        print("ry:", self.ry, end=", ")
        print("GPS_count:", self.Trip_count, end=", ")
        print("side_length:", self.side_length)


def check_all(square_arr):
    for i in range(len(square_arr)):
        if square_arr[i].check() == False:
            return square_arr[i], i
    return None, -1


def get_quad_tree(square_arr):  # 将不符合要求的子节点进一步分裂为4个子节点
    a = 1
    while(True):
        problem_square, index = check_all(square_arr)
        if problem_square == None:
            break
        lx = problem_square.lx
        ly = problem_square.ly
        rx = problem_square.rx
        ry = problem_square.ry  # 将问题square进行四等分，顺序为左上divide_square1→右上divide_square2→左下divide_square3→右下divide_square4

        divide_square1 = Square(lx, ly, (lx+rx)/2, (ly+ry)/2)
        divide_square2 = Square((lx+rx)/2, ly, rx, (ly+ry)/2)
        divide_square3 = Square(lx, (ly+ry)/2, (lx+rx)/2, ry)
        divide_square4 = Square((lx+rx)/2, (ly+ry)/2, rx, ry)

        # 删除父节点，把新的四个子结点加进列表（将上层子节点变为对应的4个子节点）
        del square_arr[index]
        '''print("进行第", a, '次子节点分裂')'''
        square_arr.append(divide_square1)
        square_arr.append(divide_square2)
        square_arr.append(divide_square3)
        square_arr.append(divide_square4)
        a = a+1
    return square_arr


"""———————————————————————————————————————————————————函数外基本参数———————————————————————————————————————————————————"""
# 研究区域
Longitude_max = 114.6167
Longitude_min = 113.7667
Latitude_max = 22.867
Latitude_min = 22.45
# 研究区域的经纬度范围（左上顶点经度，左上顶点纬度，右下顶点经度，右下顶点纬度）
square_lst = []  # 用于存放（叶子节点）正方形gdf的列表
line_lst = []  # 用于存放空驶出租车轨迹的gdf的列表
carry_lst = []  # 用于存放空驶出租车轨迹的gdf的列表
for i in range(0, len(GPS_data.vacant_trip_lst)):
    line_lst.append(GPS_data.vacant_trip_lst[i].line)
Line_GDF = gpd.GeoDataFrame(line_lst, geometry=0)
print(Line_GDF)

for i in range(0, len(GPS_data.carry_trip_lst)):
    carry_lst.append(GPS_data.carry_trip_lst[i].line)
carry_Line_GDF = gpd.GeoDataFrame(carry_lst, geometry=0)


min_size = 600  # 网格最小尺寸,米
Trip_amount = 10  # 每个网格内GPS点的数量不得高于GPS_amount个
parent_square = Square(Longitude_min, Latitude_max, Longitude_max, Latitude_min)
square_arr = [parent_square]
square_arr = get_quad_tree(square_arr)

"""—————————————————————————————————————————————————转为json文件—————————————————————————————————————————————————————"""
print("共划分为", len(square_arr), "个网格")
for i in square_arr:
    square_lst.append(i.square)
Square_GDF = gpd.GeoDataFrame(square_lst, geometry=0)
print(Square_GDF)


with open('D://状态升维马尔可夫计算（四叉树-大案例）//空驶轨迹//23-24空驶轨迹.json', 'w') as f:
    f.write(Line_GDF.to_json())

with open('D://状态升维马尔可夫计算（四叉树-大案例）//载客轨迹//23-24载客轨迹.json', 'w') as f:
    f.write(carry_Line_GDF.to_json())


with open('D://状态升维马尔可夫计算（四叉树-大案例）//网格划分边界//23-24网格.json', 'w') as f:
    f.write(Square_GDF.to_json())



