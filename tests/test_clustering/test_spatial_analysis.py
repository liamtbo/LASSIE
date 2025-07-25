import unittest
import pandas as pd
import pandas.testing as pdt

# unique_transects = ['L1_T1', 'L2_T1', 'L2_T2', 'L3_T1']
def group_data_by_transect(unique_transects, data_features_df):
    spatial_features_df = data_features_df[data_features_df['distances'].notna()]
    transect_dict = {}
    for transect in unique_transects:
        transect_dict[transect] = spatial_features_df[spatial_features_df['filenames'].str.contains(transect)]
    for transect in unique_transects:
        transect_dict[transect] = transect_dict[transect].sort_values(by=['distances'])
    return transect_dict



class Test_Unique_transects(unittest.TestCase):

    def test_1(self):
        unique_transects = ['L1_T1', 'L2_T1']
        df = pd.DataFrame({
            'filenames': ['WS23_L1_T1_P_0', 'WS23_L1_T1_P_1', 'WS23_L2_T1_P_2', 'WS23_L2_T1_P_3'],
            'distances': [1, 5, 3, 2]
        })
        expected = {
            'L1_T1': pd.DataFrame({
                'filenames': ['WS23_L1_T1_P_0', 'WS23_L1_T1_P_1'],
                'distances': [1, 5]
            }),
            'L2_T1': pd.DataFrame({
                'filenames': ['WS23_L2_T1_P_3', 'WS23_L2_T1_P_2'],
                'distances': [2, 3]
            })
        }
        result = group_data_by_transect(unique_transects, df)
        for key in expected:
            pdt.assert_frame_equal(result[key].reset_index(drop=True), expected[key].reset_index(drop=True))

if __name__ == '__main__':
    unittest.main()