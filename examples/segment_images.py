"""
Example to show how to configure and use the `segmentation` module of the `cuisto`
package.

For fiber-like objects, binarize and skeletonize the image, then use `skan` to extract
branches coordinates.
For polygon-like objects, binarize the image and detect objects and extract contours
coordinates.
For points, treat that as polygons then extract the centroids instead of contours.
Finally, export the coordinates as collections in geojson files, importable in QuPath.
Supports any number of channel of interest within the same image.
One output file per iamge, per channel will be created.

This script uses `cuisto.segmentation`. It is designed to work on probability maps
generated from a pixel classifier in QuPath, but *might* work on raw images.

Usage : fill-in the Parameters section of the script and run it. Explanation is given as
a docstring below each parameter.

Masks can be used to exclude objects detected too close to the edges, you can disable
that by setting the EDGE_DIST parameter to 0 (then you can just ignore the masks-related
parameters).

A "geojson" folder will be created in the parent directory of `IMAGES_DIR`.
To exclude objects near the edges of an ROI, specify the path to masks stored as images
with the same names as probabilities images (without their suffix).

The first block downloads toy data to showcase usage. You can drag & drop the prediction
map into QuPath, run this script and drag & drop the resulting geojson files to see the
results. Remove that block to use with your own data.

"""

import requests
from tqdm import tqdm

from cuisto import segmentation

### Configure the example to fetch data online. See after this block for the actual
# segmentation option

# --- Set up the example
# Configure so that toy data is fetched online. You can safely remove this
# part when running on your own data
dl_example = True
example_url = "https://github.com/TeamNCMC/cuisto/raw/main/resources/example-seg.tar.gz"

# Download example data into cuisto default folder. Remove this block if using your data
if dl_example:
    import tarfile
    import sys
    from pathlib import Path

    default_destination = Path.home() / ".cuisto"
    print(f"Downloading example data to {default_destination}...")
    if not default_destination.exists():
        default_destination.mkdir()

    response = requests.get(example_url)
    if response.ok:
        tarname = default_destination / "example-seg.tar.gz"
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
### Remove the block above to run on your own data

# --- Parameters
IMAGES_DIR = default_destination / "example-seg" / "probabilities"
"""Full path to the images to segment."""
MASKS_DIR = "path/to/corresponding/masks"
"""Full path to the masks, to exclude objects near the brain edges (set to None or empty
string to disable this feature)."""
MASKS_EXT = "tiff"
"""Masks files extension."""
SEGTYPE = "fibers"
"""Type of segmentation, must match one the hardcoded keywords to associate it to
'fibers', 'points' or polygon'. See `cuisto.segmentation` doc."""
IMG_SUFFIX = "_Probabilities.tiff"
"""Images suffix, including extension. Masks must be the same name without the suffix."""
ORIGINAL_PIXELSIZE = 0.5476 * 2
"""Original images pixel size in microns. This is in case the pixel classifier uses
a lower resolution, yielding smaller probability maps, so output objects coordinates
need to be rescaled to the full size images. The pixel size is written in the "Image"
tab in QuPath."""

CHANNELS_PARAMS = [
    {
        "name": "cy5",
        "target_channel": 0,
        "proba_threshold": 0.6,
        "qp_class": "Fibers: marker1",
        "qp_color": [164, 250, 120],
    },
    {
        "name": "dsred",
        "target_channel": 1,
        "proba_threshold": 0.6,
        "qp_class": "Fibers: marker2",
        "qp_color": [224, 153, 18],
    },
    {
        "name": "egfp",
        "target_channel": 2,
        "proba_threshold": 0.6,
        "qp_class": "Fibers: marker3",
        "qp_color": [135, 11, 191],
    },
]
"""This should be a list of dictionary (one per channel) with keys :

- name: str, used as suffix for output geojson files, not used if only one channel
- target_channel: int, index of the segmented channel of the image, 0-based
- proba_threshold: float < 1, probability cut-off for that channel
- qp_class: str, name of QuPath classification
- qp_color: list of RGB values, associated color"""

EDGE_DIST = 0
"""Distance to brain edge to ignore, in µm. 0 to disable."""

FILTERS = {
    "length_low": 1.5,  # minimal length in microns - for lines
    "area_low": 10,  # minimal area in µm² - for polygons and points
    "area_high": 1000,  # maximal area in µm² - for polygons and points
    "ecc_low": 0.0,  # minimal eccentricity - for polygons  and points (0 = circle)
    "ecc_high": 0.9,  # maximal eccentricity - for polygons and points (1 = line)
    "dist_thresh": 30,  # maximal inter-point distance in µm - for points
}
"""Dictionary with keys :

- length_low: minimal length in microns - for lines
- area_low: minimal area in µm² - for polygons and points
- area_high: maximal area in µm² - for polygons and points
- ecc_low: minimal eccentricity - for polygons  and points (0 = circle)
- ecc_high: maximal eccentricity - for polygons and points (1 = line)
- dist_thresh: maximal inter-point distance in µm - for points
"""

QUPATH_TYPE = "detection"
""" QuPath object type: 'annotation' or 'detection'"""
MAX_PIX_VALUE = 255
"""Maximum pixel possible value to adjust `proba_threshold`."""


# --- Call
if __name__ == "__main__":
    # check parameters is a list
    if not isinstance(CHANNELS_PARAMS, (list, tuple)):
        channels_params = [CHANNELS_PARAMS]
    else:
        channels_params = CHANNELS_PARAMS

    # format suffix (append underscore or leave empty)
    if len(channels_params) == 1:

        def make_suffix(s):
            return ""
    elif len(channels_params) > 1:

        def make_suffix(s):
            return "_" + s
    else:
        raise ValueError("'CHANNELS_PARAMS' can't be empty.")

    pbar = tqdm(channels_params)
    for param in pbar:
        pbar.set_description(f"Segmenting {param['name']}")
        segmentation.process_directory(
            IMAGES_DIR,
            img_suffix=IMG_SUFFIX,
            segtype=SEGTYPE,
            original_pixelsize=ORIGINAL_PIXELSIZE,
            target_channel=param["target_channel"],
            proba_threshold=param["proba_threshold"],
            max_pixel_value=MAX_PIX_VALUE,
            qupath_class=param["qp_class"],
            qupath_color=param["qp_color"],
            qupath_type=QUPATH_TYPE,
            channel_suffix=make_suffix(param["name"]),
            edge_dist=EDGE_DIST,
            filters=FILTERS.copy(),
            masks_dir=MASKS_DIR,
            masks_ext=MASKS_EXT,
        )
