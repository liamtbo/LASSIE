import matplotlib.pyplot as plt
from typing import List
import math
from sklearn.decomposition import PCA
import pandas as pd
from collections import Counter, defaultdict
import re


# unique coloring mappings for categories
label_color_map = {0: 'red', 1: 'gold', 2: 'blue', 3: 'green', 4: 'purple', 5: 'pink',
        6: 'turquoise', 7: 'orange', 8: 'lime', 9: 'magenta', 10: 'brown',
        11: 'lime', 12: 'teal', 13: 'navy', 14: 'maroon', 15: 'olive',
        16: 'coral', 17: 'grey', 18: 'salmon', 19: 'yellow'}

# size of figures produced
size_fig = (8,6)

# given a cluster color, this returns the filenames associated
def get_curve_idx_from_cluster_color(color, y_labels, after_mask_idxs: List[int], data_features_df):
    print(f"Indexes of curves assigned to {color} cluster: ")
    idxs = []
    for i, label in enumerate(y_labels):
        if label_color_map[label] == color:
            filename = data_features_df['filenames'].loc[after_mask_idxs[i]]
            idxs.append(after_mask_idxs[i])
            print(f'idx: {after_mask_idxs[i]}, filename: {filename}')
    return idxs

# for plotting specific curve idxs
def plot_specific_curves(plot_idxs: List[int], curve_data, data_features_df, color='black'):
    combined_columns = pd.concat(curve_data)
    for idx in plot_idxs:
        plt.figure(figsize=size_fig)
        plt.xlabel('Depth (m)')
        plt.ylabel('Resistance (N)')
        plt.title('Depth vs Resistance Curve')
        plt.xlim([0, combined_columns["depth"].max()])
        plt.ylim([0, combined_columns["resistance"].max()])
        print(data_features_df['filenames'].iloc[idx])
        plt.plot(curve_data[idx]["depth"], curve_data[idx]["resistance"], c=color)

import plotly.graph_objects as go

def plot_pca_biplot(pca, clustering_features_df):
    feature_loadings = []
    for i in range(len(clustering_features_df.columns)):
        feature_loadings.append(pca.components_[:,i])
    return feature_loadings

def extract_numerical_features(df:pd.DataFrame) -> pd.DataFrame:
    # should be updated if features are added !
    numerical_features = ['overall_slope', 'max_depth', 'max_resistance', 'num_peaks', 'largest_force_drop', 'curve_shape', 'largest_force_drop_res_level']
    df_copy = df.copy()
    for col in df.columns:
        if col not in numerical_features:
            df_copy.drop(col, axis=1, inplace=True)
    return df_copy

def extract_needed_cols(df:pd.DataFrame, remove_cols:List[str]):
    df_copy = df.copy()
    for col in df.columns:
        if col in remove_cols:
            df_copy.drop(col, axis=1, inplace=True)
    return df_copy

# plot PCA 
def plot_pca(clustering_features_df:pd.DataFrame, y_labels:List[int], num_pc:int, graph_title:str, ylabel_name:str, centroids:pd.DataFrame=pd.DataFrame()):
    clustering_features_df = clustering_features_df.copy()
    clustering_features_df = extract_numerical_features(clustering_features_df)
    
    # calculate PCA
    pca = PCA(n_components=num_pc) # reduce data down to 2 dims
    pca.fit(clustering_features_df.values)
    X_pca = pca.transform(clustering_features_df.values)
    centroid_ylabel_nums = centroids[f'{ylabel_name}_nums'].values
    if not centroids.empty:
        centroids = extract_numerical_features(centroids)
        centroid_transformations = pca.transform(centroids.values)
        centroid_colors = [label_color_map[cluster_num] for cluster_num in centroid_ylabel_nums]

    point_colors = [label_color_map[label] for label in y_labels]
    features_loadings = plot_pca_biplot(pca, clustering_features_df)

    if num_pc == 3:
        labels = [str(i) for i in clustering_features_df.index]
        # Main PCA scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=X_pca[:, 0],
            y=X_pca[:, 1],
            z=X_pca[:, 2],
            mode='text',
            text=labels,
            textfont=dict(size=8, color=point_colors),
            name='Data Points'
        )])
        if not centroids.empty:
            fig.add_trace(go.Scatter3d(
                x=centroid_transformations[:, 0],
                y=centroid_transformations[:, 1],
                z=centroid_transformations[:, 2],
                mode='markers',
                marker=dict(
                    symbol='diamond',
                    size=4,
                    color=centroid_colors
                )
            ))
        # Origin point at (0,0,0)
        fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(color='black', size=5),
            showlegend=False,
            name='Origin'
        ))
        # Feature loading vectors (e.g. PCA component directions)
        for i, (x, y, z) in enumerate(features_loadings):
            fig.add_trace(go.Scatter3d(
                x=[0, x * 3],
                y=[0, y * 3],
                z=[0, z * 3],
                mode='lines+text',
                line=dict(width=4),
                # text=[None, clustering_features_df.columns[i]],
                textposition='top center',
                name=clustering_features_df.columns[i]
            ))
        # Update layout with axis labels and title
        fig.update_layout(
            title='3D PCA Scatter Plot',
            autosize=True,
            scene=dict(
                xaxis=dict(
                    title=f'PC1 ({pca.explained_variance_ratio_[0]:.2f} var.)',
                    title_font=dict(size=11)  # change font size here
                ),
                yaxis=dict(
                    title=f'PC2 ({pca.explained_variance_ratio_[1]:.2f} var.)',
                    title_font=dict(size=11)
                ),
                zaxis=dict(
                    title=f'PC3 ({pca.explained_variance_ratio_[2]:.2f} var.)',
                    title_font=dict(size=11)
                )
            )
        )
        fig.show()
    

# creates one plot where all curves, colored by their respective cluster, are plotted
def plot_clusters_together(y_labels: List[int], after_mask_idxs: List[int], 
                           curve_data, clustering_method: str = ""):
    a = 0.3
    combined_columns = pd.concat(curve_data, axis=0, ignore_index=True)
    plt.figure(figsize=size_fig)
    for i, y in enumerate(y_labels):
        df = curve_data[after_mask_idxs[i]]
        color = label_color_map.get(y, 'black')  # default to black if label not in map
        plt.plot(df["depth"], df["resistance"], color=color, alpha=a)
    plt.xlabel('Depth (m)')
    plt.ylabel('Resistance (N)')
    plt.title('Depth vs Resistance Curves')
    plt.xlim([0, combined_columns["depth"].max()])
    plt.ylim([0, combined_columns["resistance"].max()])
    # plt.savefig(f"figures/{clustering_method.lower()}/cluster_curves", bbox_inches='tight')
    plt.show()
    plt.close() # clear figure 

def find_num_subplots(n):
    for i in range(int(math.sqrt(n)), 0, -1):
        if n % i == 0:
            # case: prime
            if i == 1 or n % i == 1: return find_num_subplots(n+1)
            else: return i, n // i

def map_cluster_to_idx(y_labels:List[int], curve_idxs:List[int]):
    zipped_label_to_idx = zip(y_labels, curve_idxs)
    sorted_label_to_idx = sorted(zipped_label_to_idx, key=lambda x: x[0])
    cluster_to_idx = defaultdict(list)
    for cluster, curve_idx in sorted_label_to_idx:
        cluster_to_idx[int(cluster)].append(curve_idx)
    return cluster_to_idx

def plot_clusters_seperately(y_labels: pd.Series, 
                             curve_data: List[pd.DataFrame], ylabel_name:str, 
                             clustering_method: str = "", cluster_category_names=[], bold_idxs=[], 
                             pseudo_corrections:pd.DataFrame=pd.DataFrame()):
    curve_idxs = y_labels.index.tolist()
    all_depth_resistance_data = pd.concat(curve_data, axis=0, ignore_index=True)
    gloabl_max_depth = all_depth_resistance_data['depth'].max()
    gloabl_max_resistance = all_depth_resistance_data['resistance'].max()

    opacity = 0.5
    labels_mapped_frequency = Counter(y_labels)
    x, y = find_num_subplots(len(labels_mapped_frequency))
    if x < y: figsize=(10,6)
    else: figsize=(10,10)

    cluster_to_idx = map_cluster_to_idx(y_labels, curve_idxs)

    fig, axs = plt.subplots(x,y,figsize=figsize)
    fig.suptitle('Cluster Depth vs Resistance')
    # for each cluster_i
    subplot_idx = 0
    axs_flattened = axs.flatten()
    for cluster_i in cluster_to_idx.keys():
        ax = axs_flattened[subplot_idx]
        ax.set_xlim([0,gloabl_max_depth])
        ax.set_ylim([0,gloabl_max_resistance])
        ax.set_xlabel('Depth (m)', fontsize=8)
        ax.set_ylabel('Resistance (N)', fontsize=8)
        if cluster_category_names: ax.set_title(f'{cluster_category_names[cluster_i].title()} Cluster', fontsize=8)
        else: ax.set_title(f'{cluster_color.title()} Cluster', fontsize=8)

        # for each curve in cluster_i
        cluster_correction_idxs = []
        cluster_bold_idxs = []
        for curve_i in cluster_to_idx[cluster_i]:

            cluster_color = label_color_map.get(cluster_i, 'black')
            curve = curve_data[curve_i]
            
            curve_needs_corrections = curve_i in pseudo_corrections.index
            curve_needs_bold = curve_i in bold_idxs
            if curve_needs_corrections or curve_needs_bold:
                if curve_needs_corrections: cluster_correction_idxs.append(curve_i)
                if curve_needs_bold: cluster_bold_idxs.append(curve_i)
            else:
                ax.plot(curve['depth'], curve['resistance'], color=cluster_color, alpha=opacity)

        for curve_i in cluster_bold_idxs:
            curve = curve_data[curve_i]
            ax.plot(curve['depth'], curve['resistance'], color=cluster_color, alpha=1, linewidth=2)

        for curve_i in cluster_correction_idxs:
            label_num = pseudo_corrections.loc[curve_i][f'{ylabel_name}_nums']
            cluster_color = label_color_map.get(label_num, 'black')
            curve = curve_data[curve_i]
            ax.plot(curve['depth'], curve['resistance'], color=cluster_color, alpha=1, linewidth=2)

        subplot_idx += 1

    plt.tight_layout()
    plt.show()
    plt.close()

def handle_max_depth(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    resistance_at_max_depth = curve_data['resistance'].iloc[curve_data['depth'].values.argmax()]
    ax.plot([curve_data['depth'].max(),curve_data['depth'].max()], [0, resistance_at_max_depth])
def handle_max_resistance(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
    depth_at_max_resistance = curve_data['depth'].iloc[curve_data['resistance'].values.argmax()]
    ax.plot([0,depth_at_max_resistance], [curve_data['resistance'].max(), curve_data['resistance'].max()])
def handle_num_peaks(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
def handle_largest_force_drop(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])
def handle_curve_shape(curve_data:pd.DataFrame, ax):
    ax.plot(curve_data['depth'], curve_data['resistance'])

def plot_feature_selection(curves_data:List[pd.DataFrame], feature_to_plot_idx:dict[str:List[int]]):
    # find dims of plot
    plot_xdim, plot_ydim = find_num_subplots(len(feature_to_plot_idx.keys()))
    if plot_xdim < plot_ydim: figsize=(10,6)
    else: figsize=(10,10)
    # normalize the x and y axis for every subplot
    all_depth_resistance_data = pd.concat(curves_data, axis=0, ignore_index=True)
    gloabl_max_depth = all_depth_resistance_data['depth'].max()
    gloabl_max_resistance = all_depth_resistance_data['resistance'].max()
    
    fig, axs = plt.subplots(plot_xdim, plot_ydim, figsize=figsize)
    flattened_axs = axs.flatten()
    for feature_i, feature_name in enumerate(feature_to_plot_idx.keys()): # loop over subplots
        ax = flattened_axs[feature_i]
        ax.set_xlim([0,gloabl_max_depth])
        ax.set_ylim([0,gloabl_max_resistance])
        ax.set_xlabel('Depth (m)', fontsize=8)
        ax.set_ylabel('Resistance (N)', fontsize=8)
        ax.set_title(feature_name.title(), fontsize=8)

        if feature_name == "max_depth": 
            curve_data = curves_data[feature_to_plot_idx['max_depth'][0]]
            handle_max_depth(curve_data, ax)
        elif feature_name == "max_resistance":
            curve_data = curves_data[feature_to_plot_idx['max_resistance'][0]]
            handle_max_resistance(curve_data, ax)
        elif feature_name == "num_peaks":
            curve_data = curves_data[feature_to_plot_idx['num_peaks'][0]]
            handle_num_peaks(curve_data, ax)
        elif feature_name == "largest_force_drop":
            curve_data = curves_data[feature_to_plot_idx['largest_force_drop'][0]]
            handle_largest_force_drop(curve_data, ax)
        elif feature_name == "curve_shape":
            curve_data = curves_data[feature_to_plot_idx['curve_shape'][0]]
            handle_curve_shape(curve_data, ax)
        else:
            print(f'feature name {feature_name} is not an extracted feature')
    plt.tight_layout()
    plt.show()
    plt.close()



def pca_analysis(clustering_features_df):
    clustering_features_df = extract_numerical_features(clustering_features_df.copy())
    pca = PCA(n_components=len(clustering_features_df.columns))
    pca.fit(clustering_features_df.values)

    # principal component table
    principle_components_table = pd.DataFrame({
        "PC": range(1,pca.n_components_+1),
        "Eigenvalue": pca.explained_variance_,
        "Proportion": pca.explained_variance_ratio_
    })
    principle_components_table.set_index('PC', inplace=True)
    principle_components_table["Cumulative"] = principle_components_table["Proportion"].cumsum()
    print(principle_components_table)

    loadings = pca.components_.T
    pc_labels = [f'PC{i+1}' for i in range(loadings.shape[1])]
    loadings_df = pd.DataFrame(loadings, index=clustering_features_df.columns, columns=pc_labels)
    print('\n')
    print(loadings_df)

def group_data_by_transect(unique_transects, data_features_df):
    spatial_features_df = data_features_df[data_features_df['distances'].notna()]
    transect_dict = {}
    for transect in unique_transects:
        transect_dict[transect] = spatial_features_df[spatial_features_df['filenames'].str.contains(transect)]
    for transect in unique_transects:
        transect_dict[transect] = transect_dict[transect].sort_values(by=['distances'])
    
    return transect_dict

def find_num_subplots(n):
    for i in range(int(math.sqrt(n)), 0, -1):
        if n % i == 0:
            # prime
            if i == 1 or n % i == 1: return find_num_subplots(n+1)
            else: return i, n // i

def plot_transect_subplots(curve_data, transect_dict, filename_to_depth_resist):
    for transect, samples in transect_dict.items():
        masked_idxs = samples.index.tolist()
        # for transect in unique_transects:
        combined_columns = pd.concat(curve_data, axis=0, ignore_index=True)
        x, y = find_num_subplots(len(samples))
        fig, axs = plt.subplots(x,y,figsize=(10,6))
        fig.suptitle(f"Transect: {transect.title()}")
        for i, ax in enumerate(axs.flatten()):
            ax.set_xlim([0, combined_columns["depth"].max()])
            ax.set_ylim([0, combined_columns["resistance"].max()])
            curve_features = samples.loc[masked_idxs[i]]
            sample_point = re.search(r'P_\d+', curve_features['filenames'])
            ax.set_title(f'{sample_point.group()}: {curve_features['distances']} ft.')
            # ax.set_title(curve_features['filenames'], fontsize=10)
            filename = curve_features['filenames']
            curve = filename_to_depth_resist[filename]
            ax.plot(curve['depth'], curve['resistance'], color=label_color_map[curve_features['liams_ylabels']])
        plt.tight_layout()
        plt.show()