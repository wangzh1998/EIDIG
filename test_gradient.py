"""
This python file is used to run test experiments.
"""


import experiments
import numpy as np
import os
import experiment_config

info = experiment_config.all_benchmark_info
all_benchmarks = [benchmark for benchmark in info.keys()]

g_num = 1000 # the number of seeds used in the global generation phase
perturbation_size = 1 # the perturbation size used in the compute_gradient function
# results of experiments to save
results = []

for benchmark in all_benchmarks:
    print('\n', benchmark, ':\n')
    model, dataset, protected_attribs = info[benchmark]
    data = dataset.X_train
    adf_gradients, eidig_gradients, maft_gradients, maft_gradients_non_vec, \
        adf_time_cost, eidig_time_cost, maft_time_cost, maft_time_cost_non_vec = \
        experiments.gradient_comparison(benchmark, data, model, g_num, perturbation_size)
    result = [benchmark, adf_gradients, eidig_gradients, maft_gradients, maft_gradients_non_vec,
              adf_time_cost, eidig_time_cost, maft_time_cost, maft_time_cost_non_vec]
    results.append(result)

# Convert list to ndarray
results = np.array(results, dtype=object)

'''
Contrcut path and create dir
'''
dir = 'logging_data/gradients_comparison/'
iter = 'Seeds_{}_H_{}_'.format(g_num, perturbation_size)
if not os.path.exists(dir):
    os.makedirs(dir)

'''
保存数据
'''
np.save(dir + iter + 'experiment_results.npy', results)

'''
读取数据 暂时不写
'''
# data = np.load(dir + iter + 'experiment_results.npy', allow_pickle=True)
# results = data

'''
画图
'''
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# 提取benchmark名称、EIDIG梯度、MAFT梯度
benchmark_names = results[:, 0]
adf_grads = results[:, 1] # 下面的画图只算eidig和maft的相似度，不算adf的
eidig_grads = results[:, 2]
maft_grads = results[:, 3]
maft_grads_non_vec = results[:, 4]

# 初始化列表来保存每个benchmark的所有实例的相似度
all_sims = []

# 初始化列表来保存每个benchmark的平均相似度
avg_sims = []

# 遍历所有的benchmarks
for i in range(len(benchmark_names)):
    # 提取出当前benchmark的EIDIG梯度和MAFT梯度
    eidig_grad = eidig_grads[i]
    maft_grad = maft_grads[i]

    # 初始化列表来保存当前benchmark的所有实例的相似度
    sims = []

    # 如果实际设置的g_num大于当前benchmark的实例数，则将g_num设置为当前benchmark的实例数（有一个数据集只有600条数据）
    if g_num >= len(eidig_grad):
        g_num = len(eidig_grad)

    # 遍历所有的实例
    for j in range(g_num):
        # 计算当前实例的EIDIG梯度和MAFT梯度之间的cosine相似度
        sim = cosine_similarity(eidig_grad[j].reshape(1, -1), maft_grad[j].reshape(1, -1))

        # 将相似度添加到列表中
        sims.append(sim[0][0])

    # 将当前benchmark的所有实例的相似度添加到总列表中
    all_sims.append(sims)

    # 计算当前benchmark的平均相似度，并将其添加到平均相似度列表中
    avg_sims.append(np.mean(sims))

# 用条形图显示每个benchmark的平均cosine相似度
plt.figure(figsize=(10, 5))
plt.bar(benchmark_names, avg_sims)
plt.xlabel('Benchmark')
plt.ylabel('Average Cosine Similarity')
plt.title('Average Cosine Similarity for Each Benchmark')
plt.savefig('logging_data/gradients_comparison/' + iter + 'average_cosine_similarity.png')
plt.show()


# 要单独可视化每个benchmark的每个实例的相似度，可以为每个benchmark创建一个箱线图或小提琴图。这可以显示出每个benchmark中实例的相似度的分布。下面是一个使用箱线图的例子

import seaborn as sns

plt.figure(figsize=(15, 10))

# 使用seaborn的箱线图函数，将每个benchmark的所有实例的相似度进行可视化
sns.boxplot(data=all_sims)

# 设置x轴的标签为benchmark的名字
plt.xticks(range(len(benchmark_names)), benchmark_names)

plt.ylabel('Cosine Similarity')
plt.title('Cosine Similarity for Each Instance in Each Benchmark')
plt.savefig('logging_data/gradients_comparison/' + iter + 'cosine_similarity_box.png')
plt.show()


# 此图与之前的箱线图类似，但还包括了每个benchmark实例的相似度的密度分布，从而更直观地显示出数据的分布。
import seaborn as sns
import pandas as pd

# 将数据转换为DataFrame格式，以便在seaborn中使用
sim_data = pd.DataFrame(all_sims, index=benchmark_names).T

plt.figure(figsize=(15, 10))

# 使用seaborn的小提琴图函数，将每个benchmark的所有实例的相似度进行可视化
sns.violinplot(data=sim_data)

plt.ylabel('Cosine Similarity')
plt.title('Cosine Similarity for Each Instance in Each Benchmark')
plt.savefig('logging_data/gradients_comparison/' + iter + 'cosine_similarity_violin.png')
plt.show()



# 画时间对比直方图
# 提取EIDIG和MAFT的时间开销
adf_time_cost = results[:, 5]
eidig_time = results[:, 6]
maft_time = results[:, 7]
maft_time_cost_non_vec = results[:, 8]

x = np.arange(len(benchmark_names))  # 设定x轴坐标

plt.figure(figsize=(15, 10))

# 使用条形图可视化ADF、EIDIG和MAFT的时间开销
plt.bar(x - 0.3, adf_time_cost, 0.2, label='ADF')
plt.bar(x - 0.1, eidig_time, 0.2, label='EIDIG')
plt.bar(x + 0.1, maft_time, 0.2, label='MAFT')
plt.bar(x + 0.3, maft_time_cost_non_vec, 0.2, label='MAFT_non_vec')

# 设置x轴的标签为benchmark的名字
plt.xticks(x, benchmark_names)

plt.ylabel('Time (s)')
plt.title('Time Cost for Each Benchmark')
plt.legend()
plt.savefig('logging_data/gradients_comparison/' + iter + 'time_cost.png')
plt.show()
