import unittest
import pandas as pd
from typing import List, Tuple
import math

label_to_cluster_num = {'ES-B':0,'ES-D':1}

def extract_numerical_features(df:pd.DataFrame) -> pd.DataFrame:
    # should be updated if features are added !
    numerical_features = ['overall_slope', 'max_depth', 'max_resistance', 'num_peaks', 'largest_force_drop', 'curve_shape', 'largest_force_drop_res_level']
    df_copy = df.copy()
    for col in df.columns:
        if col not in numerical_features:
            df_copy.drop(col, axis=1, inplace=True)
    return df_copy

def find_labels_centroids(labeled_data: pd.DataFrame, ylabel_to_cluster_num:dict[str,int], ylabel_name:str) -> pd.DataFrame:
    labeled_data = labeled_data.copy()
    numerical_data = extract_numerical_features(labeled_data)
    label_centroids = []
    for label, label_num in ylabel_to_cluster_num.items():
        if label not in labeled_data[ylabel_name].values: continue
        label_data = numerical_data[labeled_data[ylabel_name] == label]
        label_centroid = label_data.mean(axis=0).tolist() # drop cols for mean calculation
        label_centroid.extend([label, label_num]) # append these onto the end
        label_centroids.append(label_centroid)
    return_cols = numerical_data.columns.tolist()
    return_cols.extend([ylabel_name, f'{ylabel_name}_nums'])
    return pd.DataFrame(data=label_centroids, columns=return_cols)

class Test_Find_Marions_Labels_Feature_Means(unittest.TestCase):

    def test1(self):
        marions_labeled_features_df = pd.DataFrame({
            'overall_slope':[1,1,1,1],
            'max_depth':[2,2,2,2],
            'num_peaks':[3,3,3,3],
            'curve_shape':[4,4,4,4],
            'marions_ylabels': ['ES-B', 'ES-D', 'ES-B', 'ES-D']
        })
        marions_centroids = find_labels_centroids(marions_labeled_features_df, label_to_cluster_num, ylabel_name='marions_ylabels')
        ground_truth = pd.DataFrame({
            'overall_slope':[1.0,1.0,],
            'max_depth':[2.0,2.0,],
            'num_peaks':[3.0,3.0,],
            'curve_shape':[4.0,4.0,],
            'marions_ylabels': ['ES-B', 'ES-D'],
            'marions_ylabels_nums': [0,1]
        })
        print(ground_truth.equals(marions_centroids))

def euclidean_distance(x: pd.Series, y: pd.Series) -> float:
    return math.sqrt(((y - x) ** 2).sum())

def find_closest_centroid(unlabeled_data:pd.DataFrame, marions_centroids:pd.DataFrame, ylabel_name) -> pd.DataFrame:
    unlabeled_num_data = extract_numerical_features(unlabeled_data) # returns a new object
    unlabeled_non_num_data = unlabeled_data.drop(unlabeled_num_data.columns, axis=1)
    
    pseudo_label_list = []
    pseudo_label_num_list = []
    unlabeled_num_data = unlabeled_num_data.copy()
    for i, depth_res_curve in unlabeled_num_data.iterrows():
        min_distance = float('inf')
        min_distance_label = ''
        min_distance_label_num = 0
        for j, marions_label_centroid in marions_centroids.iterrows():
            curve_to_label_mean_distance = euclidean_distance(depth_res_curve, marions_label_centroid)
            if curve_to_label_mean_distance < min_distance:
                min_distance = curve_to_label_mean_distance
                min_distance_label = marions_label_centroid[ylabel_name]
                min_distance_label_num = marions_label_centroid[f'{ylabel_name}_nums']
        pseudo_label_list.append(min_distance_label)
        pseudo_label_num_list.append(min_distance_label_num)
    unlabeled_num_data[f'pseudo_{ylabel_name}'] = pseudo_label_list
    unlabeled_num_data[f'pseudo_{ylabel_name}_nums'] = pseudo_label_num_list

    return pd.concat([unlabeled_num_data, unlabeled_non_num_data], axis=1)


class Test_Find_Closest_Centroids(unittest.TestCase):

    def test1(self): 
        unlabeled_data_df = pd.DataFrame({
            'max_depth':[1,2,1,2],
            'max_resistance':[1,2,1,2],
            'num_peaks':[1,2,1,2],
            'curve_shape':[1,2,1,2],
            'filenames':['f0','f1','f2','f3']
        })
        marions_centroids = pd.DataFrame({
            'max_depth':[1.0,2.0,],
            'max_resistance':[1.0,2.0,],
            'num_peaks':[1.0,2.0,],
            'curve_shape':[1.0,2.0,],
            'marions_ylabels': ['ES-B', 'ES-D'],
            'marions_ylabels_nums': [0,1]
        })
        psuedo_labeled_data_df = find_closest_centroid(unlabeled_data_df, marions_centroids, 'marions_ylabels')
        ground_truth = pd.DataFrame({
            'max_depth':[1,2,1,2],
            'max_resistance':[1,2,1,2],
            'num_peaks':[1,2,1,2],
            'curve_shape':[1,2,1,2],
            'pseudo_marions_ylabels': ['ES-B','ES-D','ES-B','ES-D'],
            'pseudo_marions_ylabels_nums': [0,1,0,1],
            'filenames':['f0','f1','f2','f3'],
        })
        print(f'Test_Find_Closest_Centroids test1: {ground_truth.equals(psuedo_labeled_data_df)}')

    def test2(self): 
        unlabeled_data_df = pd.DataFrame({
            'max_depth':[1,2,3,7,8,9],
            'max_resistance':[1,2,3,7,8,9],
            'num_peaks':[1,2,3,7,8,9],
            'curve_shape':[1,2,3,7,8,9],
        })
        marions_centroids = pd.DataFrame({
            'max_depth':[2.0,8.0],
            'max_resistance':[2.0,8.0],
            'num_peaks':[2.0,8.0],
            'curve_shape':[2.0,8.0],
            'marions_ylabels': ['ES-B', 'ES-D'],
            'marions_ylabels_nums': [0,1]
        })
        psuedo_labeled_data_df = find_closest_centroid(unlabeled_data_df, marions_centroids, 'marions_ylabels')
        # print(psuedo_labeled_data_df)
        ground_truth = pd.DataFrame({
            'max_depth':[1,2,3,7,8,9],
            'max_resistance':[1,2,3,7,8,9],
            'num_peaks':[1,2,3,7,8,9],
            'curve_shape':[1,2,3,7,8,9],
            'pseudo_marions_ylabels': ['ES-B','ES-B','ES-B','ES-D','ES-D','ES-D'],
            'pseudo_marions_ylabels_nums': [0,0,0,1,1,1]
        })
        print(ground_truth.equals(psuedo_labeled_data_df))

def find_changed_label_curves(labeled_data:pd.DataFrame, pseudo_labeled_data:pd.DataFrame, ylabel_name:str):
    ylabel_indicies = labeled_data.index # indicies of labeled data points
    pseudo_labels_of_labeled_data = pseudo_labeled_data.loc[ylabel_indicies]
    diff_mask = (labeled_data[ylabel_name] != pseudo_labels_of_labeled_data[f'pseudo_{ylabel_name}'])
    changed_label_indicies = labeled_data[diff_mask].index.tolist()
    return changed_label_indicies

class Test_Find_Changed_Label_Curves(unittest.TestCase):

    # test when they're the same
    def test1(self): 
        labeled_data = pd.DataFrame({
            'ylabels': ['1', '2', '3']
        })
        pseudo_labeled_data = pd.DataFrame({
            'pseudo_ylabels': ['1', '2', '3']
        })
        self.assertEqual(find_changed_label_curves(labeled_data, pseudo_labeled_data, 'ylabels'), [])
    # test when pseudo_labeled_data has more values
    def test2(self): 
        labeled_data = pd.DataFrame({
            'ylabels': ['1', '2', '3']
        })
        pseudo_labeled_data = pd.DataFrame({
            'pseudo_ylabels': ['1', '2', '3', '4']
        })
        self.assertEqual(find_changed_label_curves(labeled_data, pseudo_labeled_data, 'ylabels'), [])
    # test when there are switches
    def test3(self):
        labeled_data = pd.DataFrame({
            'ylabels': ['1', '2', '3']
        })
        pseudo_labeled_data = pd.DataFrame({
            'pseudo_ylabels': ['0', '2', '1', '4']
        })
        self.assertEqual(find_changed_label_curves(labeled_data, pseudo_labeled_data, 'ylabels'), [0,2])

if __name__ == '__main__':
    unittest.main()