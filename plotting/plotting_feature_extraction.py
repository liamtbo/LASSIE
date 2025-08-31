import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Tuple
import math

def find_idxs(find_filename_idxs: list[str], filenames_list: list[str]) -> list[int]:
    return [i for i, f in enumerate(filenames_list) if f in find_filename_idxs]

def find_num_subplots(n):
    for i in range(int(math.sqrt(n)), 0, -1):
        if n % i == 0:
            # case: prime
            if i == 1 or n % i == 1: return find_num_subplots(n+1)
            else: return i, n // i

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
    ax.plot(curve_data['depth'], curve_data['resistance'])
    resistance_at_max_depth = curve_data['resistance'].iloc[curve_data['depth'].values.argmax()]
    ax.plot([curve_data['depth'].max(),curve_data['depth'].max()], [0, resistance_at_max_depth], color='#D41159')

def handle_max_resistance(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    depth_at_max_resistance = curve_data['depth'].iloc[curve_data['resistance'].values.argmax()]
    ax.plot([0,depth_at_max_resistance], [curve_data['resistance'].max(), curve_data['resistance'].max()], color='#D41159')

def handle_num_peaks(curve_data:pd.DataFrame, ax):
    subranges = find_force_drop_subranges(curve_data, percent_of_max_resistance=0.01)
    ax.plot(curve_data['depth'], curve_data['resistance'])
    for start_idx, end_idx in subranges:
        ax.plot(curve_data['depth'].iloc[start_idx], curve_data['resistance'].iloc[start_idx], marker='v', markersize=7, color='#1A85FF')

def handle_largest_force_drop(curve_data:pd.DataFrame, ax):
    subranges = find_force_drop_subranges(curve_data, percent_of_max_resistance=0.01)
    _, (largest_drop_start, largest_drop_end) = find_largest_force_drop(curve_data, subranges)
    # if largest_drop_start != -1 and largest_drop_end != -1:
    ax.plot(curve_data['depth'], curve_data['resistance'])
    ax.plot(curve_data['depth'].iloc[largest_drop_start], curve_data['resistance'].iloc[largest_drop_start], marker='v', markersize=7, color='#1A85FF')
    ax.plot(curve_data['depth'].iloc[largest_drop_end], curve_data['resistance'].iloc[largest_drop_end], marker='^', markersize=7, color='#D41159')

def handle_curve_shape(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    ax.plot([0,curve_data['depth'].max()], [0,curve_data['resistance'].iloc[curve_data['depth'].values.argmax()]], color='red')

def handle_first_quarter_slope(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    res = curve_data['resistance']
    dep = curve_data['depth']
    ax.plot([0,dep.quantile(0.33)], [0,res.quantile(0.33)], color='red')

def handle_second_quarter_slope(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    res = curve_data['resistance']
    dep = curve_data['depth']
    ax.plot([dep.quantile(0.33),dep.quantile(0.66)], [res.quantile(0.33),res.quantile(0.66)], color='red')

def handle_third_quarter_slope(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    res = curve_data['resistance']
    dep = curve_data['depth']
    ax.plot([dep.quantile(0.66),dep.max()], [res.quantile(0.66),res.max()], color='red')

def handle_fourth_quarter_slope(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    res = curve_data['resistance']
    dep = curve_data['depth']
    ax.plot([dep.quantile(0.66),dep.max()], [res.quantile(0.66),res.max()], color='red')


def handle_q1(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    res = curve_data['resistance']
    dep = curve_data['depth']
    q1_res = res.quantile(0.25)

    ax.plot([0,dep.max()], [q1_res, q1_res], color='red')

def handle_q3(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    res = curve_data['resistance']
    dep = curve_data['depth']
    q3_res = res.quantile(0.75)
    ax.plot([0,dep.max()], [q3_res, q3_res], color='red')

def plot_feature_selection(feature_names:List[str], curves_data:List[pd.DataFrame], plot_idx:int):
    # find dims of plot
    # TODO un-hardcode this
    # plot_xdim, plot_ydim = find_num_subplots(len(feature_names))
    plot_xdim = 5
    plot_ydim = 3
    # if plot_xdim < plot_ydim: figsize=(10,6)
    # else: figsize=(10,10)
    figsize=(6,10)

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
        if feature_name == "max_depth": 
            handle_max_depth(curve_data, ax)
        elif feature_name == "max_resistance":
            handle_max_resistance(curve_data, ax)
        elif feature_name == "num_peaks":
            ax.set_title(f'{feature_name.title()} (Normalized)', fontsize=font_size)
            handle_num_peaks(curve_data, ax)
        elif feature_name == "largest_force_drop":
            handle_largest_force_drop(curve_data, ax)
        elif feature_name == "curve_shape":
            handle_curve_shape(curve_data, ax)
        # elif feature_name == "first_quarter_slope":
        #     curve_data = curves_data[feature_to_plot_idx["first_quarter_slope"][0]]
            # handle_first_third_slope(curve_data, ax)
        # elif feature_name == "second_quarter_slope":
        #     curve_data = curves_data[feature_to_plot_idx["second_quarter_slope"][0]]
        #     # handle_second_third_slope(curve_data, ax)
        # elif feature_name == "third_quarter_slope":
        #     curve_data = curves_data[feature_to_plot_idx["third_quarter_slope"][0]]
        #     # handle_third_third_slope(curve_data, ax)
        # elif feature_name == "fourth_quarter_slope":
        #     curve_data = curves_data[feature_to_plot_idx["fourth_quarter_slope"][0]]
            # handle_third_third_slope(curve_data, ax)
        # elif feature_name == "q1":
        #     curve_data = curves_data[feature_to_plot_idx["q1"][0]]
        #     handle_q1(curve_data, ax)
        # elif feature_name == "q3":
        #     curve_data = curves_data[feature_to_plot_idx["q3"][0]]
        #     handle_q3(curve_data, ax)
        else:
            print(f'feature name {feature_name} is not an extracted feature')
    plt.tight_layout()
    plt.show()
    plt.close()