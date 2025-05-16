"""atlas module, part of cuisto.

Contains functions to generate atlas outlines in sagittal, cornal and horizontal views,
with each regions of the Allen Brain Atlas in a single HDF5 file.

"""

import os

import h5py
import numpy as np
import requests
from brainglobe_atlasapi import BrainGlobeAtlas
from skimage import measure
from tqdm import tqdm

AVAILABLE_ATLAS = ["allen_mouse_10um", "allen_cord_20um"]
URL_BASE = "https://github.com/TeamNCMC/brain-structures/raw/main/"


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
    Check if the outline file exists, if not, attempt to download it.

    Parameters
    ----------
    filename : str
        Full path to the file to check.
    atlas_name : str
        Brainglobe atlas name.

    Returns
    -------
    file_not_found : bool
        True if the file does not exist and could not be downloaded.

    """
    if not filename:
        # empty file name, check the default one
        filename = get_default_filename(atlas_name)
    
    if not os.path.isfile(filename):
        print("The outlines file does not exist, attempting to download it...")
        result = download_outline(filename, atlas_name)
        if result:
            # :)
            print(f"Outlines file downloaded at {filename}.")
            file_not_found = False
        else:
            # we already said it was not downloaded (not available or request failed)
            file_not_found = True
    else:
        # file exists
        file_not_found = False

    return file_not_found, filename


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


def download_outline(filename: str, atlas_name: str) -> bool:
    """
    Download outline file if available.

    Parameters
    ----------
    filename : str
        Full path to the destination file.
    atlas_name : str
        Brainglobe atlas name.

    Returns
    -------
    result : bool
        True if the file was downloaded, False otherwise.

    """
    # check the outlines is available
    if atlas_name not in AVAILABLE_ATLAS:
        print(
            f"Unfortunately, the structures outlines for {atlas_name} was not"
            " pre-generated."
        )
        return False

    # check filename
    if not filename:
        # empty filename, set the default one
        filename = get_default_filename(atlas_name)

    # build URL
    url = URL_BASE + atlas_name + "_outlines.h5"
    result = download_file(url, filename)

    return result


def download_file(url: str, filename: str) -> bool:
    """
    Download a file.

    Parameters
    ----------
    url : str
        Full URL to address the HTTP request.
    filename : str
        Path to the destination file.

    Returns
    -------
    tf : bool
        True if the file was downloaded, False otherwise.

    """

    response = requests.get(url)
    if response.ok:
        with open(filename, "wb") as fid:
            fid.write(response.content)
        return True
    else:
        print("The outlines file could not be downloaded.")
        return False
