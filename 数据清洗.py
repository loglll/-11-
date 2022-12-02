import pandas as pd
import re


df = pd.read_csv('data.csv',header=None)
df.columns = ['日期','官方信息']
# 日期格式转换
df['日期'] = df['日期'].apply(lambda x: x.replace('年','-').replace('月','-').replace('日',''))
df['日期'] = pd.to_datetime(df['日期'])
# 确诊或无症状分类
df['分类'] = df['官方信息'].apply(lambda x: '确诊' if '确诊' in x else '无症状')
# 取上下编码值并统计数量
df['编码'] = df['官方信息'].apply(lambda x: re.findall('\d+',x))
df['编码_low'] = df['编码'].apply(lambda x: x[0]).astype('int')
df['编码_high'] = df['编码'].apply(lambda x: x[1] if len(x)>1 else x[0]).astype('int')
df['新增确诊+无症状'] = df.apply(lambda x: x['编码_high']-x['编码_low']+1,axis=1)
df.drop(columns='编码',inplace=True)
# 分解地址，取区、街道名称
df.loc[df.官方信息 == '本土无症状感染者300：在外省来穗人员排查中发现。','官方信息'] = '本土无症状感染者300：在集中隔离场所排查中发现。'
df['区'] = df['官方信息'].apply(lambda x: '集中隔离' if '集中隔离' in x else x.split('居住在')[1][:3])
df['街道'] = df['官方信息'].apply(lambda x: '集中隔离' if '集中隔离' in x else x.split('区')[1].split('。')[0])
# df.sort_values(by='日期',ascending=True,inplace=True)

# 只取可视化想要的列
df_show = df[['日期','区','分类','新增确诊+无症状']]
# 分组聚合：分组聚合后是MultiIndex对象（聚合列为索引，计算列为值），使用reset_index()方法，将MultiIndex对象的索引重置，则聚合后的索引列可以变成值
gb_sum = df_show.groupby(['日期','区','分类']).sum()
df_gbs = gb_sum.reset_index()
# 将确诊、无症状感染分开
df_gbs['新增确诊'] = df_gbs.apply(lambda x: x['新增确诊+无症状'] if x['分类'] == '确诊' else 0,axis=1)
df_gbs['新增无症状感染'] = df_gbs.apply(lambda x: x['新增确诊+无症状'] if x['分类'] == '无症状' else 0,axis=1)
df_gbs.drop(columns='分类',inplace=True)
gb_sums = df_gbs.groupby(['日期','区']).sum()
df_gb_sums = gb_sums.reset_index()
# print(df_gb_sums)

# 为Tableau可视化地图方便，每天无新增的区也填充进去
district_full_list = ['从化区', '南沙区', '增城区', '天河区', '海珠区', '番禺区', '白云区', '花都区', '荔湾区', '越秀区', '黄埔区', '集中隔离']
fill_list = []
for i in range(1,29):
    district_list = df_gb_sums.query('日期=="2022-11-{}"'.format(i))['区'].tolist()
    difference_list = list(set(district_full_list).difference(set(district_list)))
    if len(difference_list) > 0:
        for j in difference_list:
            fill_list.append(['2022-11-{}'.format(i),j,0,0,0])
df_fill = pd.DataFrame(fill_list)
df_fill.columns = df_gb_sums.columns
df_fill['日期'] = pd.to_datetime(df_fill['日期'])
df_concat = pd.concat([df_gb_sums,df_fill],axis=0,ignore_index=True)
df_final = df_concat.sort_values(by='日期',ascending=True)

# 使用cumsum()方法求累计值
df_final['累计确诊+无症状'] = df_final.groupby('区')['新增确诊+无症状'].cumsum()
df_final['累计确诊'] = df_final.groupby('区')['新增确诊'].cumsum()
df_final['累计无症状感染'] = df_final.groupby('区')['新增无症状感染'].cumsum()

# 保存到本地
df_final.to_excel('data_set.xlsx',index=False)

