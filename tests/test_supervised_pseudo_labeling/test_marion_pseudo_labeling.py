import unittest
import pandas as pd
import numpy as np

label_to_cluster_num = {'ES-B':0,'ES-D':1}

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


from sklearn.neighbors import NearestCentroid
import sys
import os
sys.path.append(os.getcwd())
import plotting

ylabel_name = 'marions_ylabels_esd_removed'

def nearest_centroid_iterations(marions_labeled_data:pd.DataFrame, clustering_features:pd.DataFrame, prob_threshold:float) -> pd.Series:
    labeled_data = marions_labeled_data.copy()
    unlabeled_data = clustering_features.copy()
    high_prediction_idxs = [-1]

    while len(high_prediction_idxs):
        nc = NearestCentroid()
        X = plotting.extract_numerical_features(labeled_data).values.tolist()
        y = labeled_data[f'{ylabel_name}_nums'].values.tolist()
        nc.fit(X,y)
        unlabeled_data = clustering_features.drop(labeled_data.index, axis=0).values
        np_predictions = nc.predict(unlabeled_data)
        np_prediction_probs = np.round(nc.predict_proba(unlabeled_data), 2)

        high_prediction_idxs = np.where(np.any(np_prediction_probs > prob_threshold, axis=1))[0]
        high_prediction_unlabeled_data = unlabeled_data.loc[high_prediction_idxs, :]
        high_prediction_unlabeled_data[f'{ylabel_name}_nums'] = np_predictions
        
        if len(high_prediction_idxs):
            pd.concat([labeled_data, high_prediction_unlabeled_data], axis=0)
    
    pseudo_labeled_data = pd.concat([labeled_data, high_prediction_unlabeled_data], axis=0)
    return pseudo_labeled_data[f'{ylabel_name}_nums']

class Test_Find_Changed_Label_Curves(unittest.TestCase):

    def test1(self): 
        labeled_data = pd.DataFrame({
            'f1': [0,1],
            'marions_ylabels_esd_removed_nums': [0,1]
        })
        all_data = pd.DataFrame({
            'f1': [0,1,0,1],
            'marions_ylabels_esd_removed_nums': [0,1,np.nan,np.nan]
        })
        predicted = nearest_centroid_iterations(labeled_data, all_data, 0.9)
        self.assertEqual([0,1,0,1], predicted)
        








if __name__ == '__main__':
    unittest.main()