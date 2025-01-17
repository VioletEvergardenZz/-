import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from wordcloud import STOPWORDS, WordCloud
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures

# 环境和参数的配置
def set_seaborn_properties(context='talk', font_scale=0.8):
    sns.set_theme(context=context, font='STXIHEI', font_scale=font_scale,
                  rc={'axes.unicode_minus': False,
                      'figure.figsize': (12, 8),
                      'figure.dpi': 150})

# 获取2020年国家地区数据封装成的DataFrame
def get_2020_entities_dataframe():
    entity_group = global_users.groupby('Entity')
    entity_2020_df = pd.DataFrame()
    for entity, entity_df in entity_group:
        if entity == 'World':
            continue
        entity_2020 = entity_df[entity_df['Year'] == 2020]  # 从 entity_df 中提取出 Year 列为 2020 的行
        entity_2020_df = pd.concat([entity_2020_df, entity_2020], join='outer', axis=0)
    return entity_2020_df.set_index('Entity')   # 将合并后的 DataFrame 按 Entity 列设置为索引

# 全球用户每年的各项数据的分析与可视化
def global_internet_users_analysis():
    set_seaborn_properties()
    # 全球每年的互联网用户总数分析与可视化：
    plt.subplots_adjust(hspace=1, wspace=0.7)
    year_groups = global_users.groupby('Year')
    internet_users_groups = year_groups['No. of Internet Users']
    column_mean = internet_users_groups.sum()
    internet_users_sum_data = pd.DataFrame({'Year': column_mean.index,
                                            'sum': column_mean.values})
    plt.subplot(2, 2, 1)    # 将整个图表区域划分为 2 行 2 列的网格，并激活第 1 个子图
    plt.title('全球每年互联网用户总数')
    plt.xlabel('年份')
    plt.ylabel('全球每年互联网用户总数')
    sns.lineplot(data=internet_users_sum_data, x='Year', y='sum')
    plt.bar(column_mean.index, column_mean.values, color='cornflowerblue', width=0.6)

    # 全球每年每100人移动端互联网订阅数、互联网使用人数比例、每100人宽带订阅数的平均值分析与可视化：
    year_groups = global_users.groupby('Year')
    title_mapper = {'Cellular Subscription': '全球每年每100人移动互联网订阅数',     # 当一个普通人订阅了不止一个移动的服务时，这个数字可能会超过100
                    'Internet Users(%)': '全球每年互联网使用人数比例',
                    'Broadband Subscription': '全球每年每100人宽带订阅数平均值'}
    i = 2
    for column in ['Cellular Subscription', 'Internet Users(%)', 'Broadband Subscription']:
        plt.subplot(2, 2, i)
        i += 1
        internet_users_groups = year_groups[column]
        column_mean = internet_users_groups.mean()
        column_max = internet_users_groups.max()
        max_data = pd.DataFrame({'Year': column_max.index, 'max': column_max.values})
        mean_data = pd.DataFrame({'Year': column_mean.index, 'mean': column_mean.values})
        plt.title(title_mapper[column])
        plt.xlabel('年份')
        plt.ylabel(title_mapper[column])
        sns.lineplot(data=max_data, x='Year', y='max', label=column + ' max', lw=2, linestyle=(0, (5, 1)))
        sns.lineplot(data=mean_data, x='Year', y='mean', label=column + ' mean', lw=3, linestyle=(0, (1, 1)))
        plt.legend(loc='upper left', prop={'size': 8.5})
    plt.savefig('../img/全球用户每年的各项数据的分析与可视化.png')
    plt.show()

# 2020年各个国家地区的用户占比饼图和柱状图绘制
def entities_2020_internet_users_percentage_pie_bar():
    entity_2020_df = get_2020_entities_dataframe()
    # 将"互联网用户数量"列的值转换为该列的比例，即每个国家/地区的互联网用户数占总用户数的比例
    entity_2020_df['No. of Internet Users'] /= entity_2020_df['No. of Internet Users'].sum()

    # 只筛选用户数量最多的10组数据，其他数据用`other`代替
    entity_2020_df.sort_values(by='No. of Internet Users', axis=0, ascending=False, inplace=True)
    other = entity_2020_df.iloc[10:].loc[:, 'No. of Internet Users'].sum()
    other_df = pd.DataFrame(data={'': {'Entity': 'Other', 'No. of Internet Users': other}}).T
    other_df.set_index('Entity', inplace=True)
    processed_data = pd.concat([entity_2020_df.head(10), other_df], axis=0, join='outer')

    # 绘制饼图
    set_seaborn_properties(context='notebook', font_scale=0.8)
    explode_arr = np.zeros(shape=(11))
    explode_arr[0] = 0.07   # 突出显示饼图中第一个扇区（比例最大的国家），通过设置其爆炸距离为0.07
    plt.axes(aspect=1)  # 设置图表的坐标轴比例为1，确保饼图是圆形
    plt.title('2020年各个国家地区的互联网用户占比')
    # 绘制饼图
    plt.pie(processed_data['No. of Internet Users'], labels=processed_data.index, explode=explode_arr,
            labeldistance=1.1, autopct='%2.1f%%', pctdistance=0.9, shadow=True)
    plt.legend(loc='lower right', bbox_to_anchor=(0.5, 0., 0.95, 0.5), ncols=2)
    plt.savefig('../img/2020年各个国家地区的互联网用户占比饼图.png')
    plt.show()

    # 绘制柱状图
    set_seaborn_properties(font_scale=0.36)
    plt.rcParams['figure.dpi'] = 300
    data = pd.DataFrame({'Entity': processed_data.index, 'Percent': processed_data['No. of Internet Users']})
    plt.title('2020年各个国家地区的互联网用户占比')
    sns.barplot(data=data, x='Entity', y='Percent')
    plt.savefig('../img/2020年各个国家地区的互联网用户占比柱状图.png')
    plt.show()

# 2020年各国家地区互联网用户占比分布直方图
def entities_2020_internet_users_percentage_distribution_histogram():
    set_seaborn_properties(font_scale=0.8)
    entity_2020_df = get_2020_entities_dataframe()  # 获取包含2020年各国或地区信息的数据框(DataFrame)
    internet_users_percentage_sr = entity_2020_df['Internet Users(%)']  # 提取这一列
    plt.title('2020年各国家地区互联网用户占比分布直方图')
    plt.xlabel('互联网用户占比占比')
    plt.ylabel('国家地区数量')
    # 创建一个新的 DataFrame，包含国家地区的名称（索引）和对应的互联网用户占比(值)
    data = pd.DataFrame({'Entity': internet_users_percentage_sr.index, 'Percent': internet_users_percentage_sr.values})
    sns.histplot(data, x='Percent')
    plt.savefig('../img/2020年各国家地区互联网用户占比分布直方图.png')
    plt.show()

# 2020年各国家地区互联网用户占比和移动互联网订阅量的散点图
def entities_2020_internet_users_percentage_distribution_scatter():
    set_seaborn_properties()
    entity_2020_df = get_2020_entities_dataframe()
    plt.title('2020年各国家地区互联网用户占比和移动互联网订阅量散点图')
    plt.xlabel('互联网用户占比占比')
    plt.ylabel('移动互联网订阅量')
    # 绘制散点图
    sns.scatterplot(data=entity_2020_df, x='Internet Users(%)', y='Cellular Subscription',
                    palette='husl', hue='Entity', legend=None)

    # 利用线性回归分析两者关系
    x = entity_2020_df[['Internet Users(%)']]   # x 存储互联网用户占比的数据
    # 创建线性回归模型 model_1，并使用 fit() 方法训练模型，预测 Cellular Subscription
    model_1 = linear_model.LinearRegression()
    model_1.fit(x, entity_2020_df[['Cellular Subscription']])
    data = pd.DataFrame({'x': x['Internet Users(%)'], 'pred_y': [x[0] for x in model_1.predict(x)]})
    sns.lineplot(data=data, x='x', y='pred_y')
    plt.savefig('../img/2020年各国家地区互联网用户占比和移动互联网订阅量散点图及线性回归拟合.png')
    plt.show()

# 用每一年互联网用户的比例最大的三个国家地区名生成词云
def draw_internet_users_percentage_annual_top_3_wordcloud():
    text = ''   # 创建一个空字符串 text，用于存储所有选定的国家或地区名称
    year_groups = global_users.groupby('Year')
    # 获取每一年互联网用户的比例最大的三个国家地区名数据
    for year, year_df in year_groups:
        year_df.sort_values(by='Internet Users(%)', ascending=False, inplace=True)
        top_3 = year_df.head(3)
        entities = top_3['Entity']
        for entity in entities:
            if len(entity.split()) > 1:
                text += entity.replace(' ', '_') + ' '
                # 将名字中含有空格的国家地区名中的空格替换成下划线_，避免一个名字被拆分成多个单词
            else:
                text += entity + ' '
    # 创建一个 WordCloud 对象 wc，设置相关参数，如最大单词数、图像宽高、背景颜色、最大字体大小、停用词等
    wc = WordCloud(max_words=100, width=800, height=400, background_color='White',
                   max_font_size=150, stopwords=STOPWORDS, margin=5, scale=1.5)
    wc.generate(text)
    plt.title('每年互联网用户的比例最大的国家地区名词云')
    plt.imshow(wc)
    plt.axis("off")
    wc.to_file('../img/每年互联网用户的比例最大的国家地区名词云.png')
    plt.show()

# 对中国互联网用户数据的分析与可视化
def chinese_users_analysis():
    # 绘制各项指标的数值图
    set_seaborn_properties()
    plt.title('中国互联网用户的数量（单位：千万人）、占人口的比例、移动互联网订阅每一百人比例、宽带每一百人订阅比例')
    plt.xlabel('年份')
    plt.ylabel('数值')
    
    chinese_users['No. of Internet Users'] /= 10000000
    sns.lineplot(data=chinese_users, x='Year', y='No. of Internet Users', label='数量（单位：千万人）', lw=3)
    sns.lineplot(data=chinese_users, x='Year', y='Internet Users(%)', label='占人口的比例', lw=3)
    sns.lineplot(data=chinese_users, x='Year', y='Cellular Subscription', label='移动互联网订阅每一百人比例', lw=3)
    sns.lineplot(data=chinese_users, x='Year', y='Broadband Subscription', label='宽带每一百人订阅比例', lw=3)
    plt.legend(loc='upper left')
    plt.savefig('../img/中国互联网用户的数量（单位：千万人）、占人口的比例、移动互联网订阅每一百人比例、宽带每一百人订阅比例.png')
    plt.show()

    # 计算增长率
    growth_columns = ['No. of Internet Users', 'Internet Users(%)', 'Cellular Subscription', 'Broadband Subscription']
    for col in growth_columns:
        chinese_users[f'increase of {col}'] = chinese_users[col].pct_change().fillna(0)

    plt.title('中国互联网用户的数量及各项指标的增长率')
    plt.xlabel('年份')
    plt.ylabel('数值')
    for col in growth_columns:
        sns.lineplot(data=chinese_users, x='Year', y=f'increase of {col}', lw=4, label=f'{col}增长率')
    plt.legend(loc='upper left')
    plt.savefig('../img/中国互联网用户的数量及各项指标的增长率.png')
    plt.show()

    # 多元线性回归预测
    set_seaborn_properties()
    plt.title('对1980到2020年中国互联网总用户数的拟合')
    sns.scatterplot(data=chinese_users, x='Year', y='No. of Internet Users')
    
    poly_reg = PolynomialFeatures(degree=3)
    x = chinese_users[['Year']]
    x_m = poly_reg.fit_transform(x)

    model_2 = linear_model.LinearRegression()
    model_2.fit(x_m, chinese_users[['No. of Internet Users']])
    data = pd.DataFrame({'x': x['Year'], 'pred_y': model_2.predict(x_m).flatten()})
    plt.xlabel('年份')
    plt.ylabel('人数（单位：千万人）')
    sns.lineplot(data=data, x='x', y='pred_y')
    plt.savefig('../img/对1980到2020年中国互联网总用户数的拟合.png')
    plt.show()

    # 预测
    set_seaborn_properties()
    plt.title('到2030年中国互联网总用户数的预测')
    plt.xlabel('年份')
    plt.ylabel('人数（单位：千万人）')
    
    pred_x = pd.DataFrame(np.arange(1980, 2031), columns=['Year'])
    pred_x_m = poly_reg.transform(pred_x)
    plt.plot(pred_x, model_2.predict(pred_x_m), label='预测总用户数')
    plt.legend()
    plt.savefig('../img/到2030年中国互联网总用户数的预测.png')
    plt.show()

if __name__ == '__main__':
    # 读取文件，获取全球互联网用户信息
    global_users = pd.read_csv('../data/Final.csv', delimiter=',', usecols=range(1, 8))  # 由于第一列的列名未知，所以不使用第一列
    # 对全球用户进行分析：
    # global_internet_users_analysis()
    # entities_2020_internet_users_percentage_pie_bar()
    # entities_2020_internet_users_percentage_distribution_histogram()
    # entities_2020_internet_users_percentage_distribution_scatter()
    # draw_internet_users_percentage_annual_top_3_wordcloud()

    # 通过切片获取中国互联网用户信息
    chinese_users = global_users.loc[global_users['Entity'] == 'China']
    # chinese_users_analysis()