"""
pyramid_creator command line interface (CLI).

"""

import math
import multiprocessing
import os
import subprocess
import sys
import uuid
import warnings
from importlib import resources
from typing import Optional

import typer
from tqdm import tqdm
from typing_extensions import Annotated

__version__ = "2024.12.18"


# --- Typer functions
def app():
    typer.run(pyramidalize_directory)


def version_callback(value: bool):
    if value:
        print(f"create-pyramids CLI version : {__version__}")
        raise typer.Exit()


# --- Utilities
def get_script_path(script_path: str | None = None) -> str:
    """
    Find groovy script packaged with pyramid_creator.

    If it is provided and exists, return as is, otherwise, fallback to the script
    provided with the package.
    """
    if script_path:
        check_file_path(script_path)
        return script_path

    with resources.path(
        "pyramid_creator.scripts", "createPyramids.groovy"
    ) as script_path:
        return str(script_path)


def find_qupath_path() -> str:
    """
    Try to find QuPath console executable in Windows AppData.

    Returns
    -------
    qupath_path : str
        Full path to the QuPath console executable if found.

    """
    # attempt to find it -- will work only in Windows as it looks for it in
    # AppData\Local
    versions = ["0.6.0", "0.5.1", "0.5.0"]
    appdata_dir = os.getenv("LOCALAPPDATA")
    for version in versions:
        qupath_path = os.path.join(
            appdata_dir, f"QuPath-{version}", f"QuPath-{version} (console).exe"
        )
        if os.path.isfile(qupath_path):
            print(f"[Info] Found at {qupath_path}!")
            save_qupath_path(qupath_path)
            return qupath_path

    # QuPath was not found
    check_file_path("")  # will raise an Error


def save_qupath_path(qupath_path: str):
    """
    Save QuPath exe path in a configuration file called "QUPATH_PATH" in user home
    directory.

    If the file exists, it will not be modified.

    Parameters
    ----------
    qupath_path : str
        Path to save in the file.

    """
    home_dir = os.path.expanduser("~")
    config_file = os.path.join(home_dir, "QUPATH_PATH")
    if not os.path.isfile(config_file):
        with open(config_file, "w") as fid:
            fid.writelines(qupath_path)
    else:
        warnings.warn(f"{config_file} already exists, it will not be modified.")


def get_qupath_path(qupath_path: str | None = None) -> str:
    """
    Get QuPath executable.

    If a non-empty string is given, returns it as is.
    Otherwise try to read the QuPath executable path in the QUPATH_PATH file in home
    directory.
    If it is still not found, try to find automatically.

    Parameters
    ----------
    qupath_path : str or None, optional
        Full path to QuPath console executable, or None to try to find it from a file
        or automatically. Default is None.

    Returns
    -------
    qupath_path : str
        Full path to QuPath console executable, if found.

    """
    if qupath_path:
        # provided, check if it exists and return
        check_file_path(qupath_path)
        return qupath_path

    # then try to read it from a configuration file
    home_dir = os.path.expanduser("~")
    config_file = os.path.join(home_dir, "QUPATH_PATH")
    if os.path.isfile(config_file):
        with open(config_file, "r") as fid:
            qupath_path = fid.readline()
            check_file_path(qupath_path)
            return qupath_path

    # then try to find and set it automatically
    qupath_path = find_qupath_path()  # if not found, it will error
    # save it in a configuration file
    save_qupath_path(qupath_path)
    return qupath_path


def check_file_path(file_path: str):
    """Checks if file_path exists."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} not found.")


# --- Processing functions
def pyramidalize_qupath(
    image_path: str,
    output_image: str,
    qupath_path: str,
    script_path: str,
    tile_size: int,
    pyramid_factor: int,
    nthreads: int,
):
    """
    Pyramidalization with QuPath backend.

    """
    # generate an uid to make sure to not overwrite original file
    uid = uuid.uuid1().hex

    # prepare image names
    imagename = os.path.basename(image_path)
    inputdir = os.path.dirname(image_path)
    new_imagename = uid + "_" + imagename
    new_imagepath = os.path.join(inputdir, new_imagename)

    # prepare arguments
    args = "[" f"{uid}," f"{tile_size}," f"{pyramid_factor}," f"{nthreads}" "]"

    # call the qupath groovy script within a shell
    subprocess.run(
        [qupath_path, "script", script_path, "-i", image_path, "--args", args],
        shell=True,
        stdout=subprocess.DEVNULL,
    )

    if not os.path.isfile(new_imagepath):
        raise FileNotFoundError(
            "QuPath did not manage to create the pyramidalized image."
        )

    # move the pyramidalized image in the output directory
    os.rename(new_imagepath, output_image)


def pyramidalize_python(
    image_path: str, output_image: str, levels: list | tuple, tiffoptions: dict
):
    """
    Pyramidalization with tifffile and scikit-image.

    Parameters
    ----------
    image_path : str
        Full path to the image.
    output_image : str
        Full path to the pyramidalized image.
    levels : list-like of int
        Pyramids levels.
    tiffoptions : dict
        Options for TiffWriter.
    """
    # specific imports
    import xml.etree.ElementTree as ET

    import numpy as np
    import tifffile
    from skimage import transform

    # Nested functions
    def get_pixelsize_ome(
        desc: str,
        namespace: dict = {"ome": "http://www.openmicroscopy.org/Schemas/OME/2016-06"},
    ) -> float:
        """
        Extract physical pixel size from OME-XML description.

        Raise a warning if pixels are anisotropic (eg. X and Y sizes are not the same).
        Raise an error if size units are not microns ("µm").

        Parameters
        ----------
        desc : str
            OME-XML string from Tiff page.
        namespace : dict, optional
            XML namespace, defaults to latest OME-XML schema (2016-06).

        Returns
        -------
        pixelsize : float
            Physical pixel size.

        """
        root = ET.fromstring(desc)

        for pixels in root.findall(".//ome:Pixels", namespace):
            pixelsize_x = float(pixels.get("PhysicalSizeX"))
            pixelsize_y = float(pixels.get("PhysicalSizeY"))
            break  # stop at first Pixels field in the XML

        # sanity checks
        if pixelsize_x != pixelsize_y:
            warnings.warn(
                f"Anisotropic pixels size found, are you sure ? ({pixelsize_x}, {pixelsize_y})"
            )

        return np.mean([pixelsize_x, pixelsize_y])

    def im_downscale(img, downfactor, **kwargs):
        """
        Downscale an image by the given factor.

        Wrapper for `skimage.transform.rescale`.

        Parameters
        ----------
        img : np.ndarray
        downfactor : int or float
            Downscaling factor.
        **kwargs : passed to skimage.transform.rescale

        Returns
        -------
        img_rs : np.ndarray
            Rescaled image.

        """
        return transform.rescale(
            img, 1 / downfactor, anti_aliasing=False, preserve_range=True, **kwargs
        )

    # get metadata from original file (without loading the whole image)
    with tifffile.TiffFile(image_path) as tifin:
        metadata = tifin.ome_metadata
        pixelsize = get_pixelsize_ome(metadata)

    with tifffile.TiffWriter(output_image, ome=False) as tifout:
        # read full image
        img = tifffile.imread(image_path)

        # write full resolution multichannel image
        tifout.write(
            img,
            subifds=len(levels),
            resolution=(1e4 / pixelsize, 1e4 / pixelsize),
            description=metadata,
            metadata=None,
            **tiffoptions,
        )

        # write downsampled images (pyramidal levels)
        for level in levels:
            img_down = im_downscale(
                img, level, order=0, channel_axis=0
            )  # downsample image
            tifout.write(
                img_down,
                subfiletype=1,
                resolution=(1e4 / level / pixelsize, 1e4 / level / pixelsize),
                **tiffoptions,
            )


def get_tiff_options(compression: str, nthreads: int, tilesize: int) -> dict:
    """
    Get the relevant tags and options to write a TIFF file.

    The returned dict is meant to be used to write a new tiff page with those tags.

    Parameters
    ----------
    compression : str
        Tiff compression (None, LZW, ...).
    nthreads : int
        Number of threads to write tiles.
    tilesize : int
        Tile size in pixels. Should be a power of 2.

    Returns
    -------
    options : dict
        Dictionary with Tiff tags.

    """
    return {
        "compression": compression,
        "photometric": "minisblack",
        "resolutionunit": "CENTIMETER",
        "maxworkers": nthreads,
        "tile": (tilesize, tilesize),
    }


def pyramidalize_directory(
    inputdir: Annotated[
        str,
        typer.Argument(help="Full path to the directory with images to pyramidalize."),
    ],
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
    use_qupath: Annotated[
        Optional[bool],
        typer.Option(help="Use QuPath backend instead of Python."),
    ] = True,
    tile_size: Annotated[
        Optional[int],
        typer.Option(help="Image tile size, typically 512 or 1024."),
    ] = 512,
    pyramid_factor: Annotated[
        Optional[int],
        typer.Option(help="Factor between two consecutive pyramid levels."),
    ] = 2,
    nthreads: Annotated[
        Optional[int],
        typer.Option(help="Number of threads to parallelize image writing."),
    ] = None,
    qupath_path: Annotated[
        Optional[str],
        typer.Option(
            help="Full path to the QuPath (console) executable.",
            rich_help_panel="QuPath backend",
        ),
    ] = "",
    script_path: Annotated[
        Optional[str],
        typer.Option(
            help="Full path to the groovy script that does the job.",
            rich_help_panel="QuPath backend",
        ),
    ] = "",
    pyramid_max: Annotated[
        Optional[int],
        typer.Option(
            help="Maximum rescaling (smaller pyramid, will be rounded to closer power of 2).",
            rich_help_panel="Python backend",
        ),
    ] = 32,
):
    """
    Create pyramidal versions of .ome.tiff images found in the input directory.

    If the QuPath backend is selected (recommended), the QuPath (console) executable
    has to be provided, or it will be looked for in the AppData\QuPath-xxx folders.
    Alternatively, a QUPATH_PATH file containing the full path to that exe can be
    created in the user directory.

    """
    # get QuPath and groovy script paths for QuPath backend
    if use_qupath:
        qupath_path = get_qupath_path(qupath_path)
        script_path = get_script_path(script_path)

    # check number of threads
    if not nthreads:
        nthreads = int(multiprocessing.cpu_count() / 2)

    # prepare output directory
    outputdir = os.path.join(inputdir, "pyramidal")
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)

    # get a list of images
    files = [
        filename for filename in os.listdir(inputdir) if filename.endswith("ome.tiff")
    ]

    # check we have files to process
    if len(files) == 0:
        print("Specified input directory is empty.")
        sys.exit()

    # loop over all files
    print(f"Found {len(files)} to pyramidalize...")

    pbar = tqdm(files)
    for imagename in pbar:
        # prepare image names
        image_path = os.path.join(inputdir, imagename)
        output_image = os.path.join(outputdir, imagename)

        # check if output file already exists
        if os.path.isfile(output_image):
            continue

        # verbose
        pbar.set_description(f"Pyramidalyzing {imagename}")

        if use_qupath:
            pyramidalize_qupath(
                image_path,
                output_image,
                qupath_path,
                script_path,
                tile_size,
                pyramid_factor,
                nthreads,
            )
        else:
            # prepare tiffwriter options
            tiffoptions = get_tiff_options("LZW", nthreads, tile_size)

            # number of pyramid levels
            levels = [
                pyramid_factor**i
                for i in range(1, int(math.log(pyramid_max, pyramid_factor)) + 1)
            ]
            pyramidalize_python(image_path, output_image, levels, tiffoptions)

    print("All done!")
