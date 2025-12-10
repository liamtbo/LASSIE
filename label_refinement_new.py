import pandas as pd
import os
import plotting
import importlib
importlib.reload(plotting)
pd.options.display.max_rows = 4000
import numpy as np

def load_data(data_src):
    curve_data = [] # used for plotting
    filename_list = []
    for filename in os.listdir(data_src):
        df = pd.read_csv(f"{data_src}/{filename}")
        curve_data.append(df)
        filename_list.append(filename)
    return curve_data, filename_list

data_src = "data/cleaned_data"
curve_data, filename_list = load_data(data_src)
filename_to_depth_resist = dict(zip(filename_list, curve_data))

# ylabel_name = 'marions_ylabels_esd_removed'
ylabel_name = 'marions_ylabels'
data = pd.read_csv("data/optimal_features.csv")


data['popcorn'] = data['popcorn'].astype('boolean')
data['clump'] = data['clump'].astype('boolean')
data['loose_sand'] = data['loose_sand'].astype('boolean')

clustering_features = plotting.extract_numerical_features(data)

# ylabel_name = 'marions_ylabels_deduction'
ylabel_to_cluster_num = {'Outlier':-1, 'ES-B':0, 'ES-BW':1, 'ES-S':2, 'ES-S-Plates':3, 'ES-D':4, 'LS':5, 'F':6, 'LS/F':7, 'ES-DB':8, 'ES': 9}
cluster_num_to_ylabel = {v: k for k, v in ylabel_to_cluster_num.items()}
data[f'{ylabel_name}_nums'] = data[ylabel_name].map(ylabel_to_cluster_num)
marions_labeled_data = data[data[ylabel_name].notna()].copy() # removes NaN's which correspond to non-labled data

def loss(pseudo_labels:pd.Series, actual_labels:pd.Series):
    pseudo_actual_intersection = pseudo_labels.loc[actual_labels.index]
    diff_mask = pseudo_actual_intersection != actual_labels
    diff_labels = pseudo_actual_intersection[diff_mask]
    return diff_labels.index
    
def correct_pseudo_ylabels_to_actual(pseudo_labels:pd.Series, actual_labels:pd.Series, changed_ylabel_idxs) -> pd.Series:
    corrected_pseudo_labels = pseudo_labels.copy()
    corrected_pseudo_labels.loc[changed_ylabel_idxs] = actual_labels
    return corrected_pseudo_labels

optimal_visual_features = ['popcorn', 'clump', 'loose_sand']
groups = data.groupby(optimal_visual_features, dropna=False)
for i, (name, df) in enumerate(groups):
    data.loc[df.index, 'group_ylabel'] = i 

plotting.plot_cluster_subplots(
    data['group_ylabel'],
    curve_data,
    title='(' + ", ".join(optimal_visual_features) + ')',
    filenames=filename_list,
    cluster_category_names=[str(k) for k in groups.groups.keys()]
)

