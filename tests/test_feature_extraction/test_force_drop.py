import unittest
import pandas as pd
from typing import List, Tuple

def find_force_drop_subranges(df: pd.DataFrame, ratio: float):
    down_moves_subrange_list = []
    resistance_max = df['resistance'].max()
    curr_peak = 0
    curr_peak_idx = 0
    curr_trough_idx = 0
    in_subrange = 0
    for idx in range(1, len(df['resistance'])):

        if df['resistance'].iloc[idx] >= curr_peak and curr_trough_idx != curr_peak_idx:
            down_moves_subrange_list.append((curr_peak_idx, curr_trough_idx))
            # in_subrange = 0

        # if df['resistance'].iloc[idx] >= curr_peak and not in_subrange:
        if df['resistance'].iloc[idx] >= curr_peak:
            curr_peak = df['resistance'].iloc[idx]
            curr_peak_idx = idx
            curr_trough_idx = idx
        elif curr_peak - df['resistance'].iloc[idx] >= resistance_max * ratio and df['resistance'].iloc[idx] < df['resistance'].iloc[curr_trough_idx]: 
            # in_subrange = 1
            curr_trough_idx = idx
            
    return down_moves_subrange_list

class test_find_force_drop_subranges(unittest.TestCase):

    def test_1(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,10]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [(2,3)])
    def test_2(self):
        df = pd.DataFrame({'resistance': [0,1,2,3,10]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [])
    def test_3(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,3,1,10]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [(2,3), (4,5)])
    def test_4(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,2,1,10]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [(2,3), (4,5)])
    def test_5(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,0,10]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [(2,4)])
    def test_6(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,0,5,4,10]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [(2,4),(5,6)])
    def test_7(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,2,3,4,5,6,5,6,7,8,9,10]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [(2,3),(8,9)])
    def test_8(self):
        df = pd.DataFrame({'resistance': [0,1,2,3,4,2,3,10]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [(4,5)])    

def find_largest_force_drop(df: pd.DataFrame, subrange_list: List[Tuple]):
    curr_max = 0
    for subrange_start, subrange_end in subrange_list:
        subrange_diff = df['resistance'].iloc[subrange_start] - df['resistance'].iloc[subrange_end]
        if subrange_diff > curr_max: curr_max = subrange_diff
    return curr_max

class test_find_largest_force_drop(unittest.TestCase):

    def test_1(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), 1)
    def test_2(self):
        df = pd.DataFrame({'resistance': [0,1,2,3,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), 0)
    def test_3(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,3,1,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), 2)
    def test_4(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,2,1,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), 1)
    def test_5(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,0,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), 2)
    def test_6(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,0,5,4,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), 2)


if __name__ == '__main__':
    unittest.main()

