import unittest
import pandas as pd
from typing import List, Tuple
import math

def find_marions_labels_means(marions_features_df: pd.DataFrame) -> pd.DataFrame:
    marions_features_df['encoded'], uniques = pd.factorize(marions_features_df['marions_ylabels'])
    label_centroids_list = []
    for label_num, label_name in enumerate(uniques):
        label_features = marions_features_df[marions_features_df['encoded'] == label_num]
        label_centroid = label_features.drop(['encoded', 'marions_ylabels'], axis=1).mean(axis=0).tolist() # drop cols for mean calculation
        label_centroid.extend([label_name, label_num])
        label_centroids_list.append(label_centroid)
    return pd.DataFrame(data=label_centroids_list, columns=marions_features_df.columns)

class Test_Find_Marions_Labels_Feature_Means(unittest.TestCase):

    def test1(self):
        marions_labeled_features_df = pd.DataFrame({
            'a':[1,1,1,1],
            'b':[2,2,2,2],
            'c':[3,3,3,3],
            'd':[4,4,4,4],
            'marions_ylabels': ['ES-B', 'ES-D', 'ES-B', 'ES-D']
        })
        marions_centroids = find_marions_labels_means(marions_labeled_features_df)
        ground_truth = pd.DataFrame({
            'a':[1.0,1.0,],
            'b':[2.0,2.0,],
            'c':[3.0,3.0,],
            'd':[4.0,4.0,],
            'marions_ylabels': ['ES-B', 'ES-D'],
            'encoded': [0,1]
        })
        print(ground_truth.equals(marions_centroids))

def euclidean_distance(x: pd.DataFrame, y: pd.DataFrame) -> float:
    inner_sum = 0
    for idx in range(len(x)):
        inner_sum += (y.iloc[idx] - x.iloc[idx])**2
    return math.sqrt(inner_sum)

def find_closest_centroid(unlabeled_data_df:pd.DataFrame, marions_centroids:pd.DataFrame) -> pd.DataFrame:
    psuedo_label_list = []
    unlabeled_data_df = unlabeled_data_df.copy()
    for i, depth_res_curve in unlabeled_data_df.iterrows():
        min_distance = float('inf')
        min_distance_label = ''
        for j, marions_label_mean in marions_centroids.iterrows():
            curve_to_label_mean_distance = euclidean_distance(depth_res_curve, marions_label_mean)
            if curve_to_label_mean_distance < min_distance:
                min_distance = curve_to_label_mean_distance
                min_distance_label = marions_label_mean['marions_ylabels']
        psuedo_label_list.append(min_distance_label)
    unlabeled_data_df['marions_pseudo_labels'] = psuedo_label_list
    return unlabeled_data_df

class Test_Find_Closest_Centroids(unittest.TestCase):

    def test1(self): 
        unlabeled_data_df = pd.DataFrame({
            'a':[1,2,1,2],
            'b':[1,2,1,2],
            'c':[1,2,1,2],
            'd':[1,2,1,2],
        })
        marions_centroids = pd.DataFrame({
            'a':[1.0,2.0,],
            'b':[1.0,2.0,],
            'c':[1.0,2.0,],
            'd':[1.0,2.0,],
            'marions_ylabels': ['ES-B', 'ES-D'],
            'encoded': [0,1]
        })
        psuedo_labeled_data_df = find_closest_centroid(unlabeled_data_df, marions_centroids)
        ground_truth = pd.DataFrame({
            'a':[1,2,1,2],
            'b':[1,2,1,2],
            'c':[1,2,1,2],
            'd':[1,2,1,2],
            'marions_pseudo_labels': ['ES-B','ES-D','ES-B','ES-D']
        })
        print(ground_truth.equals(psuedo_labeled_data_df))

    def test2(self): 
        unlabeled_data_df = pd.DataFrame({
            'a':[1,2,3,7,8,9],
            'b':[1,2,3,7,8,9],
            'c':[1,2,3,7,8,9],
            'd':[1,2,3,7,8,9],
        })
        marions_centroids = pd.DataFrame({
            'a':[2.0,8.0],
            'b':[2.0,8.0],
            'c':[2.0,8.0],
            'd':[2.0,8.0],
            'marions_ylabels': ['ES-B', 'ES-D'],
            'encoded': [0,1]
        })
        psuedo_labeled_data_df = find_closest_centroid(unlabeled_data_df, marions_centroids)
        ground_truth = pd.DataFrame({
            'a':[1,2,3,7,8,9],
            'b':[1,2,3,7,8,9],
            'c':[1,2,3,7,8,9],
            'd':[1,2,3,7,8,9],
            'marions_pseudo_labels': ['ES-B','ES-B','ES-B','ES-D','ES-D','ES-D']
        })
        print(ground_truth.equals(psuedo_labeled_data_df))

if __name__ == '__main__':
    unittest.main()