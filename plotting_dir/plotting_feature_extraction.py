import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Tuple
import math

def find_idxs(find_filename_idxs: list[str], filenames_list: list[str]) -> list[int]:
    return [i for i, f in enumerate(filenames_list) if f in find_filename_idxs]

def find_subplot_dims(n):
    for i in range(int(math.sqrt(n)), 0, -1):
        if n % i == 0:
            # case: prime
            if (i == 1 or n % i == 1): 
                return find_subplot_dims(n+1)
            else: return i, n // i

def find_subplot_dims_orientation(n):
    x, y = find_subplot_dims(n)
    print(x, y)
    if y > 3:
        num_plots = y * x
        y = 3
        curr_plots = 0
        while curr_plots < num_plots:
            x += 1
            curr_plots = y * x
    return x, y

def find_force_drop_subranges(df: pd.DataFrame, percent_of_max_resistance: float):
    down_moves_subrange_list = []
    resistance_max = df['resistance'].max()
    min_drop_size = resistance_max * percent_of_max_resistance
    curr_peak_idx = 0
    curr_trough_idx = 0
    in_drop_subrange = 0 # bool

    for idx in range(1, len(df['resistance'])):
        curr_peak = df['resistance'].iloc[curr_peak_idx]
        curr_trough = df['resistance'].iloc[curr_trough_idx]
        curr_resistance = df['resistance'].iloc[idx]

        if curr_resistance >= curr_peak and in_drop_subrange:
            in_drop_subrange = 0
            down_moves_subrange_list.append((curr_peak_idx, curr_trough_idx))

        if curr_resistance >= curr_peak:
            curr_peak_idx = idx
            curr_trough_idx = idx
        elif curr_peak - curr_resistance >= min_drop_size and curr_resistance < curr_trough: 
            in_drop_subrange = 1
            curr_trough_idx = idx
    
    if in_drop_subrange: down_moves_subrange_list.append((curr_peak_idx, curr_trough_idx)) 
            
    return down_moves_subrange_list

def find_largest_force_drop(df: pd.DataFrame, subrange_list: List[Tuple]):
    curr_max_drop_size = 0
    curr_max_subrange_idxs = (0,0)
    for subrange_start, subrange_end in subrange_list:
        subrange_diff = df['resistance'].iloc[subrange_start] - df['resistance'].iloc[subrange_end]
        if subrange_diff > curr_max_drop_size: 
            curr_max_drop_size = subrange_diff
            curr_max_subrange_idxs = (subrange_start, subrange_end)
    return curr_max_drop_size, curr_max_subrange_idxs

def handle_max_depth(curve_data:pd.DataFrame, ax):
    resistance_at_max_depth = curve_data['resistance'].iloc[curve_data['depth'].values.argmax()]
    ax.plot([curve_data['depth'].max(),curve_data['depth'].max()], [0, resistance_at_max_depth], color='#D41159')

def handle_max_resistance(curve_data:pd.DataFrame, ax):
    depth_at_max_resistance = curve_data['depth'].iloc[curve_data['resistance'].values.argmax()]
    ax.plot([0,depth_at_max_resistance], [curve_data['resistance'].max(), curve_data['resistance'].max()], color='#D41159')

def handle_num_peaks(curve_data:pd.DataFrame, ax):
    subranges = find_force_drop_subranges(curve_data, percent_of_max_resistance=0.01)
    for start_idx, end_idx in subranges:
        ax.plot(curve_data['depth'].iloc[start_idx], curve_data['resistance'].iloc[start_idx], marker='v', markersize=7, color='#1A85FF')

def handle_largest_force_drop(curve_data:pd.DataFrame, ax):
    subranges = find_force_drop_subranges(curve_data, percent_of_max_resistance=0.01)
    _, (largest_drop_start, largest_drop_end) = find_largest_force_drop(curve_data, subranges)
    # if largest_drop_start != -1 and largest_drop_end != -1:
    ax.plot(curve_data['depth'].iloc[largest_drop_start], curve_data['resistance'].iloc[largest_drop_start], marker='v', markersize=7, color='#1A85FF')
    ax.plot(curve_data['depth'].iloc[largest_drop_end], curve_data['resistance'].iloc[largest_drop_end], marker='^', markersize=7, color='#D41159')

def handle_curve_shape(curve_data:pd.DataFrame, ax):
    ax.plot([0,curve_data['depth'].max()], [0,curve_data['resistance'].iloc[curve_data['depth'].values.argmax()]], color='red')

def handle_largest_force_drop_dep(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    _, (subrange_start, subrange_end) = find_largest_force_drop(curve_data, find_force_drop_subranges(curve_data, 0.001))
    ax.plot([dep.loc[subrange_start], dep.loc[subrange_start]], [0,res.loc[subrange_start]], color='red')

def handle_largest_force_drop_res(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    _, (subrange_start, subrange_end) = find_largest_force_drop(curve_data, find_force_drop_subranges(curve_data, 0.001))
    ax.plot([0,dep.loc[subrange_start]], [res.loc[subrange_start], res.loc[subrange_start]], color='red')

def handle_first_quarter_slope(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    ax.plot([0,dep.loc[round(0.25 * len(dep))]], [0,res.loc[round(0.25 * len(res))]], color='red')

def handle_second_quarter_slope(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    ax.plot([dep.loc[round(0.25 * len(dep))], dep.loc[round(0.50 * len(dep))]], 
            [res.loc[round(0.25 * len(res))], res.loc[round(0.50 * len(res))]], color='red')

def handle_third_quarter_slope(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    ax.plot([dep.loc[round(0.50 * len(dep))], dep.loc[round(0.75 * len(dep))]], 
            [res.loc[round(0.50 * len(res))], res.loc[round(0.75 * len(res))]], color='red')

def handle_fourth_quarter_slope(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    ax.plot([dep.loc[round(0.75 * len(dep))], dep.max()], 
            [res.loc[round(0.75 * len(res))], res.max()], color='red')

def handle_quartile_1(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    q1_res = res.quantile(0.25)
    ax.plot([0,dep.max()], [q1_res, q1_res], color='red')

def handle_quartile_2(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    q2_res = res.quantile(0.50)
    ax.plot([0,dep.max()], [q2_res, q2_res], color='red')

def handle_quartile_3(curve_data:pd.DataFrame, ax):
    res = curve_data['resistance']
    dep = curve_data['depth']
    q3_res = res.quantile(0.75)
    ax.plot([0,dep.max()], [q3_res, q3_res], color='red')

def plot_feature_selection(feature_names:List[str], curves_data:List[pd.DataFrame], plot_idx:int):
    # find dims of plot
    # plot_xdim, plot_ydim = find_subplot_dims_orientation(len(feature_names))
    # swtich x and y for presentation plots bc slides are horizontal in size
    plot_ydim, plot_xdim = find_subplot_dims_orientation(len(feature_names))


    # figsize=(round(plot_xdim*2), round(plot_ydim*5))
    figsize=(round(plot_xdim*5), round(plot_ydim*1.5))


    # normalize the x and y axis for every subplot
    all_depth_resistance_data = pd.concat(curves_data, axis=0, ignore_index=True)
    gloabl_max_depth = all_depth_resistance_data['depth'].max()
    gloabl_max_resistance = all_depth_resistance_data['resistance'].max()
    
    fig, axs = plt.subplots(plot_xdim, plot_ydim, figsize=figsize)
    flattened_axs = axs.flatten()
    for feature_i, feature_name in enumerate(feature_names): # loop over subplots
        ax = flattened_axs[feature_i]
        ax.set_xlim([0,gloabl_max_depth])
        ax.set_ylim([0,gloabl_max_resistance])
        font_size = 8
        ax.set_xlabel('Depth (m)', fontsize=font_size)
        ax.set_ylabel('Resistance (N)', fontsize=font_size)
        ax.set_title(feature_name.title(), fontsize=font_size)

        curve_data = curves_data[plot_idx]
        ax.plot(curve_data['depth'], curve_data['resistance'])
        if feature_name.lower() == "max_depth": 
            handle_max_depth(curve_data, ax)
        elif feature_name.lower() == "max_resistance":
            handle_max_resistance(curve_data, ax)
        elif feature_name.lower() == "num_peaks":
            ax.set_title(f'{feature_name.title()} (Normalized)', fontsize=font_size)
            handle_num_peaks(curve_data, ax)
        elif feature_name.lower() == "largest_force_drop":
            handle_largest_force_drop(curve_data, ax)
        elif feature_name.lower() == "curve_shape":
            handle_curve_shape(curve_data, ax)
        elif feature_name.lower() == "largest_force_drop_dep":
            handle_largest_force_drop_dep(curve_data, ax)
        elif feature_name.lower() == "largest_force_drop_res":
            handle_largest_force_drop_res(curve_data, ax)
        elif feature_name.lower() == "first_quarter_slope":
            handle_first_quarter_slope(curve_data, ax)
        elif feature_name.lower() == "second_quarter_slope":
            handle_second_quarter_slope(curve_data, ax)
        elif feature_name.lower() == "third_quarter_slope":
            handle_third_quarter_slope(curve_data, ax)
        elif feature_name.lower() == "fourth_quarter_slope":
            handle_fourth_quarter_slope(curve_data, ax)
        elif feature_name.lower() == "quartile_1":
            handle_quartile_1(curve_data, ax)
        elif feature_name.lower() == "quartile_2":
            handle_quartile_1(curve_data, ax)
        elif feature_name.lower() == "quartile_3":
            handle_quartile_3(curve_data, ax)
        else:
            print(f'feature name {feature_name} is not an extracted feature')
    plt.tight_layout()
    plt.show()
    plt.close()

def plot_feature_selection_seperately(feature_names: List[str], curves_data: List[pd.DataFrame], plot_idx: int):
    # normalize the x and y axis for every plot
    all_depth_resistance_data = pd.concat(curves_data, axis=0, ignore_index=True)
    global_max_depth = all_depth_resistance_data['depth'].max()
    global_max_resistance = all_depth_resistance_data['resistance'].max()

    curve_data = curves_data[plot_idx]

    for feature_name in feature_names:
        fig, ax = plt.subplots(figsize=(4, 4))  # one figure per feature
        ax.set_xlim([0, global_max_depth])
        ax.set_ylim([0, global_max_resistance])
        font_size = 10
        ax.set_xlabel('Depth (m)', fontsize=font_size)
        ax.set_ylabel('Resistance (N)', fontsize=font_size)
        # ax.set_title(feature_name.title(), fontsize=font_size)
        ax.set_title(feature_name.title(), fontsize=20)  # bigger than axis labels

        # plot the base curve
        ax.plot(curve_data['depth'], curve_data['resistance'])

        # feature-specific handlers
        fname = feature_name.lower()
        if fname == "max_depth": 
            handle_max_depth(curve_data, ax)
        elif fname == "max_resistance":
            handle_max_resistance(curve_data, ax)
        elif fname == "num_peaks":
            # ax.set_title(f'{feature_name.title()} (Normalized)', fontsize=font_size)
            handle_num_peaks(curve_data, ax)
        elif fname == "largest_force_drop":
            handle_largest_force_drop(curve_data, ax)
        elif fname == "curve_shape":
            handle_curve_shape(curve_data, ax)
        elif fname == "largest_force_drop_dep":
            handle_largest_force_drop_dep(curve_data, ax)
        elif fname == "largest_force_drop_res":
            handle_largest_force_drop_res(curve_data, ax)
        elif fname == "first_quarter_slope":
            handle_first_quarter_slope(curve_data, ax)
        elif fname == "second_quarter_slope":
            handle_second_quarter_slope(curve_data, ax)
        elif fname == "third_quarter_slope":
            handle_third_quarter_slope(curve_data, ax)
        elif fname == "fourth_quarter_slope":
            handle_fourth_quarter_slope(curve_data, ax)
        elif fname == "quartile_1":
            handle_quartile_1(curve_data, ax)
        elif fname == "quartile_2":
            handle_quartile_1(curve_data, ax)  # intentional?
        elif fname == "quartile_3":
            handle_quartile_3(curve_data, ax)
        else:
            print(f'Feature name {feature_name} is not an extracted feature')

        plt.tight_layout()
        plt.show()
        plt.close(fig)
