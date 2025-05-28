# # Fibers length in multi animals
# This example uses synthetic data to showcase how `cuisto` can be used in a pipeline.
#
# Annotations measurements should be exported from QuPath, following the required
# directory structure.
#
# Alternatively, you can merge all your CSV files yourself, one per animal, adding an
# animal ID to each table. Those can be processed with the
# `cuisto.process.process_animal()` function, in a loop, collecting the results at each
# iteration and finally concatenating the results. Finally, those can be used with
# `display` module.
#
# If you cloned the repository, this example should be ready to run.
#
# Find this script as a notebook in the documentation :
# https://teamncmc.github.io/cuisto/demo_notebooks/fibers_length_multi.html

from pathlib import Path

import matplotlib.pyplot as plt

import cuisto

# Full path to your configuration file, edited according to your need beforehand
wdir = Path(__file__).parent.parent / "resources"
config_file = wdir / "demo_config_multi.toml"

# Files
datadir = wdir / "multi"
animals = ["mouse0", "mouse1"]

# get configuration
cfg = cuisto.Config(config_file)
# update configuration file paths (so that this example can self-run)
cfg.files["blacklist"] = wdir / "demo_atlas_blacklist_brain.toml"
cfg.files["fusion"] = wdir / "demo_atlas_fusion_brain.toml"
cfg.get_blacklist()

# get distributions per regions
df_regions, _, _ = cuisto.process.process_animals(
    datadir, animals, cfg, compute_distributions=False
)

# have a look
print(df_regions.head(10))

figs_regions = cuisto.display.plot_regions(df_regions, cfg)

plt.show()
