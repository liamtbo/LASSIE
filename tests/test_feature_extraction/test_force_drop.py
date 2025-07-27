import unittest
import pandas as pd
from typing import List, Tuple

def find_force_drop_subranges(df: pd.DataFrame, percent_of_max_resistance: float):
    down_moves_subrange_list = []
    resistance_max = df['resistance'].max()
    min_drop_size = resistance_max * percent_of_max_resistance
    curr_peak_idx = 0
    curr_trough_idx = 0
    in_drop_subrange = 0 # bool

    for idx in range(1, len(df['resistance'])):
        curr_peak = df['resistance'].iloc[curr_peak_idx]
        curr_trough = df['resistance'].iloc[curr_trough_idx]
        curr_resistance = df['resistance'].iloc[idx]

        if curr_resistance >= curr_peak and in_drop_subrange:
            in_drop_subrange = 0
            down_moves_subrange_list.append((curr_peak_idx, curr_trough_idx))

        if curr_resistance >= curr_peak:
            # curr_peak = df['resistance'].iloc[idx]
            curr_peak_idx = idx
            curr_trough_idx = idx
        elif curr_peak - curr_resistance >= min_drop_size and curr_resistance < curr_trough: 
            in_drop_subrange = 1
            curr_trough_idx = idx
    
    if in_drop_subrange: down_moves_subrange_list.append((curr_peak_idx, curr_trough_idx)) 
            
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
    def test_9(self):
        df = pd.DataFrame({'resistance': [0,1,2,3,4,5,6,7,8,9,10,1,5]})
        self.assertEqual(find_force_drop_subranges(df, 0.1), [(10,11)])    

def find_largest_force_drop(df: pd.DataFrame, subrange_list: List[Tuple]):
    curr_max_val = 0
    curr_max_level = 0
    for subrange_start, subrange_end in subrange_list:
        subrange_diff = df['resistance'].iloc[subrange_start] - df['resistance'].iloc[subrange_end]
        if subrange_diff > curr_max_val: 
            curr_max_val = subrange_diff
            curr_max_level = df['resistance'].iloc[subrange_start]
    return curr_max_val, curr_max_level

class test_find_largest_force_drop(unittest.TestCase):

    def test_1(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        print(f'subranges')
        self.assertEqual(find_largest_force_drop(df, subrange), (1, 2))
    def test_2(self):
        df = pd.DataFrame({'resistance': [0,1,2,3,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), (0,0))
    def test_3(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,3,1,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), (2,3))
    def test_4(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,2,1,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), (1,2))
    def test_5(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,0,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), (2,2))
    def test_6(self):
        df = pd.DataFrame({'resistance': [0,1,2,1,0,5,4,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), (2,2))
    def test_7(self):
        df = pd.DataFrame({'resistance': [0,1,2,3,0,1,0,10]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), (3,3))
    def test_8(self):
        df = pd.DataFrame({'resistance': [0,1,2,3,7]})
        subrange = find_force_drop_subranges(df, 0.1)
        self.assertEqual(find_largest_force_drop(df, subrange), (0,0))
    def test_9(self):
        df = pd.DataFrame({'resistance': [0,1,2,3,4,5,6,7,8,9,10,1,5]})
        subrange = find_force_drop_subranges(df, 0.1)
        print(subrange)
        self.assertEqual(find_largest_force_drop(df, subrange), (9,10))    
    
if __name__ == '__main__':
    unittest.main()

