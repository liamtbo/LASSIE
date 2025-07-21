import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.signal import find_peaks
from scipy.signal import savgol_filter

import tkinter as tk
from tkinter import filedialog

from bisect import bisect_right

protocol_chosen = ""
groundHeight = 0

def evaluation_function(ax, force_max, force_min, pos, force, average_force = 0):
    # for Mt. Hood, this function calculates the slope between the abs min and abs max

    # find the index of the absolute min and max
    min_idx = np.argmin(force[force_min])
    max_idx = np.argmax(force[force_max])

    # find the position of the absolute min and max
    min_pos = pos[force_min][min_idx]
    max_pos = pos[force_max][max_idx]

    if (min_pos >= max_pos):
        min_idx = force_min[0]
        min_pos = pos[force_min][min_idx]

    # find the min and max values
    min_val = force[force_min][min_idx]
    max_val = force[force_max][max_idx]

    # calculate the slope value
    x = [min_pos, max_pos]
    y = [min_val, max_val]

    slope = (y[1] - y[0]) / (x[1] - x[0])

    # plot the slope
    ax.plot(x, y, 'r--', label='Max Slope: ' + str(round(slope, 2)) + ' N/m')


    ### As an addendum, the following code will calculate the slope between the first min and max,
    ### if the absolute min and max are not the first min and max
    min_idx2 = force_min[0]
    max_idx2 = force_max[0]

    # if the first max is before or the absolute max, graph it
    if (max_idx2 < force_max[max_idx]) :
        min_pos2 = pos[min_idx2]
        max_pos2 = pos[max_idx2]

        min_val2 = force[min_idx2]
        max_val2 = force[max_idx2]

        x2 = [min_pos2, max_pos2]
        y2 = [min_val2, max_val2]

        slope2 = (y2[1] - y2[0]) / (x2[1] - x2[0])

        #plot the slope
        ax.plot(x2, y2, 'b--', label='First Peak Slope: ' + str(round(slope2, 2)) + ' N/m')
    
    if (average_force == 0) : # default. plot linear regression line
        # Our model is y = a * x, so things are quite simple, in this case...
        # x needs to be a column vector instead of a 1D vector for this, however.
        x = pos[:,np.newaxis]
        a, _, _, _ = np.linalg.lstsq(x, force)

        ax.plot(x, a*x, linestyle='dashed', color='teal', label='Linear Regression Slope: ' + str(round(a[0], 2)) + ' N/m')
    else :
        ax.axhline(average_force, linestyle='dashed', color='teal', label='Average Force: ' + str(round(average_force)) + ' N')

def plot_penetration(filename, ax):
    
    #set variable to P for choosing a title name
    global protocol_chosen
    protocol_chosen = "P"
    
    # read in data
    data = travelerRead(filename)

    # find the maximum extension, cut off data after that
    end_i = np.argmax(data['position_y'])
    y_pos_ = data['position_y'][0:end_i]
    
    # find the minimum extension, cut off data before that
    i_start = np.argmin(y_pos_)
    
    ############################
    #BUGPATCH Old Code:
    #BUGPATCH idx = find_first_nonnegative_index(data['force_y'][i_start:])
    #BUGPATCH i_start = max(i_start, idx+i_start)
    
    #New Code:
    idx = find_ground_start(data, 0, end_i)
    i_start = max(i_start, idx)
    ############################

    print('end_i', end_i)
    print('i_start: ', i_start)
    # print('idx: ', idx)

    print('len of pos_y: ', len(y_pos_))
    
    #y_pos_ = y_pos_[i_start:] - y_pos_[i_start]

    # find the corresponding force range
    penetration_ = data['force_y'][i_start:end_i]
    y_pos_ = data['position_y'][i_start:end_i] - data['position_y'][i_start]

    y_pos, penetration_force = trim_data(y_pos_, penetration_) 

    force_max, force_min, smooth_pos, smooth_force, average_force = minmax_finder(y_pos, penetration_force)

    ax.plot(y_pos, penetration_force, '-', label="Raw Force", linewidth=2)
    ax.plot(smooth_pos[force_min], smooth_force[force_min], "v", label="Local Minima", markersize=10, markerfacecolor='r')
    ax.plot(smooth_pos[force_max], smooth_force[force_max], "^", label="Local Maxima", markersize=10, markerfacecolor='g')

    evaluation_function(ax, force_max, force_min, smooth_pos, smooth_force)


    ax.set_xlabel('Vertical Depth (meters)', fontsize=18)
    ax.set_ylabel('Penetration Force (N)', fontsize=18)
    title = generate_title(filename)
    ax.set_title(title, fontsize=24)
    ax.legend()
    ax.tick_params(labelsize=16)

    # Assuming you have a folder path for saving the plots
    plot_save_path = filename.rstrip('.csv')

    save_path_png = plot_save_path + '.png'
    save_path_fig = plot_save_path + '.fig'
    
    # plt.savefig(save_path_png, dpi=300, bbox_inches='tight', transparent=True)
    # plt.savefig(save_path_fig, bbox_inches='tight')

#BUGPATCH 
#This function takes the position_y data from the csv, which has been previously adjusted for 
#ground height, from index 0 to the index of the maximum extension, and finds the index of the 
#cell that contains a value closest to 0. This is the index of when the leg first hits ground height.
def find_ground_start(data, ground_height_target, end_i):
    
    pos_y = pd.Series(data['position_y'][:end_i])
    
    closest_index = (pos_y - ground_height_target).abs().argmin()
    closest_value = data['position_y'][closest_index]
    
    print("Closest value to target value", ground_height_target," is ",closest_value,", located at index:",closest_index)
    
    #BUGPATCH
    #Previous Attempts, delete later
    #######################################################
    #print("GH Target:",ground_height_target)
    
    #closest_diff = float('inf')
    #for i in range(0,len(data)):
    #    diff = abs(data[i] - ground_height_target)
    #    if diff < closest_diff:
    #        closest_index = i
    #        closest_diff = diff
    #        closest_value = data[i]
    
    #differences = (data['position_y'] - ground_height_target).abs()

    # Exclude the target index itself from consideration
    #differences.loc[TARGET_INDEX] = float('inf')

    # Find the index of the closest value
    #closest_index = differences.idxmin()
    #closest_value = data.loc[closest_index, 'position_y']
    #print("Closest diff:",closest_diff)
    ########################################################3

    return closest_index

def plot_shear(filename, ax):
    
    #set variable to S for choosing a title name
    global protocol_chosen
    protocol_chosen = "S"
    
    data = travelerRead(filename) 
    #BUGPATCH: deleted -1 in line below
    position_max = data['position_x'].max()
    position_min = data['position_x'].min()
    y_pos_min = data['position_y'].min()

    
    #BUGPATCH
    ##########################################################
    print("min-max_s:", position_min, "-", position_max)
    ##########################################################

    #threshold_max = 0.96 * (position_max - position_min) + position_min #OG Threshold = 0.98, then 0.96
    #BUGPATCH
    ##########################################################
    #print("max_threshold:", threshold_max)
    ##########################################################

    i_start = np.argmin(data['position_x'])
    
    for i in range(i_start, len(data['time'])):
        if data['position_x'][i] == position_max:
            break
    i_end = i

    #BUGPATCH
    ##########################################################
    print("S_Position_Max:", position_max)
    print("S_Position_Min:", position_min)
    print("i_start_1:", i_start)
    print("i_end:", i_end)
    ##########################################################
    #i_end = np.argmax(data['position_x'])

    #idx = find_first_nonnegative_index(data['force_x'][i_start:i_end])
    idx = find_ground_start(data, 0, i_end)

    #i_start = max(i_start, (idx+i_start))
    i_start = max(i_start, idx)
    
    #BUGPATCH
    ##########################################################
    print("i_start_2:", i_start)
    for i in range(i_start, len(data['time'])):
        if data['position_y'][i] == y_pos_min:
            break
    i_y = i
    print("y_pos_min:", y_pos_min, "idx:", i_y)
    ##########################################################

    shear_force_ = data['force_x'][i_start:i_end] # used toe position x's min and max indexes to slice force_x?
    # x-axis
    x_pos_ = data['position_x'][i_start:i_end] - data['position_x'][i_start] # start every curve at 0
    

    x_pos, shear_force = trim_data(x_pos_, shear_force_)
    
    # find the local minima and maxima of the force curve
    TF_max, TF_min, smooth_pos, smooth_force, average_force = minmax_finder(x_pos, shear_force)

    ax.plot(x_pos, shear_force, '-', label="Raw Force", linewidth=2)
    ax.plot(smooth_pos[TF_min], smooth_force[TF_min], "v", label="Local Minima", markersize=10, markerfacecolor='r')
    ax.plot(smooth_pos[TF_max], smooth_force[TF_max], "^", label="Local Maxima", markersize=10, markerfacecolor='g')

    evaluation_function(ax, TF_max, TF_min, smooth_pos, smooth_force, average_force)

    ax.set_xlabel('Horizontal Position (meters)', fontsize=18)
    ax.set_ylabel('Shear Force (N)', fontsize=18)
    title = generate_title(filename)
    ax.set_title(title, fontsize=24)
    ax.legend()
    ax.tick_params(labelsize=16)

    # Assuming you have a folder path for saving the plots
    plot_save_path = filename.rstrip('.csv')

    save_path_png = plot_save_path + '.png'
    save_path_fig = plot_save_path + '.fig'
    
    # plt.savefig(save_path_png, dpi=300, bbox_inches='tight', transparent=True)
    # plt.savefig(save_path_fig, bbox_inches='tight')

def minmax_finder(position, force):
    # Sort the data based on x_pos values
    sorted_indices = np.argsort(position)
    position = position[sorted_indices]
    force = force[sorted_indices]

    # Remove duplicate x_pos values and correspondingly update the force values
    unique_indices = np.unique(position, return_index=True)[1]
    unique_pos = position[unique_indices]
    unique_force = force[unique_indices]

    # Smooth the force data using Savitzky-Golay filter
    smoothed_force = savgol_filter(unique_force, window_length=11, polyorder=3)

    # Calculate the average force for prominence threshold calculation
    average_force = np.trapz(unique_force, unique_pos) / unique_pos[-1]
    print('Average Force: ', average_force)
    prominence_threshold = np.abs(0.25 * average_force)

    # Find local maxima and minima x values using the prominence threshold
    pos_max, _ = find_peaks(smoothed_force, prominence=prominence_threshold)
    pos_min, _ = find_peaks(-1.0 * smoothed_force, prominence=prominence_threshold)

    # Insert a zero at the beginning of pos_min array
    pos_min = np.insert(pos_min, 0, 0)

    if (len(pos_max) == 0):
        pos_max = np.insert(pos_max, 0, len(unique_pos) - 1)

    # add the maximum force value if not present in the array
    max_force_idx = np.argmax(unique_force)
    if (max_force_idx not in pos_max):
        pos_max = np.insert(pos_max, len(pos_max), max_force_idx)

    force_maxima = unique_force[pos_max]
    force_minima = unique_force[pos_min]

    # Create dictionaries for minima and maxima
    minima = dict(zip(pos_min, force_minima))
    maxima = dict(zip(pos_max, force_maxima))

    return pos_max, pos_min, unique_pos, smoothed_force, average_force

def find_first_nonnegative_index(arr):
        index = bisect_right(arr, 1)
        if (index >= len(arr)):
            index = 0
        return index

# Function to remove any NaN or infinite values
def trim_data(x, y):
    mask = (~pd.isna(x)) & (~pd.isna(y))
    return x[mask], y[mask]

def travelerRead(filepath, mode = 0):
    
    global groundHeight
    
    print('Reading File...')
    with open(filepath, 'r') as file:
        # Read the header and variable names
        varNames = file.readline().strip().split(',')
        varValues = file.readline().strip().split(',')

    # Extract groundHeight value and store it in data.groundHeight
    groundHeight = float(varValues[-2]) / 100.0

    print('Ground Height: ', groundHeight)

    # Read the rest of the data using Pandas
    data = pd.read_csv(filepath, skiprows=2)

    # Convert column names to lowercase for consistency
    data.columns = [col.lower() for col in data.columns]

    # Correct sign of position_y for plotting
    data['toe_position_y'] = (-data['toe_position_y']) - groundHeight

    data['toeforce_y'] = -data['toeforce_y']
    
    # Extract required columns and assign them to the data dictionary
    data_dict = {
        'time': data['time'].values,
        'position_x': data['toe_position_x'].values,
        'position_y': data['toe_position_y'].values,
        'force_x': data['toeforce_x'].values,
        'force_y': data['toeforce_y'].values,
        'groundHeight': groundHeight
    }

    return data_dict

def generate_title(filepath):
    
    global protocol_chosen
    
    # filenames are in form 'WS23_L3_T1_S_12_perp2_Sat_Mar_11....'
    filename = filepath.split('/')[-1]
    filename_args = filename.split('_')
    
    
    print("File Name:",filename)
    print("File Args:",filename_args)
    
    protocol = protocol_chosen
    protocol_string = ''
    if (protocol == 'S'):
        protocol_string = 'Shear'
    elif (protocol == 'P'):
        protocol_string = 'Penetration'

    #Filenames with dates where the day is a single digit have an extra "_". If this occurs, 
    #we trim the extra "_" and create new file args to source the title from
    for i in range(0,len(filename)):
        current_item = filename[i]
        past_item = filename[i-1]
        if current_item == "_" and past_item == "_":
            new_filename = filename[:i] + filename[i+1:]
            print("Newest Filename:",new_filename)
            filename_args = new_filename.split('_')
            print("Newest File Args:",filename_args)
           
    weekday = filename_args[1]
    #weekday = weekday.replace('W', 'Weekday ')   

    month = filename_args[2]
    #month = month.replace('M', 'Month ')   
    
    day = filename_args[3]
    #day = day.replace('D', 'Day ')   
    
    hour = filename_args[4]
    
    minute = filename_args[5]
    
    year = str(filename_args[7])
    year_trim = year.rstrip(".csv")            
    
    #DEBUG: COMMENTED OUT
    #location = filename_args[1]
    #location = location.replace('L', 'Location ')

    #transect = filename_args[2]
    #transect = transect.replace('T', 'Transect ')

    
    #Create title in the form of "Penetration: Fri, May 30, 2025, 13:30"
    title = protocol_string + ': ' + weekday + ', ' + month + " " + day + ', ' + year_trim + ", " + hour + ":" + minute

    return title

def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        print(f"Selected file: {file_path}")
        # Add your file processing logic here, e.g., open the file and read its contents
    return file_path


def save_plot(filepath):
    filename = filepath.split('/')[-1]
    parent_path = filepath.rstrip(filename)
    figure_path = parent_path + 'figures/'
    print(figure_path)
    plot_save_name = filename.rstrip('.csv') + '.png'
    # directory_path = '/home/qianlab/lassie-traveler/experiment_records/MH23_Data/'
    save_path_png = figure_path + plot_save_name
    print(save_path_png)
    
    plt.savefig(save_path_png, bbox_inches='tight', transparent=False, dpi=300)

if __name__ == "__main__":
    # Create the ArgumentParser object
    parser = argparse.ArgumentParser(description='Force vs Displacement plotting script.\n Written by John Bush for RoboLAND Lab at USC.')

    # Add the --help option
    # parser.add_argument('--help', action='help', help='Show this help message and exit.')


    root = tk.Tk()
    root.withdraw()  # Hide the main window

    filepath = open_file()
    root.destroy()

    filename = filepath.split('/')[-1]

    filename_args = filename.split('_')

    protocol = filename_args[3]
    filename_args = filename.split('_')
    protocol = filename_args[3]
    print('Protocol: ', protocol)

    fig, ax = plt.subplots(figsize=(12, 6))
    
    plt.show(block=False)

    if (protocol == 'P'):
        plot_penetration(filepath, ax)
    elif (protocol == 'S'):
        plot_shear(filepath, ax)
    else:
        protocol = input('Type \'P\' for Penetration, \'S\' for Shear.')
        if (protocol == 'P'):
            plot_penetration(filepath, ax)
        elif (protocol == 'S'):
            plot_shear(filepath, ax)


                
    print(filepath)
    save_plot(filepath)
    plt.show()



    