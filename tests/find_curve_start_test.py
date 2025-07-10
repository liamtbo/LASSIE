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

def get_penetration_start_idx(df, threshold):
    pos_ranges_list, pos_ranges_max_res_list = find_resistance_pos_ranges(df)
    if len(pos_ranges_list) < 1: return 0

    # grab the range with the highest resistance (main curve)
    max_resistance_overall = max(pos_ranges_max_res_list)

    # grab all other ranges that have a max resistance within threshold of first_max_res_value
    ranges_within_threshold_list = []
    for i, pos_range in enumerate(pos_ranges_list):
        if pos_ranges_max_res_list[i] > max_resistance_overall * threshold:
             ranges_within_threshold_list.append(pos_range)
    
    # return index of first range within threshold as start of ground penetration
    if not ranges_within_threshold_list: return 0 # no ranges found, just grab whole curve
    return ranges_within_threshold_list[0][0]

class test_get_penetration_start_idx(unittest.TestCase):
    def test_1(self):
        df = pd.DataFrame({"resistance": [0, 1, 2, 3, 2, 1, 0]})
        self.assertEqual(get_penetration_start_idx(df, threshold=0.1), 0)
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0]})
            self.assertEqual(get_penetration_start_idx(df, threshold=0.1), 0)
    def test_3(self):
            df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0]})
            self.assertEqual(get_penetration_start_idx(df, threshold=0.1), 1)
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5]})
        self.assertEqual(get_penetration_start_idx(df, threshold=0.1), 1)
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8]})
        self.assertEqual(get_penetration_start_idx(df, threshold=0.1), 0)
    def test_6(self):
        df = pd.DataFrame({"resistance": [1]})
        self.assertEqual(get_penetration_start_idx(df, threshold=0.1), 0)
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0]})
        self.assertEqual(get_penetration_start_idx(df, threshold=0.1), 0)

def start_df_at_penetrations(df, threshold=0.1):
    start_idx = get_penetration_start_idx(df, threshold)
    df = df.iloc[start_idx:]
    return df

class test_start_df_at_penetrations(unittest.TestCase):
    def test_1(self):
        df = pd.DataFrame({"resistance": [0, 1, 2, 3, 2, 1, 0]})
        self.assertEqual(start_df_at_penetrations(df, threshold=0.1)["resistance"].to_list(), [0, 1, 2, 3, 2, 1, 0])
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0]})
            self.assertEqual(start_df_at_penetrations(df, threshold=0.1)["resistance"].to_list(), [0, 1, 0, 2, 0])
    def test_3(self):
            df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0]})
            self.assertEqual(start_df_at_penetrations(df, threshold=0.1)["resistance"].to_list(), [0, 1, 0, 0, 2, 0, 0])
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5]})
        self.assertEqual(start_df_at_penetrations(df, threshold=0.1)["resistance"].to_list(), [0, 1, 0, 0, 2, 0, 9, 5])
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8]})
        self.assertEqual(start_df_at_penetrations(df, threshold=0.1)["resistance"].to_list(), [5,8])
    def test_6(self):
        df = pd.DataFrame({"resistance": [1]})
        self.assertEqual(start_df_at_penetrations(df, threshold=0.1)["resistance"].to_list(), [1])
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0]})
        self.assertEqual(start_df_at_penetrations(df, threshold=0.1)["resistance"].to_list(), [0,0,0,0,0])

if __name__ == '__main__':
    unittest.main()