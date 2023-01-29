import pandas as pd
import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import geometry
pd.set_option('display.max_columns', None)

Longitude_max = 114.6167
Longitude_min = 113.7667
Latitude_max = 22.867
Latitude_min = 22.45
Longitude_delta = Longitude_max - Longitude_min
Latitude_delta = Latitude_max - Latitude_min
min_delta = min(Longitude_delta, Latitude_delta)
a = 0  # 列表lst的的 index，也是网格的数量
n = 17 # 最短边上划分成n个小网格
l = min_delta/n  # 网格中的小正方形边长（经纬度表示）
col = int((Longitude_delta*n)/min_delta)  # 网格的总列数
row = int((Latitude_delta*n)/min_delta)  # 网格的总行数
uniform_series = []  # 用于储存GeoSeries小正方形的一维列表
# 向空列表 lst 中不断填写更新GeoSeries
for i in range(0, col):
    for j in range(0, row):
        uniform_series.append(geometry.Polygon([(Longitude_min+i*l, Latitude_min+j*l), (Longitude_min+i*l, Latitude_min+(j+1)*l), (Longitude_min + (i+1)*l, Latitude_min +(j+1)*l), (Longitude_min + (i+1)*l, Latitude_min+ j*l)]))
        a = a+1
# print(Square_Series)
grid_uniform_gdf = gpd.GeoDataFrame(uniform_series, geometry=0)

"""———————————————————————————————————————————————————调取接客点数据————————————————————————————————————————————————————"""
fpath = "C://Users//张晨皓//Desktop//Quadtree//data//24DataFrame_O.txt"
Pickup_df = pd.read_csv(fpath, sep=",")

Pickup_df['Time'] = pd.to_datetime(Pickup_df['Time'], errors='raise', yearfirst=True)  # 将时间转化成datetime形式
Pickup_df = Pickup_df.sort_values(by=["Taxi_ID", "Time"]).copy()   # 按照车辆ID和时间进行排序
Pickup_df['Hour'] = Pickup_df['Time'].apply(lambda x: x.hour)  # 在原数据中增加一列'Hour'，至此可以根据Hour的取值进行筛选groupby
Pickup_df_df_hour0 = Pickup_df.groupby("Hour").get_group(23).copy().reset_index()  # 改这里！！
Pickup_df_df_hour0.drop(labels = ['index','Unnamed: 0','Unnamed: 0.1'], axis = 1,inplace = True)

"""—————————————————————————————————————————GDF——————————————————————————————————————————————"""
Pickup_GDF = gpd.GeoDataFrame(Pickup_df_df_hour0, geometry=gpd.points_from_xy(Pickup_df_df_hour0.Longitude, Pickup_df_df_hour0.Latitude))

with open("C://Users//张晨皓//Desktop//Quadtree//data//0-1Vacant trajectory.json",'r',encoding='utf8') as fp:
    line_json = json.load(fp)
    line_gdf = gpd.GeoDataFrame.from_features(line_json["features"])

"""———————————————————————————————————————————————————空间连接————————————————————————————————————————————————————"""

'''空间连接【hour0的接客点&网格】'''
# 空间连接结果用join_gp表示，grid+point
join_gp = gpd.sjoin(grid_uniform_gdf, Pickup_GDF, op='intersects')
join_gp["Square_ID"] = join_gp.index
Amount_GDF_gp = gpd.GeoDataFrame(join_gp.groupby("Square_ID").size(),)  # 建立一个不同网格的数据点数量的GeoDataFrame,名叫Amount_GDF_gp
Amount_GDF_gp.rename(columns={0: 'Point_Amount'}, inplace=True)  # 对Amount_GDF_gp里面的“0”列进行重命名，叫“Point_Amount”
grid_uniform_gdf['Point_Amount'] = Amount_GDF_gp['Point_Amount']  # 在grid_gdf里面增加新列，数据来自Amount_GDF_gp（GeoDataFrame）的'Point_Amount'列
grid_uniform_gdf.fillna(0, inplace=True)  # 填充空置，赋值为0

'''继续空间连接【hour0的空驶轨迹&网格】'''
join_gl = gpd.sjoin(grid_uniform_gdf, line_gdf, op='intersects')
join_gl["Square_ID"] = join_gl.index
Amount_GDF_gl = gpd.GeoDataFrame(join_gl.groupby("Square_ID").size(),)  # 建立一个不同网格的数据点数量的GeoDataFrame,名叫Amount_GDF_gl
Amount_GDF_gl.rename(columns={0: 'Line_Amount'}, inplace=True)  # 对Amount_GDF_gl里面的“0”列进行重命名，叫“Line_Amount”
grid_uniform_gdf['Line_Amount'] = Amount_GDF_gl['Line_Amount']  # 在grid_gdf里面增加新列，数据来自Amount_GDF_gl（GeoDataFrame）的'Line_Amount'列
grid_uniform_gdf.fillna(0, inplace=True)  # 填充空置，赋值为0
print(grid_uniform_gdf)

'''计算各个网格的匹配概率'''
grid_uniform_gdf['Matching_Prob'] = 0
for i in range(0, len(grid_uniform_gdf)):
    if grid_uniform_gdf.loc[i, 'Line_Amount'] == 0 and grid_uniform_gdf.loc[i, 'Point_Amount'] != 0:  # 将没有空驶轨迹，但有接客点的网格，接客点数量修正成0
        grid_uniform_gdf.loc[i, 'Point_Amount'] = 0
    if (grid_uniform_gdf.loc[i, 'Line_Amount']+grid_uniform_gdf.loc[i, 'Point_Amount']) != 0:
        grid_uniform_gdf.loc[i, 'Matching_Prob'] = grid_uniform_gdf.loc[i, 'Point_Amount'] /(grid_uniform_gdf.loc[i, 'Point_Amount']+grid_uniform_gdf.loc[i, 'Line_Amount'])

"""——————————————————————————————————————————————保存人车匹配概率至文本——————————————————————————————————————————————————"""
file = open("C://Users//张晨皓//Desktop//Quadtree//data//0-1matching probability_uniform.txt", 'w').close()  # 每次写入前清空文本文件的内容
file_handle = open("C://Users//张晨皓//Desktop//Quadtree//data//0-1matching probability_uniform.txt", mode='a')  # 将结果不断写入文本文件中！
k = 0
for i in range(0, len(grid_uniform_gdf)):
    file_handle.write(str(grid_uniform_gdf.loc[i, 'Matching_Prob']))
    file_handle.write('\n')  # 写入计算结果
    k = k + 1
file_handle.close()  # 关闭文件

"""————————————————————————————————————————————————————————可视化—————————————————————————————————————————————————————"""
Longitude_max = 114.6167
Longitude_min = 113.7667
Latitude_max = 22.867
Latitude_min = 22.45
fig, ax = plt.subplots(figsize=(16, 9), dpi=90)
# plt.title(" ")  # 给图像增加标题
plt.xlim(xmax=Longitude_max, xmin=Longitude_min)  # 调节输出图像x和y的上下限
plt.ylim(ymax=Latitude_max, ymin=Latitude_min)
ax = grid_uniform_gdf.plot(ax=ax, vmin=0, vmax=1, column='Matching_Prob', cmap='Reds', legend=True)  # 将匹配概率的数据用红色Reads进行展示

ax = grid_uniform_gdf.plot(ax=ax, label='grid', lw=0.5, edgecolor='k', facecolor='None')  # 网格
#ax = line_gdf.plot(ax=ax, label='vacant_trip', lw=0.3, edgecolor='red', facecolor='None')  # 线
# ax = Pickup_GDF.plot(ax=ax, label='vacant_trip', alpha=1, markersize=0.5, c='g')  # 点
# plt.legend()
plt.xlabel("Longitude")
plt.ylabel("Latitude")
shenzhen = gpd.GeoDataFrame.from_file('C://Users//张晨皓//Desktop//Quadtree//data//Shenzhenshi.json')
ax = shenzhen.plot(ax=ax, facecolor='None')
plt.savefig("C://Users//张晨皓//Desktop//Quadtree//figures//0-1Matching probability_uniform.png")
plt.show()

for i in range(0, len(grid_uniform_gdf)):
    print(grid_uniform_gdf.loc[i, 'Matching_Prob'])







