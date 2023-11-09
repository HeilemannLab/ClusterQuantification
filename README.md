# ClusterQuantification
This code quantifies the number of cluster centers within binary masks.

## Installation and execution

The required packages are numpy, matplotlib, h5py, and PIL. They can be for example installed in an Anaconda environment with
```conda install numpy matplotlib h5py pillow```

Adapt the script's parameters inside the Python file and execute the script with
```python quantify_clusters.py```

## Required file format

The cluster file containing the cluster x and y coordinates is the dbcluster.hdf5 file generated from the [Picasso](https://github.com/jungmannlab/picasso) software. The binary masks can be in tif, png, or jpg format.

## Required folder structure

directory1: <br/>
    - <cluster file>.hdf5 # one hdf5 dbcluster file <br/>
    - <mask1>.tif # mask file with extension tif/png/jpg <br/>
    - <mask2>.tif # mask file with extension tif/png/jpg <br/>
    - ... <br/>
directory2: <br/>
    - <cluster file>.hdf5 # one hdf5 dbcluster file <br/>
    - <mask1>.tif # mask file with extension tif/png/jpg <br/>
    - ... <br/>

## Parameters
Multiple directories containing binary mask images and dbcluster.hdf5 file can be defined.
```DIR_PATHS = [r"D:\path_to_dirA", r"D:\path_to_dirB"]```

The pixel size of the measurements / binary mask must be defined in nm.
```PX_SIZE_MEASUREMENT = 108```

The pixel size of the cluster image must be defined in nm.
```PX_SIZE_CLUSTERS = 10```

Wheather plots showing the clusters inside and outside the binary mask should be shown.
```SHOW_PLOTS = False```

## Output
As output the results per dbcluster file are stored in a csv file. Each row represents a mask file. Saved are information about the mask area, the number of clusters inside and outside the mask, as well as the cluster density.

## Publications
The code was used in [A. N. Birtasu, K. Wieland, U. H. Ermel, J. V. Rahm, M. P. Scheffer, B. Flottmann, M. Heilemann, F. Grahammer, A. S. Frangakis, The molecular architecture of the kidney slit diaphragm, bioRxiv, 2023](https://doi.org/10.1101/2023.10.27.564405).