import matplotlib.pyplot as plt
from typing import List
import math
from sklearn.decomposition import PCA
import pandas as pd
from collections import Counter
import re

# unique coloring mappings for categories
label_color_map = {0: 'red', 1: 'gold', 2: 'blue', 3: 'green', 4: 'purple', 5: 'pink',
        6: 'brown', 7: 'orange', 8: 'cyan', 9: 'magenta', 10: 'turquoise',
        11: 'lime', 12: 'teal', 13: 'navy', 14: 'maroon', 15: 'olive',
        16: 'coral', 17: 'grey', 18: 'salmon', 19: 'yellow'}

# size of figures produced
size_fig = (4,3)

# given a cluster color, this returns the filenames associated
def get_curve_idx_from_cluster_color(color, y_labels, after_mask_indicies: List[int], data_features_df):
    print(f"Indexes of curves assigned to {color} cluster: ")
    for i, label in enumerate(y_labels):
        if label_color_map[label] == color:
            print(f'idx: {i}, filename: {data_features_df['filenames'].iloc[after_mask_indicies[i]]}')

# for plotting specific curve indicies
def plot_specific_curves(plot_indicies: List[int], depth_resist_curve_df_list):
    combined_columns = pd.concat(depth_resist_curve_df_list)
    for idx in plot_indicies:
        plt.figure(figsize=size_fig)
        plt.xlabel('Depth (m)')
        plt.ylabel('Resistance (N)')
        plt.title('Depth vs Resistance Curve')
        plt.xlim([0, combined_columns["depth"].max()])
        plt.ylim([0, combined_columns["resistance"].max()])
        plt.plot(depth_resist_curve_df_list[idx]["depth"], depth_resist_curve_df_list[idx]["resistance"], c='black')

# plot PCA 
def plot_pca(clustering_features_df_list: pd.DataFrame, y_labels: List[int], graph_title: str, kmeans_centroids=[]):
    # calculate PCA
    pca = PCA(n_components=2) # reduce data down to 2 dims
    pca.fit(clustering_features_df_list.values)
    X_pca = pca.transform(clustering_features_df_list.values)
    # plot
    plt.figure(figsize=size_fig)
    plt.title(f"{graph_title} Clustering Visualized with pca")
    colors = [label_color_map[label] for label in y_labels]
    plt.scatter(X_pca[:,0], X_pca[:,1], c=colors, alpha=0)
    for i in range(X_pca.shape[0]): # loops over every point
        plt.text(X_pca[i,0], X_pca[i,1], str(i), c=label_color_map[y_labels[i]], fontsize=8)

    # special cases per algorithm used
    if graph_title.lower() == "kmeans" and kmeans_centroids.any():
        centroids_pca = pca.transform(kmeans_centroids)
        plt.scatter(centroids_pca[:,0], centroids_pca[:,1], c="Red", marker="^", s=180)
    if graph_title.lower() == "dbscan":
        plt.scatter([], [], c=label_color_map[max(y_labels)], label='Outliers')
        plt.legend()

    # plot
    # plt.savefig(f"figures/{graph_title.lower()}/PCA", bbox_inches='tight')
    plt.show()
    plt.close() # clear figure 

# creates one plot where all curves, colored by their respective cluster, are plotted
def plot_clusters_together(y_labels: List[int], after_mask_indicies: List[int], depth_resist_curve_df_list, clustering_method: str = ""):
    a = 0.3
    combined_columns = pd.concat(depth_resist_curve_df_list, axis=0, ignore_index=True)
    plt.figure(figsize=size_fig)
    for i, y in enumerate(y_labels):
        df = depth_resist_curve_df_list[after_mask_indicies[i]]
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

def find_plot_dimensions(n):
    for i in range(int(math.sqrt(n)), 0, -1):
        if n % i == 0:
            # prime
            if i == 1 or n % i == 1: return find_plot_dimensions(n+1)
            else: return i, n // i

def plot_clusters_seperately(y_labels: List[int], after_mask_indicies: List[int], depth_resist_curve_df_list, clustering_method: str = "", cluster_category_names=[], filenames=False):
    all_depth_resistance_data = pd.concat(depth_resist_curve_df_list, axis=0, ignore_index=True)
    gloabl_max_depth = all_depth_resistance_data['depth'].max()
    gloabl_max_resistance = all_depth_resistance_data['resistance'].max()

    opacity = 0.5
    labels_mapped_frequency = Counter(y_labels)
    x, y = find_plot_dimensions(len(labels_mapped_frequency))
    fig, axs = plt.subplots(x,y,figsize=(10,8))
    fig.suptitle('Cluster Depth vs Resistance')
    # for each cluster_i
    for i, ax in enumerate(axs.flatten()):
        ax.set_xlim([0,gloabl_max_depth])
        ax.set_ylim([0,gloabl_max_resistance])
        ax.set_xlabel('Depth (m)', fontsize=8)
        ax.set_ylabel('Resistance (N)', fontsize=8)

        cluster_color = label_color_map.get(i, 'black')
        if cluster_category_names: ax.set_title(f'{cluster_category_names[i].title()} Cluster', fontsize=8)
        else: ax.set_title(f'{cluster_color.title()} Cluster', fontsize=8)

        # for each curve in cluster_i
        for j in range(len(y_labels)):
            if i != y_labels[j]:
                continue
            dep_res_curve = depth_resist_curve_df_list[after_mask_indicies[j]]
            ax.plot(dep_res_curve['depth'], dep_res_curve['resistance'], color=cluster_color, alpha=opacity)
    plt.tight_layout()
    plt.show()
    plt.close()

# size of figures produced
size_fig = (4,3)
def pca_analysis(clustering_features_df_list):
    pca = PCA(n_components=len(clustering_features_df_list.columns))
    pca.fit(clustering_features_df_list.values)

    # plot scree plot
    plt.figure(figsize=size_fig)
    plt.title("Scree Plot")
    plt.xlabel("PC Number")
    plt.ylabel("Eigenvalue")
    plt.xticks(range(1, pca.n_components_+1))
    plt.plot(range(1, pca.n_components_+1), pca.explained_variance_)
    plt.show()

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
    loadings_df = pd.DataFrame(loadings, index=clustering_features_df_list.columns, columns=pc_labels)
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

def find_plot_dimensions(n):
    for i in range(int(math.sqrt(n)), 0, -1):
        if n % i == 0:
            # prime
            if i == 1 or n % i == 1: return find_plot_dimensions(n+1)
            else: return i, n // i

def plot_transect_subplots(depth_resist_curve_df_list, transect_dict, filename_to_depth_resist):
    for transect, samples in transect_dict.items():
        masked_indicies = samples.index.tolist()
        # for transect in unique_transects:
        combined_columns = pd.concat(depth_resist_curve_df_list, axis=0, ignore_index=True)
        x, y = find_plot_dimensions(len(samples))
        fig, axs = plt.subplots(x,y,figsize=(10,6))
        fig.suptitle(f"Transect: {transect.title()}")
        for i, ax in enumerate(axs.flatten()):
            ax.set_xlim([0, combined_columns["depth"].max()])
            ax.set_ylim([0, combined_columns["resistance"].max()])
            curve_features = samples.loc[masked_indicies[i]]
            sample_point = re.search(r'P_\d+', curve_features['filenames'])
            ax.set_title(f'{sample_point.group()}: {curve_features['distances']} ft.')
            # ax.set_title(curve_features['filenames'], fontsize=10)
            filename = curve_features['filenames']
            curve = filename_to_depth_resist[filename]
            ax.plot(curve['depth'], curve['resistance'], color=label_color_map[curve_features['liams_ylabels']])
        plt.tight_layout()
        plt.show()