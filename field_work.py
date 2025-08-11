from typing import List, Tuple
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------------------------
"""Load data"""
if len(sys.argv) != 3:
    print('Error: two arguments must be provided:')
    print('\t1. data csv file path')
    print('\t2. figure folder destination path')
    print('ex: \n\tpython3 find_max_slope.py penetration_data.csv .')
    sys.exit(1)

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

# ----------------------------------------------
# Basic Transformations

def flip_over_y_axis(df_list: List[pd.DataFrame]):
    cleaned_df_list = []
    for df in df_list:
        copy_df = df.copy()
        copy_df['depth'] = -copy_df['depth']
        cleaned_df_list.append(copy_df)
    return cleaned_df_list

df_list = flip_over_y_axis(df_list)

def flip_over_x_axis(df_list: List[pd.DataFrame]):
    cleaned_df_list = []
    for df in df_list:
        copy_df = df.copy()
        copy_df['resistance'] = -copy_df['resistance']
        cleaned_df_list.append(copy_df)
    return cleaned_df_list

df_list = flip_over_x_axis(df_list)

def remove_points_after_max_depth(df_list: List[pd.DataFrame]):
    cleaned_list = []
    for i, df in enumerate(df_list):
        end_idx = df[df["depth"] == df["depth"].max()].index[0]
        cleaned_df = df.iloc[:end_idx+1]
        cleaned_list.append(cleaned_df)
    return cleaned_list

df_list = remove_points_after_max_depth(df_list)

def remove_points_before_min_depth(df_list: List[pd.DataFrame]):
    cleaned_list = []
    for i, df in enumerate(df_list):
        min_idx = df[df["depth"] == df["depth"].min()].index[0]
        cleaned_df = df.iloc[min_idx:]
        cleaned_list.append(cleaned_df)
    return cleaned_list

df_list = remove_points_before_min_depth(df_list)

def make_resistance_min_equal_zero(df_list: List[pd.DataFrame]):
    cleaned_df_list = []
    for df in df_list:
        copy_df = df.copy()
        copy_df["resistance"] = copy_df["resistance"].clip(lower=0)
        cleaned_df_list.append(copy_df)
    return cleaned_df_list

df_list = make_resistance_min_equal_zero(df_list)

def num_dataframes_with_ascending_depth(df_list: List[pd.DataFrame]):
    count = 0
    for df in df_list:
        if not (df['depth'].is_monotonic_increasing and df['depth'].is_unique): 
            count += 1
    return count

def only_increasing_depth(df_list: List[pd.DataFrame]):
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

def interpolate(df_list: List[pd.DataFrame], num_points):
    interp_df_list = []
    for df in df_list:
        x_intervals = np.linspace(0, df['depth'].max(), num_points, endpoint=True) # 100 points between 0 and trunc_level
        y_new = np.interp(x_intervals, df["depth"], df["resistance"])
        new_df = pd.DataFrame({'depth': x_intervals, 'resistance': y_new})
        interp_df_list.append(new_df)
    return interp_df_list

df_list = interpolate(df_list, 500)

def find_max_slope(df_list: List[pd.DataFrame]):
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

# ----------------------------------------------
"""Finding Peaks and Valleys"""
def find_subrange_end_idx(subrange: pd.DataFrame, subrange_start_idx: int, idx: int):
    # need to differentiate between a plateau and a drop
    subrange_start_value = subrange.loc[subrange_start_idx]
    num_points_in_subrange = len(subrange)
    num_points_below_subrange_start = len(subrange[subrange < subrange_start_value])
    # case: force drop
    if not num_points_in_subrange: 
        # print('Number of points in subrange is 0. Can\'t divide by 0')
        sys.exit(1) 
    if num_points_below_subrange_start / num_points_in_subrange > 0.9:
        subrange_end_idx = subrange.index[subrange.argmin()]
    # case: plateau
    else:
        subrange_end_idx = idx - 1
    return subrange_end_idx

def find_nonincreasing_subranges(df: pd.DataFrame, subrange_resistance_upper_bound_ratio, subrange_depth_min_length_ratio):

    df = df.reset_index(drop=True)
    nonincreasing_subrange_list = []
    subrange_start_idx = 0
    in_nonincreasing_subrange = 0
    
    resistance_subrange_upper_bound = df['resistance'].max() * subrange_resistance_upper_bound_ratio
    depth_subrange_length = df['resistance'].max() * subrange_depth_min_length_ratio

    for idx in range(1, len(df['resistance'])):
        # print(f'idx res: {df["resistance"].iloc[idx]}')
        above_threshold = df['resistance'].iloc[idx] > df['resistance'].iloc[subrange_start_idx] + resistance_subrange_upper_bound
        # print(f'above: {above_threshold}')

        if above_threshold and in_nonincreasing_subrange:
            # print('above threshold and in_nonincreasing_subrange')
            in_nonincreasing_subrange = 0
            subrange = df['resistance'][subrange_start_idx:idx]
            # print(f'subrange_start_idx: {subrange_start_idx}')
            # print(f'subrange:\n {subrange}')
            subrange_end_idx = find_subrange_end_idx(subrange, subrange_start_idx, idx)

            if df['depth'].loc[subrange_end_idx] - df['depth'].loc[subrange_start_idx] > depth_subrange_length:
                nonincreasing_subrange_list.append((subrange_start_idx, subrange_end_idx))

        if above_threshold:
            subrange_start_idx = idx
        if not above_threshold and not in_nonincreasing_subrange:
            # print('below threshold')
            in_nonincreasing_subrange = 1
            subrange_start_idx = idx - 1

    return nonincreasing_subrange_list

def plot(df_list: List[pd.DataFrame], plot_idx_range: List[int], title: str = 'Depth vs Resistance'):
    for idx in plot_idx_range:
        print(f"plot idx: {idx}")

        df = df_list[idx]
        # percent = 0.1
        subranges = find_nonincreasing_subranges(df, 0.1, 0.1)
        print(f"max_resistance: {df['resistance'].max()}")
        print(f"subranges: {[(float(df['resistance'].iloc[start]), float(df['resistance'].iloc[end])) for start, end in subranges]}")
        # print(f"")
        
        plt.figure(figsize=(5, 3))
        
        # Plot subrange start/end points
        for start_idx, end_idx in subranges:
            plt.plot(df['depth'].iloc[start_idx], df['resistance'].iloc[start_idx], marker='v', color='green')
            plt.plot(df['depth'].iloc[end_idx], df['resistance'].iloc[end_idx], marker='^', color='red')
        
        # Plot full depth vs resistance line
        plt.plot(df['depth'], df['resistance'],linestyle='-')
        plt.xlabel('Depth (m)')
        plt.ylabel('Resistance (N)')
        plt.title(f"{title} - Plot {idx}")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

plot(df_list, plot_idx_range=range(len(df_list)))

# ----------------------------------------------
"""Folder Creation and Saving of Figures"""
create_folder_names = ['figures']
def create_data_folders(create_folder_names, save_plots_dst):
    for folder in create_folder_names:
        folder = save_plots_dst + '/' + folder
        if not os.path.exists(folder):
            os.makedirs(folder)  # creates all intermediate directories if needed

# creates figures folder if it exists
create_data_folders(create_folder_names, save_plots_dst)

def save_plots(df_list: List[pd.DataFrame], filenames_list, save_plots_dst, save_bool=False, same_axis_range=True):
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