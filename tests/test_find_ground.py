import pandas as pd
import unittest

def find_positive_subranges_of_resistance(df):
    """
    - args: 
        - dp: depth-resistance dataframe
    - returns:
        - parallel arrays: df['resistance'] subranges seperated by 0-values & the maximum resistance within each subrange
    - ex
        - if df["resistance"] = [0,1,2,1,0,1,2,3,4,5], this function would output ( [(0,3), (4,9)], [2, 5] ) 
        - first sub range is [0,1,2,1] with a max resistance of 2
        - second sub range is [0,1,2,3,4,5] with a max resistance of 5
    """
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
        self.assertEqual(find_positive_subranges_of_resistance(df), ([(0,5)], [3]))
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0]})
            self.assertEqual(find_positive_subranges_of_resistance(df), ([(0,1),(2,3)], [1,2]))
    def test_3(self):
            df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0]})
            self.assertEqual(find_positive_subranges_of_resistance(df), ([(1,2),(4,5)], [1,2]))
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5]})
        self.assertEqual(find_positive_subranges_of_resistance(df), ([(1,2),(4,5),(6,8)], [1,2,9]))
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8]})
        self.assertEqual(find_positive_subranges_of_resistance(df), ([(0,1)], [8]))
    def test_6(self):
        df = pd.DataFrame({"resistance": [1]})
        self.assertEqual(find_positive_subranges_of_resistance(df), ([(0,0)], [1]))
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0]})
        self.assertEqual(find_positive_subranges_of_resistance(df), ([], []))

def filter_subranges(subrange_list, subrange_max_resistance_list, subrange_max_resistance):
    max_resistance_overall = max(subrange_max_resistance_list)
    filtered_subranges = []
    for i, pos_range in enumerate(subrange_list):
        if subrange_max_resistance_list[i] > max_resistance_overall * subrange_max_resistance:
             filtered_subranges.append(pos_range)
    return filtered_subranges

def get_ground_start_idx(df, subrange_max_resistance, spacing_between_ranges):
    """
    - args
        - dp: depth-resistance dataframe
        - subrange_max_resistance (user defined threshold used for selecting resistance subranges above this value)
        - spacing_between_ranges (user defined threshold for droping subranges with a max resistance)
    - returns
        - index where the robotic arm contacts the ground - i.e where the curve should start
    """
    subrange_list, subrange_max_resistance_list = find_positive_subranges_of_resistance(df)

    if len(subrange_list) < 1: return 0
    
    filtered_subranges = filter_subranges(subrange_list, subrange_max_resistance_list, subrange_max_resistance)

    ground_start_idx = filtered_subranges[-1][0] # init ground_start_idx with start of largest curve (last subrange in range_list)
    if len(filtered_subranges) < 2: return ground_start_idx

    # reverse iterate over the filtered subranges and stop when the distance from subrange i to j is too high
    for i in range(len(filtered_subranges)-2, -1, -1): 
        subrange_i_start_idx = df["depth"].iloc[filtered_subranges[i][1]]
        subrange_j_end_idx = df["depth"].iloc[filtered_subranges[i+1][0]]
        if subrange_j_end_idx - subrange_i_start_idx > spacing_between_ranges * len(df["depth"]):
            ground_start_idx = filtered_subranges[i+1][0]
            break # found our final ground_start_idx
        else:
            ground_start_idx = filtered_subranges[i][0]
    return ground_start_idx

spacing = 0.2
class test_get_penetration_start_idx(unittest.TestCase):
    # test range_max_res_threshold by setting max_spacing to very high number st it doesn't matter
    def test_1(self):
        df = pd.DataFrame({"resistance": [0, 1, 2, 3, 2, 1, 0], "depth": [0,1,2,3,4,5,6]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=100), 0)
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0], 'depth': [0,1,2,3,4]})
            self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=100), 0)
    def test_3(self):
            df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0], 'depth': [0,1,2,3,4,5,6,7]})
            self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=100), 1)
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5], 'depth': [0,1,2,3,4,5,6,7,8]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=100), 1)
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8], 'depth': [0,1]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=100), 0)
    def test_6(self):
        df = pd.DataFrame({"resistance": [1], 'depth': [0]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=100), 0)
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0], 'depth':[0,1,2,3,4]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=100), 0)
    
    # testing spacing threshold
    def test_8(self):
        df = pd.DataFrame({"resistance": [0,8,0,0,0,0,0,0,0,3,10], 'depth':[0,1,2,3,4,5,6,7,8,9,10]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=0.2), 8)
    def test_9(self):
        df = pd.DataFrame({"resistance": [0,4,0,5,0,0,0,0,0,0,0,0,4,0,5,6,8], 'depth':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=0.2), 11)
    def test_10(self):
        df = pd.DataFrame({"resistance": [1,2], 'depth':[0,1]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=1), 0)
    def test_11(self):
        df = pd.DataFrame({"resistance": [0,1,0,2], 'depth':[0,1,2,3]})
        self.assertEqual(get_ground_start_idx(df, subrange_max_resistance=0.1, spacing_between_ranges=0.1), 2)

def start_curve_at_ground(df, subrange_max_resistance, spacing_between_ranges):
    """    
    - args
        - dp: depth-resistance dataframe
        - subrange_max_resistance (user defined threshold used for selecting resistance subranges above this value)
        - spacing_between_ranges (user defined threshold for droping subranges with a max resistance)
    - returns
        - dataframe with all data prior to first contact with ground removed
    """
    ground_start_idx = get_ground_start_idx(df, subrange_max_resistance, spacing_between_ranges)
    df = df.iloc[ground_start_idx:]
    return df

class test_start_df_at_penetrations(unittest.TestCase):
    def test_1(self):
        df = pd.DataFrame({"resistance": [0, 1, 2, 3, 2, 1, 0], "depth": [0,1,2,3,4,5,6]})
        self.assertEqual(start_curve_at_ground(df, subrange_max_resistance=0.1, spacing_between_ranges=0.2)["resistance"].to_list(), [0, 1, 2, 3, 2, 1, 0])
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0], 'depth': [0,1,2,3,4]})
            self.assertEqual(start_curve_at_ground(df, subrange_max_resistance=0.1, spacing_between_ranges=0.1)["resistance"].to_list(), [0, 2, 0])
    def test_3(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0], 'depth': [0,1,2,3,4,5,6,7]})
        self.assertEqual(start_curve_at_ground(df, subrange_max_resistance=0.1, spacing_between_ranges=0.2)["resistance"].to_list(), [0, 2, 0, 0])
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5], 'depth': [0,1,2,3,4,5,6,7,8]})
        self.assertEqual(start_curve_at_ground(df, subrange_max_resistance=0.1, spacing_between_ranges=0.1)["resistance"].to_list(), [0, 9, 5])
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8], 'depth': [0,1]})
        self.assertEqual(start_curve_at_ground(df, subrange_max_resistance=0.1, spacing_between_ranges=0.2)["resistance"].to_list(), [5,8])
    def test_6(self):
        df = pd.DataFrame({"resistance": [1], 'depth': [0]})
        self.assertEqual(start_curve_at_ground(df, subrange_max_resistance=0.1, spacing_between_ranges=0.2)["resistance"].to_list(), [1])
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0], 'depth':[0,1,2,3,4]})
        self.assertEqual(start_curve_at_ground(df, subrange_max_resistance=0.1, spacing_between_ranges=0.2)["resistance"].to_list(), [0,0,0,0,0])

if __name__ == '__main__':
    unittest.main()