import unittest
import pandas as pd
from typing import List, Tuple
import math

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

if __name__ == '__main__':
    unittest.main()