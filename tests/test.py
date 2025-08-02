# from matplotlib import pyplot as plt
# from sklearn.decomposition import PCA
# import pandas as pd
# import numpy as np

# x = [1, 2, 3, 4, 5]
# y = [5, 4, 3, 2, 1]
# # y = [1,2,3,4,5]


# plt.figure()
# # plt.scatter(x, y, color='blue', label='Data points')
# # plt.xlabel('x')
# # plt.ylabel('y')
# # plt.title('Scatter Plot of x vs y')
# # plt.grid(True)
# # plt.legend()
# # plt.show()
# # plt.close()

# df = pd.DataFrame({'x':x, 'y':y})

# pca = PCA(n_components=2)
# pca.fit(df.values)
# x_pca = pca.transform(df.values)
# plt.scatter(x=np.rint(x_pca[:,0]), y=np.rint(x_pca[:,1]))
# plt.xlabel('pc1')
# plt.ylabel('pc2')
# print(pca.components_)
# print(pca.explained_variance_)
# print(f'xpca[:,0] : {np.rint(x_pca[:,0])}')
# print(f'xpca[:,1] : {np.rint(x_pca[:,1])}')
# plt.arrow(x=0,y=0,dx=np.rint(x_pca[0,0]), dy=np.rint(x_pca[1,0]))
# plt.arrow(x=0,y=0,dx=np.rint(x_pca[0,1]), dy=np.rint(x_pca[1,1]))


# plt.show()


import copy


d = {
    'overall_slope': ['max_depth', 'max_resistance'],
    'max_depth': ['overall_slope', 'max_resistance', 'num_peaks'],
    'max_resistance': ['overall_slope', 'max_depth', 'num_peaks'],
    'num_peaks': ['max_depth', 'max_resistance'],
    'largest_force_drop': [],
    'curve_shape': [],
}
non_corr_list = []
for root_key, value in d.items():
    go_list = [root_key]
    no_go_list = copy.deepcopy(value) + [root_key]
    for key in d.keys():
        if key not in no_go_list:
            go_list.append(key) 
            no_go_list = no_go_list + [key] + d[key]
    non_corr_list.append(go_list)
non_corr_list = non_corr_list.sort() # TODO wrong need each sublist to be sorted
uniques = []
for i in range(len(non_corr_list)):
    dupl = 0
    for j in range(len(non_corr_list)):
        if j == i: continue
        if non_corr_list[i] == non_corr_list[j]: 
            dupl = 1
    if not dupl:
        uniques.append(non_corr_list.)
    dupl = 1




# overall_slope, nums_peaks, largest_force_drop, curve_shape
# max_depth, largest_force_drop, curve_shape
# max_resistance, largest_force_drop, curve_shape

