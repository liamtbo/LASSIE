import pandas as pd
import unittest

# def find_curve_start_idx(df):
#     # stores range indexes as (start, end) tuple pairs
#     ranges_above_zero_list = []
#     range_max_height_list = []
#     range_start_idx = 0
#     range_end_idx = 0
#     range_max_resistance = 0

#     for i, res in enumerate(df["resistance"]):
#         if res > 0: 
#             range_end_idx = i
#             range_max_resistance = max(range_max_resistance, res)
#             if i == len(df["resistance"]) - 1:
#                 ranges_above_zero_list.append((range_start_idx, range_end_idx))
#                 range_max_height_list.append(range_max_resistance)
#         elif res == 0 or i == len(df["resistance"]) - 1:
#             # if we've actually captured a range
#             if range_end_idx - range_start_idx > 0:
#                 # updata parallel arrays
#                 ranges_above_zero_list.append((range_start_idx, range_end_idx))
#                 range_max_height_list.append(range_max_resistance)
#                 # reset variables
#                 range_start_idx = i
#                 range_end_idx = i
#                 range_max_resistance = 0
#             else:
#                 range_start_idx = i
#                 range_end_idx = i
#     return ranges_above_zero_list, range_max_height_list

def find_curve_start_idx(df):
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
                range_start_idx = i - 1
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


class test(unittest.TestCase):

    def test_1(self):
        df = pd.DataFrame({"resistance": [0, 1, 2, 3, 2, 1, 0]})
        self.assertEqual(find_curve_start_idx(df), ([(0,5)], [3]))
    def test_2(self):
            df = pd.DataFrame({"resistance": [0, 1, 0, 2, 0]})
            self.assertEqual(find_curve_start_idx(df), ([(0,1),(2,3)], [1,2]))
    def test_3(self):
            df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 0]})
            self.assertEqual(find_curve_start_idx(df), ([(1,2),(4,5)], [1,2]))
    def test_4(self):
        df = pd.DataFrame({"resistance": [0, 0, 1, 0, 0, 2, 0, 9, 5]})
        self.assertEqual(find_curve_start_idx(df), ([(1,2),(4,5),(6,8)], [1,2,9]))
    def test_5(self):
        df = pd.DataFrame({"resistance": [5,8]})
        self.assertEqual(find_curve_start_idx(df), ([(0,1)], [8]))
    def test_6(self):
        df = pd.DataFrame({"resistance": [1]})
        self.assertEqual(find_curve_start_idx(df), ([(0,0)], [1]))
    def test_7(self):
        df = pd.DataFrame({"resistance": [0,0,0,0,0]})
        self.assertEqual(find_curve_start_idx(df), ([], []))

if __name__ == '__main__':
    unittest.main()