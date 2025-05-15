"""atlas module, part of cuisto.

Contains functions to generate atlas outlines in sagittal, cornal and horizontal views,
with each regions of the Allen Brain Atlas in a single HDF5 file.

"""

import os

import h5py
import numpy as np
from brainglobe_atlasapi import BrainGlobeAtlas
from skimage import measure
from tqdm import tqdm


def get_structure_contour(mask: np.ndarray, axis: int = 2) -> list:
    """
    Get structure contour.

    Parameters
    ----------
    mask : np.ndarray
        3D mask of structure.
    axis : int, optional
        Axis, determines the projection. 2 is sagittal. Default is 2.

    Returns
    -------
    contour : list
        List of 2D array with contours (in pixels).

    """
    return measure.find_contours(np.max(mask, axis=axis))


def outlines_to_group(
    grp, acronym: str, outlines: list, resolution: tuple = (10, 10), fliplr=False
):
    """
    Write arrays to hdf5 group.

    Parameters
    ----------
    grp : h5py group
        Group in hdf5 file
    acronym : str
        Subgroup name
    outlines : list
        List of 2D ndarrays
    resolution : tuple, optional
        Resolution (row, columns) in the 2D projection, before flipping. Default is
        (10, 10).
    fliplr : bool, Defaults to False

    """
    grp_structure = grp.create_group(acronym)
    c = 0
    for outline in outlines:
        outline *= resolution
        if fliplr:
            outline = np.fliplr(outline)
        grp_structure.create_dataset(f"{c}", data=outline)
        c += 1


def generate_outlines(atlas_name: str, output_file: str | None = None):
    """
    Generate brain regions contours outlines from Brainglobe atlases masks.

    Parameters
    ----------
    atlas_name : str
        Name of Brainglobe atlas.
    output_file : str, optional
        Destination file. If it exists already, nothing is done. If None, the file is
        created at $HOME/.cuisto/{atlas_name}.h5.

    """
    if not output_file:
        output_file = get_default_filename(atlas_name)

    if os.path.isfile(output_file):
        print(f"{output_file} already exists, outlines will not be re-generated.")
        return

    atlas = BrainGlobeAtlas(atlas_name)

    with h5py.File(output_file, "w") as f:
        # create groups
        grp_sagittal = f.create_group("sagittal")
        grp_coronal = f.create_group("coronal")
        grp_top = f.create_group("top")

        # loop through structures
        pbar = tqdm(atlas.structures_list)
        for structure in pbar:
            pbar.set_description(structure["acronym"])

            mask = atlas.get_structure_mask(structure["id"])

            # sagittal
            outlines = get_structure_contour(mask, axis=2)
            res = atlas.resolution[1], atlas.resolution[0]  # d-v, r-c
            outlines_to_group(
                grp_sagittal, structure["acronym"], outlines, resolution=res
            )

            # coronal
            outlines = get_structure_contour(mask, axis=0)
            res = atlas.resolution[1], atlas.resolution[2]  # d-v, l-r
            outlines_to_group(
                grp_coronal, structure["acronym"], outlines, resolution=res, fliplr=True
            )

            # top
            outlines = get_structure_contour(mask, axis=1)
            res = atlas.resolution[2], atlas.resolution[0]  # l-r, a-p
            outlines_to_group(grp_top, structure["acronym"], outlines, resolution=res)


def check_outlines_file(filename: str, atlas_name: str) -> bool:
    """
    Check if the outline file exists, if not, it will be generated if `generate` is
    True.

    Parameters
    ----------
    filename : str
        Full path to the file to check.

    Returns
    -------
    file_not_found : bool
        True if the file does not exist.

    """
    if not os.path.isfile(filename):
        # file does not exist, check the default one
        filename = get_default_filename(atlas_name)
        if not os.path.isfile(filename):
            file_not_found = True
        else:
            msg = (
                f"The outlines file was not found but exists at {filename}.\n"
                "Set this path in the [files] section of the configuration file."
            )
            print(msg)
            file_not_found = True
    else:
        file_not_found = False

    return file_not_found


def get_default_filename(atlas_name: str) -> str:
    """
    Get the file name $HOME/.cuisto/{atlas_name}.h5

    Parameters
    ----------
    atlas_name : str
        Name of a Brainglobe atlas.

    Returns
    -------
    filename : str
        Path to the default file location.

    """
    from pathlib import Path

    local_dir = Path.home() / ".cuisto"
    if not local_dir.exists():
        print(f"[Info] Outline file not specified, creating the {local_dir} directory.")
        local_dir.mkdir()
    return str(local_dir / (atlas_name + "_outlines.h5"))
