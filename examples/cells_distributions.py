# This script shows how to load data exported from QuPath, compute metrics and display
# them, according to the configuration file. This is meant for a single-animal.
#
# There are some conventions that need to be met in the QuPath project so that the
# measurements are usable with `cuisto`:
# + Objects' classifications must be derived, eg. be in the form "something: else". The
#   primary classification ("something") will be refered to "object_type" and the
#   secondary classification ("else") to "channel" in the configuration file.
# + Only one "object_type" can be processed at once, but supports any numbers of
#   channels.
# + Annotations (brain regions) must have properly formatted measurements. For punctual
#   objects, it would be the count. Run the "add_regions_count.groovy" script to add
#   them. The measurements names must be in the form "something: else name", for
#   instance, "something: else Count". "name" is refered to "base_measurement" in the
#   configuration file.
#
# The data was generated from QuPath with stardist cell detection followed by a pixel
# classifier "Classify" function on toy data.
#
# If you cloned the repository, this example should be ready to run.
#
# Find this script as a notebook in the documentation :
# https://teamncmc.github.io/cuisto/demo_notebooks/cells_distributions.html

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import cuisto

# Full path to your configuration file, edited according to your need beforehand
wdir = Path(__file__).parent.parent / "resources"
config_file = wdir / "demo_config_cells.toml"

# - Files
# animal identifier
animal = "animalid0"
# set the full path to the annotations tsv file from QuPath
annotations_file = wdir / "cells_measurements_annotations.tsv"
# set the full path to the detections tsv file from QuPath
detections_file = wdir / "cells_measurements_detections.tsv"

# get configuration
cfg = cuisto.config.Config(config_file)
# update configuration file paths (so that this example can self-run)
cfg.files["blacklist"] = wdir / "demo_atlas_blacklist_brain.toml"
cfg.files["fusion"] = wdir / "demo_atlas_fusion_brain.toml"
cfg.files["infos"] = wdir / "demo_info_cells.toml"
cfg.get_blacklist()

# read data
df_annotations = pd.read_csv(annotations_file, index_col="Object ID", sep="\t")
df_detections = pd.read_csv(detections_file, index_col="Object ID", sep="\t")

# remove annotations that are not brain regions
df_annotations = df_annotations[df_annotations["Classification"] != "Region*"]
df_annotations = df_annotations[df_annotations["ROI"] != "Rectangle"]

# convert atlas coordinates from mm to microns
df_detections[["Atlas_X", "Atlas_Y", "Atlas_Z"]] = df_detections[
    ["Atlas_X", "Atlas_Y", "Atlas_Z"]
].multiply(1000)

# have a look
print(df_annotations.head())
print(df_detections.head())

# get distributions per regions, spatial distributions and coordinates
df_regions, dfs_distributions, df_coordinates = cuisto.process.process_animal(
    animal, df_annotations, df_detections, cfg, compute_distributions=True
)

# have a look
print(df_regions.head())
print(df_coordinates.head())

# plot distributions per regions
figs_regions = cuisto.display.plot_regions(df_regions, cfg)
# specify which regions to plot
# figs_regions = cuisto.display.plot_regions(df_regions, cfg, names_list=["GRN", "IRN", "MDRNv"])

# save as svg
# figs_regions[0].savefig(r"C:\Users\glegoc\Downloads\regions_count.svg")
# figs_regions[1].savefig(r"C:\Users\glegoc\Downloads\regions_density.svg")

# plot 1D distributions
fig_distrib = cuisto.display.plot_1D_distributions(
    dfs_distributions, cfg, df_coordinates=df_coordinates
)
# If there were several `animal` in the measurement file, it would be displayed as
# mean +/- sem instead.

# plot heatmap (all types of cells pooled)
fig_heatmap = cuisto.display.plot_2D_distributions(df_coordinates, cfg)

plt.show()
