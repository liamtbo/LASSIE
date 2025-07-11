import pandas as pd
import unittest

def find_resistance_pos_ranges(df):
    ranges_above_zero_list = []
    range_max_height_list = []

    in_range = False
    range_start_idx = None
    range_max_resistance = 0

    for i, res in enumerate(df["resistance"]):
        if res > 0:
            if not in_range:
                # starting a new range
                in_range = True
                if i > 0: range_start_idx = i - 1
                else: range_start_idx = 0
                range_max_resistance = res
            else:
                range_max_resistance = max(range_max_resistance, res)
        elif in_range:
            # end of a positive range
            ranges_above_zero_list.append((range_start_idx, i - 1))
            range_max_height_list.append(range_max_resistance)
            in_range = False

    # handle if last element was part of a range
    if in_range:
        ranges_above_zero_list.append((range_start_idx, len(df["resistance"]) - 1))
        range_max_height_list.append(range_max_resistance)

    return ranges_above_zero_list, range_max_height_list

class test_find_resistance_pos_ranges(unittest.TestCase):
    def test_1(self):
        df = pd.DataFrame({"resistance": [0, 1, 2, 3, 2, 1, 0]})
        self.assertEqual(find_resistance_pos_ranges(df), ([(0,5)], [3]))
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0]})
            self.assertEqual(find_resistance_pos_ranges(df), ([(0,1),(2,3)], [1,2]))
    def test_3(self):
            df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0]})
            self.assertEqual(find_resistance_pos_ranges(df), ([(1,2),(4,5)], [1,2]))
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5]})
        self.assertEqual(find_resistance_pos_ranges(df), ([(1,2),(4,5),(6,8)], [1,2,9]))
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8]})
        self.assertEqual(find_resistance_pos_ranges(df), ([(0,1)], [8]))
    def test_6(self):
        df = pd.DataFrame({"resistance": [1]})
        self.assertEqual(find_resistance_pos_ranges(df), ([(0,0)], [1]))
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0]})
        self.assertEqual(find_resistance_pos_ranges(df), ([], []))

def get_penetration_start_idx(df, range_max_res_thresh, max_spacing_between_ranges_thresh):
    pos_ranges_list, pos_ranges_max_res_list = find_resistance_pos_ranges(df)
    if len(pos_ranges_list) < 1: return 0

    # grab the range with the highest resistance (main curve)
    max_resistance_overall = max(pos_ranges_max_res_list)

    # grab all other ranges that have a max resistance within range_max_res_thresh of first_max_res_value
    ranges_within_res_thresh_list = []
    for i, pos_range in enumerate(pos_ranges_list):
        if pos_ranges_max_res_list[i] > max_resistance_overall * range_max_res_thresh:
             ranges_within_res_thresh_list.append(pos_range)
    
    # some files have high resistance noise way before penetration even starts
    # need to make sure this high res noise is not considered for start
    start_idx = ranges_within_res_thresh_list[-1][0] # init start idx with start of largest curve (last range is range_list)
    # case: only one range within res threshold, the main curve
    if len(ranges_within_res_thresh_list) < 2: return 0
    # case: many ranges within res threshold
    for i in range(len(ranges_within_res_thresh_list)-2, -1, -1): 
        range_start_i = df["depth"].iloc[ranges_within_res_thresh_list[i][1]]
        range_end_j = df["depth"].iloc[ranges_within_res_thresh_list[i+1][0]]
        if range_end_j - range_start_i > max_spacing_between_ranges_thresh * len(df["depth"]):
            start_idx = ranges_within_res_thresh_list[i+1][0]
            break
        else:
            start_idx = ranges_within_res_thresh_list[i][0]
    return start_idx

spacing = 0.2
class test_get_penetration_start_idx(unittest.TestCase):
    # test range_max_res_threshold by setting max_spacing to very high number st it doesn't matter
    def test_1(self):
        df = pd.DataFrame({"resistance": [0, 1, 2, 3, 2, 1, 0], "depth": [0,1,2,3,4,5,6]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=100), 0)
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0], 'depth': [0,1,2,3,4]})
            self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=100), 0)
    def test_3(self):
            df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0], 'depth': [0,1,2,3,4,5,6,7]})
            self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=100), 1)
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5], 'depth': [0,1,2,3,4,5,6,7,8]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=100), 1)
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8], 'depth': [0,1]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=100), 0)
    def test_6(self):
        df = pd.DataFrame({"resistance": [1], 'depth': [0]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=100), 0)
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0], 'depth':[0,1,2,3,4]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=100), 0)
    
    # testing spacing threshold
    def test_8(self):
        df = pd.DataFrame({"resistance": [0,8,0,0,0,0,0,0,0,3,10], 'depth':[0,1,2,3,4,5,6,7,8,9,10]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.2), 8)
    def test_9(self):
        df = pd.DataFrame({"resistance": [0,4,0,5,0,0,0,0,0,0,0,0,4,0,5,6,8], 'depth':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.2), 11)
    def test_10(self):
        df = pd.DataFrame({"resistance": [1,2], 'depth':[0,1]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=1), 0)
    def test_11(self):
        df = pd.DataFrame({"resistance": [0,1,0,2], 'depth':[0,1,2,3]})
        self.assertEqual(get_penetration_start_idx(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.1), 2)

def start_df_at_penetrations(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.2):
    start_idx = get_penetration_start_idx(df, range_max_res_thresh, max_spacing_between_ranges_thresh)
    df = df.iloc[start_idx:]
    return df

class test_start_df_at_penetrations(unittest.TestCase):
    def test_1(self):
        df = pd.DataFrame({"resistance": [0, 1, 2, 3, 2, 1, 0], "depth": [0,1,2,3,4,5,6]})
        self.assertEqual(start_df_at_penetrations(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.2)["resistance"].to_list(), [0, 1, 2, 3, 2, 1, 0])
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0], 'depth': [0,1,2,3,4]})
            self.assertEqual(start_df_at_penetrations(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.1)["resistance"].to_list(), [0, 2, 0])
    def test_3(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0], 'depth': [0,1,2,3,4,5,6,7]})
        self.assertEqual(start_df_at_penetrations(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.2)["resistance"].to_list(), [0, 2, 0, 0])
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5], 'depth': [0,1,2,3,4,5,6,7,8]})
        self.assertEqual(start_df_at_penetrations(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.1)["resistance"].to_list(), [0, 9, 5])
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8], 'depth': [0,1]})
        self.assertEqual(start_df_at_penetrations(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.2)["resistance"].to_list(), [5,8])
    def test_6(self):
        df = pd.DataFrame({"resistance": [1], 'depth': [0]})
        self.assertEqual(start_df_at_penetrations(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.2)["resistance"].to_list(), [1])
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0], 'depth':[0,1,2,3,4]})
        self.assertEqual(start_df_at_penetrations(df, range_max_res_thresh=0.1, max_spacing_between_ranges_thresh=0.2)["resistance"].to_list(), [0,0,0,0,0])

if __name__ == '__main__':
    unittest.main()