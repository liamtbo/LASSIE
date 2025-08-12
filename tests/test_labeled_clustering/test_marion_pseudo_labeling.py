import unittest
import pandas as pd
from typing import List, Tuple
import math

def find_marions_labels_feature_means(marions_features_df: pd.DataFrame, uniques: List[str]) -> pd.DataFrame:
    meta_data_cols = ['filenames', 'feifeis_ylabels', 'liams_ylabels', 'distances']
    marions_features_df = marions_features_df.drop(meta_data_cols, axis=1)
    marions_labels_mean_df = pd.DataFrame(columns=marions_features_df.columns)
    for label_num, label_name in enumerate(uniques):
        label_features = marions_features_df[marions_features_df['encoded'] == label_num]
        mean_series = label_features.drop(['encoded', 'marions_ylabels'], axis=1).mean(axis=0) # drop cols for mean calculation
        label_features_mean_df = pd.DataFrame([mean_series], columns=marions_features_df.columns)
        label_features_mean_df['marions_ylabels'] = label_name
        label_features_mean_df['encoded'] = label_num
        marions_labels_mean_df = pd.concat([marions_labels_mean_df, label_features_mean_df], axis=0)
    return marions_labels_mean_df.reset_index().drop('index', axis=1)

class Test_Find_Marions_Labels_Feature_Means(unittest.TestCase):

    def test1(self):
        # marions_features_df
        pass



# def euclidean_distance(x: pd.DataFrame, y: pd.DataFrame) -> float:
#     inner_sum = 0
#     for idx in range(len(x)):
#         inner_sum += (y.iloc[idx] - x.iloc[idx])**2
#     return math.sqrt(inner_sum)

# psuedo_label_list = []
# psuedo_labeled_features_df = clustering_features_df.copy()
# for i, depth_res_curve in psuedo_labeled_features_df.iterrows():
#     min_distance = float('inf')
#     min_distance_label = ''
#     for j, marions_label_mean in marions_features_df.iterrows():
#         curve_to_label_mean_distance = euclidean_distance(depth_res_curve, marions_label_mean)
#         if curve_to_label_mean_distance < min_distance:
#             min_distance = curve_to_label_mean_distance
#             min_distance_label = marions_label_mean['marions_ylabels']
#     psuedo_label_list.append(min_distance_label)
# psuedo_labeled_features_df['marions_pseudo_labels'] = psuedo_label_list
