"""
@author: Johanna Rahm
Research group of Mike Heilemann
Institute of Physical and Theoretical Chemistry, Goethe University Frankfurt a.M.

Quantify number of clusters in binary mask areas.
The information is stored as csv file.

The required folder structure contains one dbcluster and one to multiple mask files.
The analysis is applied to each directory and to each mask file.

directory1:
    - <cluster file>.hdf5 # one hdf5 dbcluster file
    - <mask1>.tif # mask file with extension tif/png/jpg
    - <mask2>.tif # mask file with extension tif/png/jpg
    - ...
directory2:
    - <cluster file>.hdf5 # one hdf5 dbcluster file
    - <mask1>.tif # mask file with extension tif/png/jpg
    - ...
"""

import csv
import h5py
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
from typing import List
from PIL import Image


# directories containing binary mask images and dbcluster.hdf5 file
DIR_PATHS = [r"D:\_data\SideProjects_Scripts\Frangakis_kidney\analysis\final_files_multimasks\Grid6_Pos2",
r"D:\_data\SideProjects_Scripts\Frangakis_kidney\analysis\final_files_multimasks\Grid7_Pos2",
r"D:\_data\SideProjects_Scripts\Frangakis_kidney\analysis\final_files_multimasks\Grid8_Pos3",
r"D:\_data\SideProjects_Scripts\Frangakis_kidney\analysis\final_files_multimasks\Grid8_Pos4"]

# define px size of measurement in nm
PX_SIZE_MEASUREMENT = 108
# define px size in cluster image in nm
PX_SIZE_CLUSTERS = 10
# enable or disable displayment of plots
SHOW_PLOTS = False


def get_xy_locs(h5_path: Path) -> np.ndarray:
    """
    Get xy coordinates of clusters.
    :param h5_path: Path to hdf5 Picasso cluster file.
    :return: xy-coordinates of clusters.
    """
    h5_file = h5py.File(h5_path, "r")
    # read xy-coordiates as numpy array with shape (n_clusters, 2)
    # the coordinates are in px and are transferred to match the mask image
    xy_stack = np.column_stack((h5_file["clusters"]["com_x"] * PX_SIZE_MEASUREMENT / PX_SIZE_CLUSTERS, h5_file["clusters"]["com_y"] * PX_SIZE_MEASUREMENT / PX_SIZE_CLUSTERS))
    return xy_stack


def get_mask(mask_path: Path, dir_path: Path, mask_name: str) -> np.ndarray:
    """
    Read mask image as numpy.array.
    :param mask_path: Path to mask image.
    :param dir_path: Path to working directory.
    :param mask_name: File name of mask.
    :return: Mask as numpy array.
    """
    img = Image.open(mask_path).convert("L")
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    img = img.rotate(90)
    # img.save(dir_path[:-13] + "\\" + mask_name + "_rotated_flipped.png")
    mask = np.array(img)
    return mask


def get_cluster_count(mask: np.ndarray, clusters_xy: np.ndarray) -> (int, List):
    """
    Count the number of clusters within mask.
    :param mask: Binary mask.
    :param clusters_xy: Cluster xy-coordinates of shape (n_clusters, 2).
    :return: Number of clusters and their localizations within mask.
    """
    count = 0  # number of clusters within mask
    locs_mask = []  # localizations of clusters within mask
    for xy in clusters_xy:
        x, y = int(np.round(xy[0])), int(np.round(xy[1]))
        if mask[x][y] != 0:
            count += 1
            locs_mask.append([x, y])
    return count, locs_mask


def get_mask_area(mask: np.ndarray) -> (float, float):
    """
    Calculate the area of the mask.
    :param mask: Binary mask.
    :return: Mask area in px² and µm².
    """
    # set all values != 0 to 1
    mask = np.where(mask > 0, 1, mask)
    # area in px²
    area_px = np.sum(mask)
    # area in µm²
    area_um = area_px * (PX_SIZE_CLUSTERS/1000)**2
    return area_px, area_um
            
            
def save_results(mask_name: str, mask_area_px: int, mask_area_um: float, cluster_count: int, cluster_count_per_area: float, n_clusters: int, save_path: Path) -> None:
    """
    Save lists as columns in a csv file.
    :param mask_name: Name of mask file.
    :param mask_area_px: Area of the mask in px².
    :param mask_area_um: Area of the mask in um².
    :param cluster_count: Number of clusters in mask.
    :param cluster_count_per_area: Number of clusters in mask per mask area um².
    :param n_clusters: Total number of clusters on FOV.
    :param save_path: Path to store csv file.
    """
    with open(save_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "mask area / px\u00B2", "mask area / \u00B5m\u00B2", "number of clusters in mask", "number of clusters in mask / mask area", "total number of clusters"])
        writer.writerow([mask_name, mask_area_px, mask_area_um, cluster_count, cluster_count_per_area, n_clusters])


def helper_plot_coordinates_mask(mask, locs_mask, mask_name, dir_path):
    # plot coordinates that are on mask in red and mask area in white
    plt.imshow(mask, cmap="gray")
    x_coords, y_coords = zip(*locs_mask)
    plt.scatter(y_coords, x_coords, color="red", marker=".", s=3)
    plt.title(mask_name)
    plt.savefig(os.path.join(dir_path[:-13], mask_name + "_mask_locs.png"), bbox_inches="tight", pad_inches=0,
                transparent=True)
    if SHOW_PLOTS:
        plt.show()


def helper_plot_coordinates_FOV(clusters_xy, dir_path, mask_name):
    # plot all localizations on FOV in blue
    shape = 5530
    fig = plt.figure(figsize=(shape / 1000, shape / 1000), dpi=100)
    plt.imshow(np.zeros((shape, shape)), cmap="gray")
    x_coords, y_coords = zip(*clusters_xy)
    plt.scatter(y_coords, x_coords, color="blue", marker=".", s=5)
    plt.xlim([0, shape])
    plt.ylim([0, shape])
    plt.axis("off")
    plt.savefig(os.path.join(dir_path[:-13], mask_name + "_FOV_locs.png"), bbox_inches="tight", pad_inches=0,
                transparent=True)
    if SHOW_PLOTS:
        plt.show()


def helper_plot_mask(mask, mask_name, dir_path):
    # plot the mask area in white
    shape = np.shape(mask)[0]
    fig = plt.figure(figsize=(shape / 1000, shape / 1000), dpi=100)
    plt.imshow(mask, cmap="gray")
    plt.savefig(os.path.join(dir_path[:-13], mask_name + "_mask.png"), bbox_inches="tight", pad_inches=0,
                transparent=True)
    if SHOW_PLOTS:
        plt.show()


def visualize_cluster_centers_mask(clusters_xy: List, locs_mask: List, mask: np.ndarray, mask_name: str, dir_path: Path):
    """
    Plot the mask area in white with coordinates within mask in red and coordinates outside mask in blue.
    :param clusters_xy: Localizations outside mask.
    :param locs_mask: Localizations inside mask.
    :param mask: Mask numpy array.
    :param mask_name: File name of mask.
    :param dir_path: Path to save plot.
    """
    shape = np.shape(mask)[0]
    fig = plt.figure(figsize=(shape / 1000, shape / 1000), dpi=100)
    plt.xlim([0, shape])
    plt.ylim([0, shape])
    # plot locs outside mask
    x_coords, y_coords = zip(*clusters_xy)
    plt.scatter(y_coords, x_coords, color="blue", marker=".", s=5)
    # plot locs inside mask
    if locs_mask:
        x_coords, y_coords = zip(*locs_mask)
        plt.scatter(y_coords, x_coords, color="red", marker=".", s=5)
    # plot mask
    plt.imshow(mask, cmap="gray")
    plt.savefig(os.path.join(dir_path, mask_name + "_FOV_mask_locs.png"), bbox_inches="tight", pad_inches=0,
                transparent=True)
    if SHOW_PLOTS:
        plt.show()


def run_quantify_clusters(dir_path):
    # get cluster file path (=hdf5 file)
    cluster_path = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if file.endswith(".hdf5")][0]
    # get masks file paths (=all image files in directory)
    masks_paths = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if file.endswith((".tif", ".png", ".jpg")) and "_FOV_mask_locs" not in file]

    # get cluster xy coordinates
    clusters_xy = get_xy_locs(cluster_path)
    # get total number of clusters
    n_clusters = len(clusters_xy)

    for mask_path in masks_paths:
        # file name of mask
        mask_name = os.path.splitext(os.path.basename(mask_path))[0]
        # get mask images as numpy arrays
        mask = get_mask(mask_path, dir_path, mask_name)
        # get mask areas
        mask_area_px, mask_area_um = get_mask_area(mask)
        # count number of clusters in mask
        cluster_count, locs_mask = get_cluster_count(mask, clusters_xy)
        # calc number of clusters in mask per mask area
        cluster_count_per_area = cluster_count / mask_area_um

        # # coordinates that are on mask in red and mask area
        # helper_plot_coordinates_mask(mask, locs_mask, mask_name, dir_path)
        # # coordinates on entire FOV in blue
        # helper_plot_coordinates_FOV(clusters_xy, dir_path, mask_name)
        # # show only mask
        # helper_plot_mask(mask, mask_name, dir_path)
        # visualize localizations inside mask = red, outside mask = blue, and mask area
        visualize_cluster_centers_mask(clusters_xy, locs_mask, mask, mask_name, dir_path)

        # save results as csv
        save_results(mask_name, mask_area_px, mask_area_um, cluster_count, cluster_count_per_area, n_clusters, os.path.splitext(cluster_path)[0] + mask_name + ".csv")


def main():
    # quantify the number of clusters per mask area
    for dir_path in DIR_PATHS:
        run_quantify_clusters(dir_path)


if __name__ == "__main__":
    main()
