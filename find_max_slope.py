from typing import List
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
import os

"""
Hello to any future debugger of this script
This script was initially developed for cleaning an entire folder of force-depth curves
which is why <df_list> is used. df_list is still being used because I had to change it in
a time sensitive manner ... 
"""


if len(sys.argv) != 3:
    print('two arguments must be provided: \n')
    print('\t1. data csv file path')
    print('\t2. figure folder path')
    

filename_path = sys.argv[1]
save_plots_dst = sys.argv[2]

df_list = []
filenames_list = []
ground_start_list = []

df = pd.read_csv(filename_path, skiprows=2)
df = df[['toeforce_y', 'toe_position_y']] # takes just the two important columns
df.columns = ["resistance", "depth"] # rename columns


def cm_to_m(cm):
    return cm / 100

def find_ground(df: pd.DataFrame):
    return cm_to_m(df['ground_height'].iloc[0])

df_list.append(df)
filenames_list.append(filename_path)
ground = find_ground(pd.read_csv(filename_path))
ground_start_list.append(ground)

def flip_over_y_axis(df_list):
    cleaned_df_list = []
    for df in df_list:
        copy_df = df.copy()
        copy_df['depth'] = -copy_df['depth']
        cleaned_df_list.append(copy_df)
    return cleaned_df_list

df_list = flip_over_y_axis(df_list)

def flip_over_x_axis(df_list):
    cleaned_df_list = []
    for df in df_list:
        copy_df = df.copy()
        copy_df['resistance'] = -copy_df['resistance']
        cleaned_df_list.append(copy_df)
    return cleaned_df_list

df_list = flip_over_x_axis(df_list)

def remove_points_after_max_depth(df_list):
    cleaned_list = []
    for i, df in enumerate(df_list):
        end_idx = df[df["depth"] == df["depth"].max()].index[0]
        cleaned_df = df.iloc[:end_idx+1]
        cleaned_list.append(cleaned_df)
    return cleaned_list

df_list = remove_points_after_max_depth(df_list)

def remove_points_before_min_depth(df_list):
    cleaned_list = []
    for i, df in enumerate(df_list):
        min_idx = df[df["depth"] == df["depth"].min()].index[0]
        cleaned_df = df.iloc[min_idx:]
        cleaned_list.append(cleaned_df)
    return cleaned_list

df_list = remove_points_before_min_depth(df_list)

def make_resistance_min_equal_zero(df_list):
    cleaned_df_list = []
    for df in df_list:
        copy_df = df.copy()
        copy_df["resistance"] = copy_df["resistance"].clip(lower=0)
        cleaned_df_list.append(copy_df)
    return cleaned_df_list

df_list = make_resistance_min_equal_zero(df_list)

def num_dataframes_with_ascending_depth(df_list):
    count = 0
    for df in df_list:
        if not (df['depth'].is_monotonic_increasing and df['depth'].is_unique): 
            count += 1
    return count

def only_increasing_depth(df_list):
    cleaned_df_list = []
    for df in df_list:
        mask = [1]  # keep the first row
        current_max_depth = df['depth'].iloc[0]
        for i in range(1, len(df)):
            if df['depth'].iloc[i] > current_max_depth:
                current_max_depth = df['depth'].iloc[i]
                mask.append(1)
            else:
                mask.append(0)
        mask_series = pd.Series(mask, index=df.index)
        cleaned_df_list.append(df.loc[mask_series.astype(bool)])

    return cleaned_df_list

df_list = only_increasing_depth(df_list)

def start_curve_at_ground(df_list: List[pd.DataFrame]):
    updated_df_list = []
    for i, df in enumerate(df_list):
        df = df.copy()
        df = df[df['depth'] > ground_start_list[i]].reset_index()
        df['depth'] = df['depth'] - df['depth'].iloc[0]
        updated_df_list.append(df)
    return updated_df_list

df_list = start_curve_at_ground(df_list)

def interpolate(df_list, num_points):
    interp_df_list = []
    for df in df_list:
        x_intervals = np.linspace(0, df['depth'].max(), num_points, endpoint=True) # 100 points between 0 and trunc_level
        y_new = np.interp(x_intervals, df["depth"], df["resistance"])
        new_df = pd.DataFrame({'depth': x_intervals, 'resistance': y_new})
        interp_df_list.append(new_df)
    return interp_df_list

df_list = interpolate(df_list, 500)

def find_max_slope(df_list):
    max_slope_list = []
    for i, df in enumerate(df_list):
        res = df['resistance']
        dep = df['depth']
        min_idx = res.idxmin()
        max_idx = res.idxmax()
        max_slope = (res.iloc[max_idx] - res.iloc[min_idx]) / (dep.iloc[max_idx] - dep.iloc[min_idx])
        max_slope_list.append(float(max_slope))
    return max_slope_list

print(f'max slope: {find_max_slope(df_list)[0]}')

create_folder_names = ['figures']
def create_data_folders(create_folder_names, save_plots_dst):
    for folder in create_folder_names:
        folder = save_plots_dst + '/' + folder
        if not os.path.exists(folder):
            os.makedirs(folder)  # creates all intermediate directories if needed

# creates figures folder if it exists
create_data_folders(create_folder_names, save_plots_dst)

def save_plots(df_list, filenames_list, save_plots_dst, save_bool=False, same_axis_range=True):
    if save_bool:
        combined_columnes = pd.concat(df_list, axis=0)
        for i, df in enumerate(df_list):
            plt.figure(figsize=(8,6))         # Optional: set figure size
            plt.plot(df['depth'], df['resistance'], marker='o', linestyle='-')
            plt.xlabel('Depth (m)')
            plt.ylabel('Resistance (N)')
            if "uncleaned" not in save_plots_dst and same_axis_range:
                plt.xlim([0, combined_columnes['depth'].max()])
                plt.ylim([0, combined_columnes['resistance'].max()])
            plt.title('Depth vs Resistance')
            plt.grid(True)
            plt.savefig(f'{save_plots_dst}/figures/{os.path.basename(filenames_list[i][:-3])}') # sliceing by -3 gets rid of extra '.csv' in filename_path
            plt.close()

save_plots(df_list, filenames_list, save_plots_dst, save_bool=True, same_axis_range=False)