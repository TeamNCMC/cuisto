"""segmentation module, part of cuisto.

Functions for segmentating probability map stored as an image.

"""

import os
import uuid
from datetime import datetime
from pathlib import Path

import geojson
import numpy as np
import pandas as pd
import shapely
import tifffile
from skan import Skeleton, summarize
from skimage import measure, morphology
from tqdm import tqdm

pd.options.mode.copy_on_write = True  # prepare for pandas 3

def get_pixelsize(image_name: str) -> float:
    """
    Get pixel size recorded in `image_name` TIFF metadata.

    Parameters
    ----------
    image_name : str
        Full path to image.

    Returns
    -------
    pixelsize : float
        Pixel size in microns.

    """

    with tifffile.TiffFile(image_name) as tif:
        # XResolution is a tuple, numerator, denomitor. The inverse is the pixel size
        return (
            tif.pages[0].tags["XResolution"].value[1]
            / tif.pages[0].tags["XResolution"].value[0]
        )


def convert_to_pixels(filters, pixelsize):
    """
    Convert some values in `filters` in pixels.

    Parameters
    ----------
    filters : dict
        Must contain the keys used below.
    pixelsize : float
        Pixel size in microns.

    Returns
    -------
    filters : dict
        Same as input, with values in pixels.

    """

    filters["area_low"] = filters["area_low"] / pixelsize**2
    filters["area_high"] = filters["area_high"] / pixelsize**2
    filters["length_low"] = filters["length_low"] / pixelsize
    filters["dist_thresh"] = int(filters["dist_thresh"] / pixelsize)

    return filters


def pad_image(img: np.ndarray, finalsize: tuple | list) -> np.ndarray:
    """
    Pad image with zeroes to match expected final size.

    Parameters
    ----------
    img : ndarray
    finalsize : tuple or list
        nrows, ncolumns

    Returns
    -------
    imgpad : ndarray
        img with black borders.

    """

    final_h = finalsize[0]  # requested number of rows (height)
    final_w = finalsize[1]  # requested number of columns (width)
    original_h = img.shape[0]  # input number of rows
    original_w = img.shape[1]  # input number of columns

    a = (final_h - original_h) // 2  # vertical padding before
    aa = final_h - a - original_h  # vertical padding after
    b = (final_w - original_w) // 2  # horizontal padding before
    bb = final_w - b - original_w  # horizontal padding after

    return np.pad(img, pad_width=((a, aa), (b, bb)), mode="constant")


def erode_mask(mask: np.ndarray, edge_dist: float) -> np.ndarray:
    """
    Erode the mask outline so that it is `edge_dist` smaller from the border.

    This allows discarding the edges.

    Parameters
    ----------
    mask : ndarray
    edge_dist : float
        Distance to edges, in pixels.

    Returns
    -------
    eroded_mask : ndarray of bool

    """

    if edge_dist % 2 == 0:
        edge_dist += 1  # decomposition requires even number

    footprint = morphology.square(edge_dist, decomposition="sequence")

    return mask * morphology.binary_erosion(mask, footprint=footprint)


def get_image_skeleton(img: np.ndarray, minsize=0) -> np.ndarray:
    """
    Get the image skeleton.

    Computes the image skeleton and removes objects smaller than `minsize`.

    Parameters
    ----------
    img : ndarray of bool
    minsize : number, optional
        Min. size the object can have, as a number of pixels. Default is 0.

    Returns
    -------
    skel : ndarray of bool
        Binary image with 1-pixel wide skeleton.

    """

    skel = morphology.skeletonize(img)

    return morphology.remove_small_objects(skel, min_size=minsize, connectivity=2)


def get_collection_from_skel(
    skeleton: Skeleton, properties: dict, rescale_factor: float = 1.0, offset=0.5
) -> geojson.FeatureCollection:
    """
    Get the coordinates of each skeleton path as a GeoJSON Features in a
    FeatureCollection.
    `properties` is a dictionnary with QuPath properties of each detections.

    Parameters
    ----------
    skeleton : skan.Skeleton
    properties : dict
        QuPath objects' properties.
    rescale_factor : float
        Rescale output coordinates by this factor.
    offset : float
        Shift coordinates by this amount, typically to get pixel centers or edges.
        Default is 0.5.

    Returns
    -------
    collection : geojson.FeatureCollection
        A FeatureCollection ready to be written as geojson.

    """

    branch_data = summarize(skeleton, separator="_")

    collection = []
    for ind in range(skeleton.n_paths):
        prop = properties.copy()
        prop["measurements"] = {"skeleton_id": int(branch_data.loc[ind, "skeleton_id"])}
        collection.append(
            geojson.Feature(
                geometry=shapely.LineString(
                    (skeleton.path_coordinates(ind)[:, ::-1] + offset) * rescale_factor
                ),  # shape object
                properties=prop,  # object properties
                id=str(uuid.uuid4()),  # object uuid
            )
        )

    return geojson.FeatureCollection(collection)


def get_collection_from_poly(
    contours: list, properties: dict, rescale_factor: float = 1.0, offset: float = 0.5
) -> geojson.FeatureCollection:
    """
    Gather coordinates in the list and put them in GeoJSON format as Polygons.

    An entry in `contours` must define a closed polygon. `properties` is a dictionnary
    with QuPath properties of each detections.

    Parameters
    ----------
    contours : list
    properties : dict
        QuPatj objects' properties.
    rescale_factor : float
        Rescale output coordinates by this factor.
    offset : float
        Shift coordinates by this amount, typically to get pixel centers or edges.
        Default is 0.5.

    Returns
    -------
    collection : geojson.FeatureCollection
        A FeatureCollection ready to be written as geojson.

    """
    collection = [
        geojson.Feature(
            geometry=shapely.Polygon(
                np.fliplr((contour + offset) * rescale_factor)
            ),  # shape object
            properties=properties,  # object properties
            id=str(uuid.uuid4()),  # object uuid
        )
        for contour in contours
    ]

    return geojson.FeatureCollection(collection)


def get_collection_from_points(
    coords: list, properties: dict, rescale_factor: float = 1.0, offset: float = 0.5
) -> geojson.FeatureCollection:
    """
    Gather coordinates from `coords` and put them in GeoJSON format.

    An entry in `coords` are pairs of (x, y) coordinates defining the point.
    `properties` is a dictionnary with QuPath properties of each detections.

    Parameters
    ----------
    coords : list
    properties : dict
    rescale_factor : float
        Rescale output coordinates by this factor.

    Returns
    -------
    collection : geojson.FeatureCollection

    """

    collection = [
        geojson.Feature(
            geometry=shapely.Point(
                np.flip((coord + offset) * rescale_factor)
            ),  # shape object
            properties=properties,  # object properties
            id=str(uuid.uuid4()),  # object uuid
        )
        for coord in coords
    ]

    return geojson.FeatureCollection(collection)


def segment_lines(
    img: np.ndarray, geojson_props: dict, minsize=0.0, rescale_factor=1.0
) -> geojson.FeatureCollection:
    """
    Wraps skeleton analysis to get paths coordinates.

    Parameters
    ----------
    img : ndarray of bool
        Binary image to segment as lines.
    geojson_props : dict
        GeoJSON properties of objects.
    minsize : float
        Minimum size in pixels for an object.
    rescale_factor : float
        Rescale output coordinates by this factor.

    Returns
    -------
    collection : geojson.FeatureCollection
        A FeatureCollection ready to be written as geojson.

    """

    skel = get_image_skeleton(img, minsize=minsize)

    # get paths coordinates as FeatureCollection
    skeleton = Skeleton(skel, keep_images=False)
    return get_collection_from_skel(
        skeleton, geojson_props, rescale_factor=rescale_factor
    )


def segment_polygons(
    img: np.ndarray,
    geojson_props: dict,
    area_min: float = 0.0,
    area_max: float = np.inf,
    ecc_min: float = 0.0,
    ecc_max: float = 1.0,
    rescale_factor: float = 1.0,
) -> geojson.FeatureCollection:
    """
    Polygon segmentation.

    Parameters
    ----------
    img : ndarray of bool
        Binary image to segment as polygons.
    geojson_props : dict
        GeoJSON properties of objects.
    area_min, area_max : float
        Minimum and maximum area in pixels for an object.
    ecc_min, ecc_max : float
        Minimum and maximum eccentricity for an object.
    rescale_factor: float
        Rescale output coordinates by this factor.

    Returns
    -------
    collection : geojson.FeatureCollection
        A FeatureCollection ready to be written as geojson.

    """

    label_image = measure.label(img)

    # get objects properties
    stats = pd.DataFrame(
        measure.regionprops_table(
            label_image, properties=("label", "area", "eccentricity")
        )
    )

    # remove objects not matching filters
    toremove = stats[
        (stats["area"] < area_min)
        | (stats["area"] > area_max)
        | (stats["eccentricity"] < ecc_min)
        | (stats["eccentricity"] > ecc_max)
    ]

    label_image[np.isin(label_image, toremove["label"])] = 0

    # find objects countours
    label_image = label_image > 0
    contours = measure.find_contours(label_image)

    return get_collection_from_poly(
        contours, geojson_props, rescale_factor=rescale_factor
    )


def segment_points(
    img: np.ndarray,
    geojson_props: dict,
    area_min: float = 0.0,
    area_max: float = np.inf,
    ecc_min: float = 0,
    ecc_max: float = 1,
    dist_thresh: float = 0,
    rescale_factor: float = 1,
) -> geojson.FeatureCollection:
    """
    Point segmentation.

    First, segment polygons to apply shape filters, then extract their centroids,
    and remove isolated points as defined by `dist_thresh`.

    Parameters
    ----------
    img : ndarray of bool
        Binary image to segment as points.
    geojson_props : dict
        GeoJSON properties of objects.
    area_min, area_max : float
        Minimum and maximum area in pixels for an object.
    ecc_min, ecc_max : float
        Minimum and maximum eccentricity for an object.
    dist_thresh : float
        Maximal distance in pixels between objects before considering them as isolated and remove them.
        0 disables it.
    rescale_factor : float
        Rescale output coordinates by this factor.

    Returns
    -------
    collection : geojson.FeatureCollection
        A FeatureCollection ready to be written as geojson.

    """

    # get objects properties
    stats = pd.DataFrame(
        measure.regionprops_table(
            measure.label(img), properties=("label", "area", "eccentricity", "centroid")
        )
    )

    # keep objects matching filters
    stats = stats[
        (stats["area"] >= area_min)
        & (stats["area"] <= area_max)
        & (stats["eccentricity"] >= ecc_min)
        & (stats["eccentricity"] <= ecc_max)
    ]

    # create an image from centroids only
    stats["centroid-0"] = stats["centroid-0"].astype(int)
    stats["centroid-1"] = stats["centroid-1"].astype(int)
    bw = np.zeros(img.shape, dtype=bool)
    bw[stats["centroid-0"], stats["centroid-1"]] = True

    # filter isolated objects
    if dist_thresh:
        # dilation of points
        if dist_thresh % 2 == 0:
            dist_thresh += 1  # decomposition requires even number

        footprint = morphology.square(int(dist_thresh), decomposition="sequence")
        dilated = measure.label(morphology.binary_dilation(bw, footprint=footprint))
        stats = pd.DataFrame(
            measure.regionprops_table(dilated, properties=("label", "area"))
        )

        # objects that did not merge are alone
        toremove = stats[(stats["area"] <= dist_thresh**2)]
        dilated[np.isin(dilated, toremove["label"])] = 0  # remove them

        # apply mask
        bw = bw * dilated

    # get points coordinates
    coords = np.argwhere(bw)

    return get_collection_from_points(
        coords, geojson_props, rescale_factor=rescale_factor
    )


def get_seg_method(segtype: str):
    """
    Determine what kind of segmentation is performed.

    Segmentation kind are, for now, lines, polygons or points. We detect that based on
    hardcoded keywords.

    Parameters
    ----------
    segtype : str

    Returns
    -------
    seg_method : str

    """

    line_list = ["fibers", "axons", "fiber", "axon"]
    point_list = ["synapto", "synaptophysin", "syngfp", "boutons", "points"]
    polygon_list = ["cells", "polygon", "polygons", "polygon", "cell"]

    if segtype in line_list:
        seg_method = "lines"
    elif segtype in polygon_list:
        seg_method = "polygons"
    elif segtype in point_list:
        seg_method = "points"
    else:
        raise ValueError(
            f"Could not determine method to use based on segtype : {segtype}."
        )

    return seg_method


def get_geojson_dir(images_dir: str):
    """
    Get the directory of geojson files, which will be in the parent directory
    of `images_dir`.

    If the directory does not exist, create it.

    Parameters
    ----------
    images_dir : str

    Returns
    -------
    geojson_dir : str

    """

    geojson_dir = os.path.join(Path(images_dir).parent, "geojson")

    if not os.path.isdir(geojson_dir):
        os.mkdir(geojson_dir)

    return geojson_dir


def get_geojson_properties(name: str, color: tuple | list, objtype: str = "detection"):
    """
    Return geojson objects properties as a dictionnary, ready to be used in geojson.Feature.

    Parameters
    ----------
    name : str
        Classification name.
    color : tuple or list
        Classification color in RGB (3-elements vector).
    objtype : str, optional
        Object type ("detection" or "annotation"). Default is "detection".

    Returns
    -------
    props : dict

    """

    return {
        "objectType": objtype,
        "classification": {"name": name, "color": color},
        "isLocked": "true",
    }


def parameters_as_dict(
    images_dir: str,
    masks_dir: str,
    segtype: str,
    name: str,
    proba_threshold: float,
    edge_dist: float,
):
    """
    Get information as a dictionnary.

    Parameters
    ----------
    images_dir : str
        Path to images to be segmented.
    masks_dir : str
        Path to images masks.
    segtype : str
        Segmentation type (eg. "fibers").
    name : str
        Name of the segmentation (eg. "green").
    proba_threshold : float < 1
        Probability threshold.
    edge_dist : float
        Distance in µm to the brain edge that is ignored.

    Returns
    -------
    params : dict

    """

    return {
        "images_location": images_dir,
        "masks_location": masks_dir,
        "type": segtype,
        "probability threshold": proba_threshold,
        "name": name,
        "edge distance": edge_dist,
    }


def write_parameters(
    outfile: str, parameters: dict, filters: dict, original_pixelsize: float
):
    """
    Write parameters to `outfile`.

    A timestamp will be added. Parameters are written as key = value,
    and a [filters] is added before filters parameters.

    Parameters
    ----------
    outfile : str
        Full path to the output file.
    parameters : dict
        General parameters.
    filters : dict
        Filters parameters.
    original_pixelsize : float
        Size of pixels in original image.

    """

    with open(outfile, "w") as fid:
        fid.writelines(f"date = {datetime.now().strftime('%d-%B-%Y %H:%M:%S')}\n")

        fid.writelines(f"original_pixelsize = {original_pixelsize}\n")

        for key, value in parameters.items():
            fid.writelines(f"{key} = {value}\n")

        fid.writelines("[filters]\n")

        for key, value in filters.items():
            fid.writelines(f"{key} = {value}\n")


def process_directory(
    images_dir: str,
    img_suffix: str = "",
    segtype: str = "",
    original_pixelsize: float = 1.0,
    target_channel: int = 0,
    proba_threshold: float = 0.0,
    max_pixel_value: float = 255,
    qupath_class: str = "Object",
    qupath_color: list = [0, 0, 0],
    qupath_type: str = "detection",
    channel_suffix: str = "",
    edge_dist: float = 0.0,
    filters: dict = {},
    masks_dir: str = "",
    masks_ext: str = "",
):
    """
    Segment the .ome.tiff files in the input directory.

    Parameters
    ----------
    images_dir : str
        Animal ID to process.
    img_suffix : str
        Images suffix, including extension.
    segtype : str
        Segmentation type.
    original_pixelsize : float
        Original images pixel size in microns.
    target_channel : int
        Index of the channel containning the objects of interest (eg. not the
        background), in the probability map (*not* the original images channels).
    proba_threshold : float < 1
        Probability below this value will be discarded (multiplied by `max_pixel_value`)
    max_pixel_value : float
        Maximum pixel value in the segmented image, to rescale them to a probability
        between 0 and 1.
    qupath_class : str
        Name of the QuPath classification.
    qupath_color : list of three elements
        Color associated to that classification in RGB.
    qupath_type : {"detection", "annotation"}
        QuPath type of object.
    channel_suffix : str
        Channel name, will be used as a suffix in output geojson files.
    edge_dist : float
        Distance to the edge of the brain masks that will be ignored, in microns. Set to
        0 to disable this feature.
    filters : dict
        Filters values to include or excludes objects. See the top of the script.
    masks_dir : str, optional
        Path to images masks, to exclude objects found near the edges. The masks must be
        with the same name as the corresponding image to be segmented, without its
        suffix. Default is "", which disables this feature.
    masks_ext : str, optional
        Masks files extension, without leading ".". Default is ""

    """

    # -- Preparation
    # get segmentation type
    seg_method = get_seg_method(segtype)

    # get output directory path
    geojson_dir = get_geojson_dir(images_dir)

    # get images list
    images_list = [
        os.path.join(images_dir, filename)
        for filename in os.listdir(images_dir)
        if filename.endswith(img_suffix)
    ]

    if len(images_list) == 0:
        raise FileNotFoundError(
            f"No file found in {images_dir}. Check 'IMAGES_DIR' and 'IMG_SUFFIX'."
        )

    # write parameters
    parameters = parameters_as_dict(
        images_dir, masks_dir, segtype, channel_suffix, proba_threshold, edge_dist
    )
    param_file = os.path.join(geojson_dir, "parameters" + channel_suffix + ".txt")
    if os.path.isfile(param_file):
        raise FileExistsError("Parameters file already exists.")
    else:
        write_parameters(param_file, parameters, filters, original_pixelsize)

    # convert parameters to pixels in probability map
    pixelsize = get_pixelsize(images_list[0])  # get pixel size
    edge_dist = int(edge_dist / pixelsize)
    filters = convert_to_pixels(filters, pixelsize)

    # get rescaling factor
    rescale_factor = pixelsize / original_pixelsize

    # get GeoJSON properties
    geojson_props = get_geojson_properties(
        qupath_class, qupath_color, objtype=qupath_type
    )

    # -- Processing
    pbar = tqdm(images_list)
    for imgpath in pbar:
        # build file names
        imgname = os.path.basename(imgpath)
        geoname = imgname.replace(img_suffix, "")
        geojson_file = os.path.join(
            geojson_dir, geoname + "_segmentation" + channel_suffix + ".geojson"
        )

        # checks if output file already exists
        if os.path.isfile(geojson_file):
            continue

        # read images
        pbar.set_description(f"{geoname}: Loading...")
        img = tifffile.imread(imgpath, key=target_channel)
        if (edge_dist > 0) & (len(masks_dir) != 0):
            mask = tifffile.imread(os.path.join(masks_dir, geoname + "." + masks_ext))
            mask = pad_image(mask, img.shape)  # resize mask
            # apply mask, eroding from the edges
            img = img * erode_mask(mask, edge_dist)

        # image processing
        pbar.set_description(f"{geoname}: IP...")

        # threshold probability and binarization
        img = img >= proba_threshold * max_pixel_value

        # segmentation
        pbar.set_description(f"{geoname}: Segmenting...")

        if seg_method == "lines":
            collection = segment_lines(
                img,
                geojson_props,
                minsize=filters["length_low"],
                rescale_factor=rescale_factor,
            )

        elif seg_method == "polygons":
            collection = segment_polygons(
                img,
                geojson_props,
                area_min=filters["area_low"],
                area_max=filters["area_high"],
                ecc_min=filters["ecc_low"],
                ecc_max=filters["ecc_high"],
                rescale_factor=rescale_factor,
            )

        elif seg_method == "points":
            collection = segment_points(
                img,
                geojson_props,
                area_min=filters["area_low"],
                area_max=filters["area_high"],
                ecc_min=filters["ecc_low"],
                ecc_max=filters["ecc_high"],
                dist_thresh=filters["dist_thresh"],
                rescale_factor=rescale_factor,
            )
        else:
            # we already printed an error message
            return

        # save geojson
        pbar.set_description(f"{geoname}: Saving...")
        with open(geojson_file, "w") as fid:
            fid.write(geojson.dumps(collection))
