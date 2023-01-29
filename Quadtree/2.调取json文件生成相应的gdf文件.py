# 靡不有初，鲜克有终
# 开发时间：2022/6/27 10:35
import pandas as pd
import json
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
fpath = "C:/Users/张晨皓/Desktop/2022TRB投稿内容/分小时数据/hour0.txt"
Taxi_df = pd.read_csv(fpath, sep=",")
# print(Taxi_df)

with open("D://状态升维马尔可夫计算（四叉树-大案例）//空驶轨迹//0-1空驶轨迹.json",'r',encoding='utf8') as fp:
    line_json = json.load(fp)
    line_gdf = gpd.GeoDataFrame.from_features(line_json["features"])


with open("D://状态升维马尔可夫计算（四叉树-大案例）//载客轨迹//0-1载客轨迹.json",'r',encoding='utf8') as fp:
    carry_line_json = json.load(fp)
    carry_line_gdf = gpd.GeoDataFrame.from_features(carry_line_json["features"])

with open("D://状态升维马尔可夫计算（四叉树-大案例）//网格划分边界//0-1网格.json",'r',encoding='utf8') as fp:
    grid_json = json.load(fp)
    grid_gdf = gpd.GeoDataFrame.from_features(grid_json["features"])

"""—————————————————————————————————————————————————————可视化——————————————————————————————————————————————————————"""
Longitude_max = 114.6167
Longitude_min = 113.7667
Latitude_max = 22.867
Latitude_min = 22.45
fig, ax = plt.subplots(figsize=(16, 9), dpi=90)
# plt.title(" ")  # 给图像增加标题
plt.xlim(xmax=Longitude_max, xmin=Longitude_min)  # 调节输出图像x和y的上下限
plt.ylim(ymax=Latitude_max, ymin=Latitude_min)
ax = grid_gdf.plot(ax=ax, label='grid', lw=0.5, edgecolor='k', facecolor='None')  # lw线宽
ax = line_gdf.plot(ax=ax, label='vacant_trip', lw=0.3, edgecolor='red', facecolor='None')  # lw线宽
ax = carry_line_gdf.plot(ax=ax, label='carry_trip', lw=0.3, edgecolor='blue', facecolor='None')  # lw线宽
plt.legend()
plt.xlabel("Longitude")
plt.ylabel("Latitude")
shenzhen = gpd.GeoDataFrame.from_file('C:\\Users\\张晨皓\\Desktop\\Data_Mining\\Shenzhenshi.json')  # 导入深圳市的json底图，如果投影可以crs='EPGS:2401
ax = shenzhen.plot(ax=ax, facecolor='None')
plt.savefig('C:\\Users\\张晨皓\\Desktop\\Data_Mining\\Grids.png')
print("总网格数:", len(grid_gdf))
plt.show()