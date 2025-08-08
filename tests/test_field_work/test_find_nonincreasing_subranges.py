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
def find_nonincreasing_subranges(df: pd.DataFrame, subrange_resistance_upper_bound_ratio, subrange_depth_min_length_ratio):

    df = df.reset_index(drop=True)
    nonincreasing_subrange_list = []
    subrange_start_idx = 0
    in_nonincreasing_subrange = 0
    
    resistance_subrange_upper_bound = df['resistance'].max() * subrange_resistance_upper_bound_ratio
    depth_subrange_length = df['resistance'].max() * subrange_depth_min_length_ratio


    for idx in range(1, len(df['resistance'])):
        print(f'idx res: {df["resistance"].iloc[idx]}')
        above_threshold = df['resistance'].iloc[idx] > df['resistance'].iloc[subrange_start_idx] + resistance_subrange_upper_bound
        print(f'above: {above_threshold}')
        below_threshold = df['resistance'].iloc[idx] <= df['resistance'].iloc[subrange_start_idx] + resistance_subrange_upper_bound
        print(f'below: {below_threshold}')
        print(f'below_threshold = {df['resistance'].iloc[idx]} <= {df['resistance'].iloc[subrange_start_idx]} + {resistance_subrange_upper_bound}')

        if above_threshold and in_nonincreasing_subrange:
            print('above threshold and in_nonincreasing_subrange')
            in_nonincreasing_subrange = 0
            subrange = df['resistance'][subrange_start_idx:idx]
            # print(f'subrange_start_idx: {subrange_start_idx}')
            # print(f'subrange:\n {subrange}')
            subrange_start_value = subrange.loc[subrange_start_idx]
            # need to differentiate between a plateau and a drop
            num_points_in_subrange = len(subrange)
            num_points_below_subrange_start = len(subrange[subrange < subrange_start_value])
            # case: force drop
            if not num_points_in_subrange: 
                print('Number of points in subrange is 0. Can\'t divide by 0')
                sys.exit(1) 
            if num_points_below_subrange_start / num_points_in_subrange > 0.9:
                subrange_end_idx = subrange.index[subrange.argmin()]
            # case: plateau
            else:
                subrange_end_idx = idx - 1
            # if 
            nonincreasing_subrange_list.append((subrange_start_idx, subrange_end_idx))

        if above_threshold:
            subrange_start_idx = idx
        if below_threshold and not in_nonincreasing_subrange:
            print('below threshold')
            in_nonincreasing_subrange = 1
            subrange_start_idx = idx - 1

    return nonincreasing_subrange_list

resistance_subrange_upper_bound = 0

class Test_Find_Drops_Plateues(unittest.TestCase):

    def test1(self):
        resistance = [0,1,2,3,4,5,6,7,7,7,7,10]
        df = pd.DataFrame({
            'resistance': resistance,
            'depth': range(len(resistance))
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, resistance_subrange_upper_bound)
        self.assertEqual(drop_plateaus_subrangs, [(7,10)])

    def test2(self):
        df = pd.DataFrame({
            'depth': range(10),
            'resistance': [0,1,2,2,4,5,6,7,7,10]
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, resistance_subrange_upper_bound)
        self.assertEqual(drop_plateaus_subrangs, [(2,3),(7,8)])

    def test3(self):
        df = pd.DataFrame({
            'depth': range(10),
            'resistance': [0,1,2,3,4,5,6,7,7,7]
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, resistance_subrange_upper_bound)
        self.assertEqual(drop_plateaus_subrangs, [])
    
    def test4(self):
        df = pd.DataFrame({
            'depth': range(10),
            'resistance': [0,1,2,3,1,0,5,6,7,10]
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, resistance_subrange_upper_bound)
        self.assertEqual(drop_plateaus_subrangs, [(3,5)])
    
    def test5(self):
        df = pd.DataFrame({
            'depth': range(10),
            'resistance': [0,1,2,3,1,0,5,4,1,10]
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df)
        self.assertEqual(drop_plateaus_subrangs, [(4,5), (7,8)])
    
    def test6(self):
        df = pd.DataFrame({
            'depth': range(10),
            'resistance': [0,1,2,0,2,0,2,3,4,6]
        })
        drop_plateaus_subrangs = find_nonincreasing_subranges(df, resistance_subrange_upper_bound)
        self.assertEqual(drop_plateaus_subrangs, [(2,6)])


if __name__ == '__main__':
    unittest.main()

    