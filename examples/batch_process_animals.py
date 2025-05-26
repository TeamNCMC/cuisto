"""
This example shows how to collect data from single animal when they were exported
individually from QuPath, resulting in a single file per animal, containing data from
all the images in each project. Thus, there should be, for each animal, a file
corresponding to Annotations (brain regions) and Detections (objects of interest).

We assume all the pairs of files are located in the same directory, and their file name
is in the form : animalid_annotations.tsv and animalid_detections.tsv.

For fibers, a json file is required to store the coordinates of all the points making
a single fiber. Those would be generated with the exportFibersAtlasCoordinates.groovy
script. We assume all json files corresponding to one animal is stored in a
"animalid_detections" folder.

"""

# import required packages
import os
import tarfile
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
from tqdm import tqdm

import cuisto

# --- Parameters
# Configure to get the example online
dl_example = True
animals = ("animalid0", "animalid1")
example_url = "https://github.com/TeamNCMC/cuisto/raw/main/resources/example.tar.gz"

# Configure with your own data
# full path to where are the TSV files and {animal}_detections folders
# dl_example = False
# animals = ("animalid0", "animalid1")
# input_dir = "~/.cuisto/example"
# config_file = "~/.cuisto/config_multi.toml"

# Download example data into cuisto default folder. Remove this block if using your data
if dl_example:
    default_destination = Path.home() / ".cuisto"
    print(f"Downloading example data to {default_destination}...")
    if not default_destination.exists():
        default_destination.mkdir()

    response = requests.get(example_url)
    if response.ok:
        tarname = default_destination / "example.tar.gz"
        with open(tarname, "wb") as fid:
            fid.write(response.content)
        with tarfile.open(tarname) as tar:
            tar.extractall(tarname.parent, filter="data")

    else:
        msg = (
            "Download failed. Download manually here : "
            "https://github.com/TeamNCMC/cuisto/tree/main/resources"
        )
        print(msg)
        sys.exit()

    # set paths
    input_dir = default_destination / "example"
    config_file = input_dir / "config_multi.toml"
    # we need to overwrite the paths to the other configuration files
    with open(config_file, "r") as fid:
        data_config = fid.readlines()
    data_config[-4] = (
        "blacklist = '" + str(input_dir / "demo_atlas_blacklist_brain.toml") + "'\n"
    )
    data_config[-3] = (
        "fusion = '" + str(input_dir / "demo_atlas_fusion_brain.toml") + "'\n"
    )
    with open(config_file, "w") as fid:
        fid.writelines(data_config)


# --- Preparation

# load configuration
cfg = cuisto.Config(config_file)

# initialize lists
df_regions = []
dfs_distributions = []
df_coordinates = []

# --- Processing
pbar = tqdm(animals)

for animal in pbar:
    pbar.set_description(f"Processing {animal}")

    # read annotation for this animal
    df_annotations = pd.read_csv(
        os.path.join(input_dir, f"{animal}_annotations.tsv"),
        index_col="Object ID",
        sep="\t",
    )

    # read detections only to plot spatial distributions, otherwise set
    # df_detections = pd.DataFrame()
    # uncomment out for cells
    # df_detections = pd.read_csv(
    #     os.path.join(input_dir, f"{animal}_detections.tsv"),
    #     index_col="Object ID",
    #     sep="\t",
    # )
    
    # comment out for non-fibers
    df_detections = cuisto.io.cat_json_dir(
        os.path.join(input_dir, f"{animal}_detections"),
        hemisphere_names=cfg.hemispheres["names"],  # we need it now for performance
        atlas=cfg.bg_atlas,
    )

    # get results
    df_reg, dfs_dis, df_coo = cuisto.process.process_animal(
        animal,
        df_annotations,
        df_detections,
        cfg,
        compute_distributions=True,  # set to False if df_detections is empty
    )

    # collect results
    df_regions.append(df_reg)
    dfs_distributions.append(dfs_dis)
    df_coordinates.append(df_coo)

# concatenate all results
df_regions = pd.concat(df_regions, ignore_index=True)
dfs_distributions = [
    pd.concat(dfs_list, ignore_index=True) for dfs_list in zip(*dfs_distributions)
]
df_coordinates = pd.concat(df_coordinates, ignore_index=True)

# plot as usual -- animals will be pooled and the mean +/- sem will be shown
cuisto.display.plot_regions(df_regions, cfg)
cuisto.display.plot_1D_distributions(
    dfs_distributions, cfg, df_coordinates=df_coordinates
)
cuisto.display.plot_2D_distributions(df_coordinates, cfg)

plt.show()
