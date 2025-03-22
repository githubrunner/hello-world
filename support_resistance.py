import yfinance as yf
import pandas as pd
import scipy as sp
import mplfinance as mpf
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from stumpy.core import replace_distance

ticker = yf.Ticker('AAPL')

df = ticker.history( period='2y', interval='1d')
print(df.head)


# find strong resistance
strong_peak_distance = 60 # 60天
strong_peak_prominence = 20 # 显著性阈值
strong_peaks, _ = find_peaks(df['High'], distance=strong_peak_distance, prominence=strong_peak_prominence)
strong_peaks_values = df.iloc[strong_peaks]['High'].tolist()

yearly_high = df['High'].iloc[-252:].max()
strong_peaks_values.append(yearly_high)
print("strong peak : ", np.around(strong_peaks_values, decimals=3))

#find strong support
strong_troughs, _ = find_peaks(-df['Low'], distance=strong_peak_distance, prominence=strong_peak_prominence)
strong_troughs_values = df.iloc[strong_troughs]['Low'].tolist()
yearly_low = df['Low'].iloc[-252:].min()
strong_troughs_values.append(yearly_low)
print("strong trough : ", np.around(strong_troughs_values, decimals=3))



# 定义一般蜂值之间的距离（天数）
peak_distance = 5

# 定义峰值合并的宽度（垂直距席）
peak_rank_width = 2

# 定义支撑位最小反转次数
resistance_min_pivot_rank = 3

# 找到 高”价格数据中的峰值
peaks, _ = find_peaks(df['High'], distance=peak_distance)

# 初始化字d典以跟踪每个峰值的排名
peak_to_rank = {peak: 0 for peak in peaks}

# 遍历所有一般峰值，比较它们的接近程度并排名

for i, current_peak in enumerate(peaks) :
    current_high = df.iloc[current_peak]['High']
    for previous_peak in peaks[:i]:
        if abs(current_high - df.iloc[previous_peak]['High']) <= peak_rank_width:
            peak_to_rank[current_peak] += 1

#初始化包含强峰值的阻力位列表
resistances = strong_peaks_values.copy()

#遍历每个一般峰值，如果其排名达到阈值，则添加到阻力位列表
for peak, rank in peak_to_rank.items():
    if rank >= resistance_min_pivot_rank:
        resistances.append(df.iloc[peak]['High'] + 1e-3) # 添加小量以避免浮点精度问题

#对阻力位进行排序
resistances.sort()

# 合并接近的阻力位

resistance_bins = []
current_bin = [resistances[0]]
for r in resistances [1:]:
    if r - current_bin[-1] < peak_rank_width:
        current_bin.append (r)
    else:
        resistance_bins.append(current_bin)
        current_bin = [r]
resistance_bins.append(current_bin)

# 计算每个阻力位区间的平均值
final_resistances = [np.mean(bin) for bin in resistance_bins]
np.set_printoptions(precision=3)
print("一般阻力位：", np.around(final_resistances, decimals=3))

df.index = pd.to_datetime(df.index)
#fig = mpf.plot(df, type='candle', style='charles', title='AAPL Candlestick Chart', volume=True)

add_plot_resistence = [mpf.make_addplot(np.full(len(df), resistance), color='r') for resistance in strong_peaks_values]
#mpf.plot(df, type='candle', style='charles', title='AAPL Candlestick Chart with Strong resistance lines', volume=True, addplot=add_plot_resistence)

add_plot_support = [mpf.make_addplot(np.full(len(df), support), color='g') for support in strong_troughs_values]
temp = add_plot_resistence + add_plot_support

mpf.plot(df, type='candle', style='charles', title='AAPL Candlestick Chart with Strong support lines', volume=True, addplot=temp)