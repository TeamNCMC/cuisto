"""
Use pyramid_creator from a Python script.

"""

import multiprocessing

from pyramid_creator import pyramidalize_directory

images_dir = "/path/to/your/images"

# --- Parameters
# Tile size (usually 512 or 1024)
TILE_SIZE = 512
# Factor between two consecutive pyramid levels
PYRAMID_FACTOR = 2
# Number of threads for parallelization
NTHREADS = int(multiprocessing.cpu_count() / 2)

# --- QuPath backend parameters
# Use QuPath and the external groovy script instead of pure python (more reliable)
USE_QUPATH = True
# Full path to the QuPath (console) executable. If empty, it will look for it in a
# QUPATH_PATH file in the user home directory.
QUPATH_PATH = ""

# --- Python backend parameters
# Maximum rescaling (smallest pyramid)
PYRAMID_MAX: int = 32

# -- Call
pyramidalize_directory(
    images_dir,
    use_qupath=USE_QUPATH,
    tile_size=TILE_SIZE,
    pyramid_factor=PYRAMID_FACTOR,
    nthreads=NTHREADS,
    qupath_path=QUPATH_PATH,
    pyramid_max=PYRAMID_MAX,
)
