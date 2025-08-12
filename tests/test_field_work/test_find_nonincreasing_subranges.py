import unittest
import pandas as pd
import sys
from typing import List, Tuple

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
def find_subrange_end_idx(subrange: pd.Series) -> int:
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


def find_nonincreasing_subranges(df: pd.DataFrame, subrange_upper_bound_percent: float, subrange_depth_min_length_percent: float) -> List[Tuple[int, int]]:
    in_subrange = 0
    subrange_list = []
    subrange_start_idx = 0
    res = df['resistance']
    subrange_upper_bound = df['resistance'].max() * subrange_upper_bound_percent
    print(f'subrange_upper_bound: {subrange_upper_bound}')

    for idx in range(1, len(res)):
        # if not in_subrange: subrange_start_idx = idx
        if in_subrange: above_threshold = res[idx] > res[subrange_start_idx] + subrange_upper_bound
        else: above_threshold = res[idx] > res[idx - 1] + subrange_upper_bound

        print(f'idx value: {res[idx]}')
        if not above_threshold and not in_subrange:
            print('\tnot above_threshold and not in_subrange')
            in_subrange = 1
            subrange_start_idx = idx - 1

        if above_threshold and in_subrange:
            print('\tabove_threshold and in_subrange')
            in_subrange = 0
            subrange_list.append((subrange_start_idx, idx - 1))

            previous_idx_start_of_subrange = res[idx] <= res[idx - 1] + subrange_upper_bound
            if previous_idx_start_of_subrange:
                print('\tprevious_idx_start_of_subrange')
                in_subrange = 1
                subrange_start_idx = idx - 1

    if in_subrange: subrange_list.append((subrange_start_idx, idx))
    return subrange_list


class Test_Find_Drops_Plateues(unittest.TestCase):

    def test1(self):
        res = [1,2,3,4,5,6,7,8,9,10]
        df = pd.DataFrame({
            'depth': range(len(res)),
            'resistance': res
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, 0.1, 0.0)
        self.assertEqual(drop_plateaus_subrangs, [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)])

    def test2(self):
        res = [1,2,3,4,5,5,7,8,9,10]
        df = pd.DataFrame({
            'depth': range(len(res)),
            'resistance': res
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, 0.0, 0.0)
        self.assertEqual(drop_plateaus_subrangs, [(4,5)])

    def test3(self):
        res = [1,2,3,4,5,5,5,8,9,10]
        df = pd.DataFrame({
            'depth': range(len(res)),
            'resistance': res
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, 0.0, 0.0)
        self.assertEqual(drop_plateaus_subrangs, [(4,6)])

    def test4(self):
        res = [1,2,3,4,5,4,5,8,9,10]
        df = pd.DataFrame({
            'depth': range(len(res)),
            'resistance': res
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, 0.0, 0.0)
        self.assertEqual(drop_plateaus_subrangs, [(4,6)])

    def test5(self):
        res = [1,2,3,4,5,5,5,8,9,10]
        df = pd.DataFrame({
            'depth': range(len(res)),
            'resistance': res
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, 0.2, 0.0)
        self.assertEqual(drop_plateaus_subrangs, [(0,2),(2,6),(7,9)])

    def test6(self):
        res = [1,2,3,3,3,4,5,6,7,7,7,8,9,10]
        df = pd.DataFrame({
            'depth': range(len(res)),
            'resistance': res
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, 0.0, 0.0)
        self.assertEqual(drop_plateaus_subrangs, [(2,4),(8,10)])

    # TODO need to add in min subrange len
    # def test7(self):
    #     res = [1,2,3,4,5,4,3,4,5,6,7,8,9,10]
    #     df = pd.DataFrame({
    #         'depth': range(len(res)),
    #         'resistance': res
    #     })
    #     drop_plateaus_subrangs = find_nonincreasing_subranges(df, 0.1, 0.0)
    #     self.assertEqual(drop_plateaus_subrangs, [(3,8)])

if __name__ == '__main__':
    unittest.main()




    