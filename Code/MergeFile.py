import pandas as pd
import glob

# 获取所有 CSV 文件的文件名
file_pattern = '../Data/single/results-*.csv'  # 将 'path_to_directory' 替换为包含 CSV 文件的目录路径
file_list = glob.glob(file_pattern)

# 创建一个空的 DataFrame 用于存储合并后的数据
merged_data = pd.DataFrame()

# 依次读取并合并所有 CSV 文件
for file in file_list:
    df = pd.read_csv(file)
    merged_data = pd.concat([merged_data, df], ignore_index=True)

# 去除重复行
deduplicated_data = merged_data.drop_duplicates(subset='Issue ID')

# 按照 ID 列进行排序
sorted_data = deduplicated_data.sort_values(by='Issue ID', ascending=False)

# 保存到新的 CSV 文件
sorted_data.to_csv('../Data/multi/results-2020-2023.csv', index=False)
