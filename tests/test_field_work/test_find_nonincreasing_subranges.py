import unittest
import pandas as pd
import sys

'''
for idx in resistance
    if resistance > threshold: continue
    if resistance <= threshold: 
        subrange start = idx
        in_subrange = 1
    elif resistance > threshold :
        if 90% of points are below subrange start res:
            subrange_end_idx = subrange argmin
        else:
            subrange_end_idx = idx
'''
def find_subrange_end_idx(subrange: pd.Series):
    # need to differentiate between a plateau and a drop
    subrange_start_idx = subrange.index[0]
    # print(f'subrange_start_idx: {subrange_start_idx}')
    idx = subrange.index[-1] + 1
    # print(f'idx: {idx}')

    subrange_start_value = subrange.loc[subrange_start_idx]
    num_points_in_subrange = len(subrange)
    num_points_below_subrange_start = len(subrange[subrange < subrange_start_value])
    # print(f"num_points_below_subrange_start: {num_points_below_subrange_start}")
    # case: force drop
    if not num_points_in_subrange: 
        print('Number of points in subrange is 0. Can\'t divide by 0')
        sys.exit(1) 
    if num_points_below_subrange_start / num_points_in_subrange > 0.5:
        # print('drop')
        subrange_end_idx = subrange.index[subrange.argmin()]
    # case: plateau
    else:
        # print('plateau')
        subrange_end_idx = idx - 1
    return subrange_end_idx

class Test_Find_Subrange_End_Idx(unittest.TestCase):

    def test1(self):
        subrange = pd.Series([5,5,5,5,5])
        self.assertEqual(find_subrange_end_idx(subrange), 4)

    def test2(self):
        subrange = pd.Series([5,4,3,2,2,2,2,2,1,2,2,2,2,2,6])
        self.assertEqual(find_subrange_end_idx(subrange), 8)

    def test3(self):
        subrange = pd.Series([5,6,5,6,7,5,6,7,6,5,5,6,7])
        self.assertEqual(find_subrange_end_idx(subrange), len(subrange)-1)

    def test4(self):
        subrange = pd.Series([5,5,5,5,4,5,5,5,5,5,5,5,5,5,5,5,5,5,5])
        self.assertEqual(find_subrange_end_idx(subrange), len(subrange)-1)

def find_nonincreasing_subranges(df: pd.DataFrame, subrange_upper_bound_percent: float, subrange_depth_min_length_percent: float):

    df = df.reset_index(drop=True)
    nonincreasing_subrange_list = []
    subrange_start_idx = 0
    in_nonincreasing_subrange = 0
    
    subrange_upper_bound = df['resistance'].max() * subrange_upper_bound_percent
    subrange_depth_min_length = df['resistance'].max() * subrange_depth_min_length_ratio

    for idx in range(1, len(df['resistance'])):

        is_above_threshold = df['resistance'].iloc[idx] > df['resistance'].iloc[subrange_start_idx] + subrange_upper_bound

        if is_above_threshold and in_nonincreasing_subrange:
            in_nonincreasing_subrange = 0
            subrange = df['resistance'][subrange_start_idx:idx]
            # print(subrange)
            subrange_end_idx = find_subrange_end_idx(subrange, subrange_start_idx, idx)

            subrange_start_value = df['depth'].loc[subrange_start_idx]
            subrange_end_value = df['depth'].loc[subrange_end_idx]

            if subrange_end_value - subrange_start_value > subrange_depth_min_length:
                nonincreasing_subrange_list.append((subrange_start_idx, subrange_end_idx))

        if is_above_threshold:
            subrange_start_idx = idx
        if not is_above_threshold and not in_nonincreasing_subrange:
            in_nonincreasing_subrange = 1
            subrange_start_idx = idx - 1

    return nonincreasing_subrange_list

subrange_upper_bound = 0
subrange_depth_min_length_ratio = 0.5

# class Test_Find_Drops_Plateues(unittest.TestCase):

#     def test1(self):
#         resistance = [0,1,2,3,4,5,6,7,7,7,7,10]
#         df = pd.DataFrame({
#             'resistance': resistance,
#             'depth': range(len(resistance))
#         })
#         drop_plateaus_subrangs = find_nonincreasing_subranges(df, subrange_upper_bound, subrange_depth_min_length_ratio)
#         self.assertEqual(drop_plateaus_subrangs, [(7,10)])

#     def test2(self):
#         df = pd.DataFrame({
#             'depth': range(10),
#             'resistance': [0,1,2,2,4,5,6,7,7,10]
#         })
#         drop_plateaus_subrangs = find_nonincreasing_subranges(df, subrange_upper_bound, subrange_depth_min_length_ratio)
#         self.assertEqual(drop_plateaus_subrangs, [(2,3),(7,8)])

#     def test3(self):
#         df = pd.DataFrame({
#             'depth': range(10),
#             'resistance': [0,1,2,3,4,5,6,7,7,7]
#         })
#         drop_plateaus_subrangs = find_nonincreasing_subranges(df, subrange_upper_bound, subrange_depth_min_length_ratio)
#         self.assertEqual(drop_plateaus_subrangs, [])
    
#     def test4(self):
#         df = pd.DataFrame({
#             'depth': range(10),
#             'resistance': [0,1,2,3,1,0,5,6,7,10]
#         })
#         drop_plateaus_subrangs = find_nonincreasing_subranges(df, subrange_upper_bound, subrange_depth_min_length_ratio)
#         self.assertEqual(drop_plateaus_subrangs, [(3,5)])
    
#     def test5(self):
#         df = pd.DataFrame({
#             'depth': range(10),
#             'resistance': [0,1,2,3,1,0,5,4,1,10]
#         })
#         drop_plateaus_subrangs = find_nonincreasing_subranges(df, subrange_upper_bound, subrange_depth_min_length_ratio)
#         self.assertEqual(drop_plateaus_subrangs, [(4,5), (7,8)])
    
#     def test6(self):
#         df = pd.DataFrame({
#             'depth': range(10),
#             'resistance': [0,1,2,0,2,0,2,3,4,6]
#         })
#         drop_plateaus_subrangs = find_nonincreasing_subranges(df, subrange_upper_bound, subrange_depth_min_length_ratio)
#         self.assertEqual(drop_plateaus_subrangs, [(2,6)])


if __name__ == '__main__':
    unittest.main()

    