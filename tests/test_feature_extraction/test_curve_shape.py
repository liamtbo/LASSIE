import numpy as np
import unittest
import pandas as pd

def find_curve_shape(df):
    x = df['depth'].to_numpy()
    y = df['resistance'].to_numpy()
    chord = np.linspace(df['resistance'].iloc[0], df['resistance'].iloc[-1], num=len(df['depth']))
    print(f"{y}: {chord}")
    y_diff = y - chord # makes chord the x-axis, any y_points above chord are pos, below are neg
    return np.trapezoid(y=y_diff, x=x)

class Test_Find_Curve_Shape(unittest.TestCase):

    def test_convex(self):
        df = pd.DataFrame({'resistance': [1,4,6,7], 'depth':[1,2,3,4]})
        self.assertGreater(find_curve_shape(df), 0)

    def test_concave(self):
        df = pd.DataFrame({'resistance': [1,2,4,8], 'depth':[1,2,3,4]})
        self.assertLess(find_curve_shape(df), 0)

if __name__ == '__main__':
    unittest.main()