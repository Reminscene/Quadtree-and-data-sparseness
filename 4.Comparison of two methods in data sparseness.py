import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
sns.set(style="whitegrid")  # 设置绘图风格darkgrid\whitegrid\dark\white\ticks
# 以下两句防止中文显示为窗格
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 处理中文乱码
plt.rcParams["axes.unicode_minus"] = False  # 坐标轴负号的处理
# 设置字体
font_legend = {'family' : 'Times New Roman','weight' : 'bold','size' : 20}
font_ticks = {'family' : 'Times New Roman','weight' : 'bold','size' : 20}
font_lable = {'family' : 'Times New Roman','weight' : 'bold','size' : 23}

# 导入数据，从excel中
fig, ax = plt.subplots(figsize=(16, 9), dpi=90)
tips = pd.read_excel(r'C://Users//张晨皓//Desktop//Quadtree//data//matching probability.xlsx')
# ax.set_ylim(0,1)

# 绘制分组小提琴图
sns.violinplot(x="Period", y="Matching probability", hue = "Quadtree",  data = tips, scale ='area',split = True,cut=0, palette = 'PiYG_r',linewidth = 0.8,saturation = 1.0)
# plt.title('小提琴图')

# 调整图例
# plt.legend(loc='upper left', ncol=2, title = 'Whether to use quadtree ?', framealpha = 0.5, prop=font_legend)

# 调整坐标轴信息
plt.xticks(fontsize = 15)  # 字号
plt.yticks(fontsize = 15)
plt.tick_params(pad = 1)  # 与坐标轴的距离
labels = ax.get_xticklabels() + ax.get_yticklabels()  # 字体
[label.set_fontname('Times New Roman') for label in labels]

# 调整标签信息
plt.xlabel('Period', font_lable, linespacing = 1, labelpad = 20)
plt.ylabel(r'Matching probability', font_lable, linespacing = 1, labelpad = 20)

# 显示图形
plt.savefig("C://Users//张晨皓//Desktop//Quadtree//figures//Comparison in data sparseness of matching probability.png")
plt.show()

